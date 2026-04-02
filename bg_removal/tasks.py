import logging
import os
from io import BytesIO

from celery import shared_task
from django.core.files.base import ContentFile
from PIL import Image
from rembg import remove

from .models import ImageUpload

logger = logging.getLogger(__name__)


@shared_task(
    name="remover.process_image",
    bind=True,
    max_retries=2,
    default_retry_delay=10,
    ignore_result=True,
)
def process_image(self, image_id: int) -> None:
    """
    Remove the background from an uploaded image and save the result.
    Marks the record as 'failed' instead of crashing if anything goes wrong,
    so the API always returns a meaningful status.
    """
    try:
        obj = ImageUpload.objects.get(pk=image_id)
    except ImageUpload.DoesNotExist:
        logger.error("ImageUpload %s not found.", image_id)
        return

    obj.status = "processing"
    obj.save(update_fields=["status"])

    try:
        # Open input from storage (works with S3, local, etc.)
        obj.input_image.open("rb")
        input_bytes = obj.input_image.read()
        obj.input_image.close()

        input_image = Image.open(BytesIO(input_bytes)).convert("RGBA")

        # rembg works on bytes — faster than passing PIL images
        output_bytes = remove(input_bytes)

        # Build output filename: same stem, always PNG (transparency)
        original_name = os.path.basename(obj.input_image.name)
        stem = os.path.splitext(original_name)[0]
        output_name = f"bg_removed_{stem}.png"

        output_file = ContentFile(output_bytes, name=output_name)
        obj.output_image.save(output_name, output_file, save=False)
        obj.status = "completed"
        obj.save(update_fields=["output_image", "status"])

        logger.info("Background removal complete for ImageUpload %s", image_id)

    except Exception as exc:
        logger.error(
            "Background removal failed for ImageUpload %s: %s",
            image_id, exc, exc_info=True,
        )
        # Retry up to max_retries before marking failed
        try:
            raise self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            obj.status = "failed"
            obj.save(update_fields=["status"])