from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import ImageUpload
from PIL import Image
import io
from django.core.files.uploadedfile import SimpleUploadedFile


def create_test_image():
    file = io.BytesIO()
    image = Image.new("RGB", (100, 100), color="red")
    image.save(file, "JPEG")
    file.seek(0)

    return SimpleUploadedFile(
        "test.jpg",
        file.read(),
        content_type="image/jpeg"
    )

class BackgroundRemovalTests(APITestCase):

    def setUp(self):
        self.upload_url = "/api/remove-bg/"
        self.status_url = "/api/status/{}/"

        self.image = create_test_image()

    def test_upload_image(self):
        response = self.client.post(
            self.upload_url,
            {"image": self.image},
            format="multipart"
        )

        print(response.data)  # DEBUG

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertIn("id", response.data)

    def test_status_endpoint(self):
        obj = ImageUpload.objects.create(
            input_image=create_test_image(),
            status="pending"
        )

        response = self.client.get(self.status_url.format(obj.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "pending")

    def test_invalid_upload(self):
        response = self.client.post(
            self.upload_url,
            {"image": "not_a_file"},
            format="multipart"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_complete_flow(self):
        response = self.client.post(
            self.upload_url,
            {"image": create_test_image()},
            format="multipart"
        )

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        image_id = response.data["id"]

        obj = ImageUpload.objects.get(id=image_id)
        obj.status = "completed"
        obj.output_image = obj.input_image
        obj.save()

        status_response = self.client.get(self.status_url.format(image_id))

        self.assertEqual(status_response.status_code, status.HTTP_200_OK)
        self.assertEqual(status_response.data["status"], "completed")