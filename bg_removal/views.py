import logging

from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from rest_framework import status
from rest_framework.generics import RetrieveAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .models import ImageUpload
from .serializers import ImageUploadSerializer, ImageUploadCreateSerializer
from .tasks import process_image

logger = logging.getLogger(__name__)


class RemoveBGView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Upload image for background removal",
        description=(
            "Accepts a JPEG, PNG, or WebP image (max 10 MB). "
            "Background removal runs asynchronously via Celery. "
            "Use the returned `id` to poll `/api/status/{id}/` for completion.."
        ),
        request=ImageUploadCreateSerializer,
        responses={
            202: OpenApiResponse(
                description="Processing started",
                examples=[
                    OpenApiExample(
                        "Accepted",
                        value={
                            "id": 42,
                            "status": "pending",
                            "message": "Processing started. Poll /api/status/42/ for updates.",
                        },
                    )
                ],
            ),
            400: OpenApiResponse(description="Validation error (bad file type, too large, etc.)"),
        },
        tags=["Background Removal"],
    )
    def post(self, request):
        serializer = ImageUploadCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        file = serializer.validated_data["image"]
        obj = ImageUpload.objects.create(input_image=file, status="pending")
        process_image.delay(obj.pk)
        logger.info("Queued background removal for ImageUpload %s", obj.pk)

        return Response(
            {
                "id": obj.pk,
                "status": obj.status,
                "message": f"Processing started. Poll /api/status/{obj.pk}/ for updates.",
            },
            status=status.HTTP_202_ACCEPTED,
        )


class ImageStatusView(RetrieveAPIView):
    queryset = ImageUpload.objects.all()
    serializer_class = ImageUploadSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Check processing status",
        description=(
            "Returns the current status of a background removal job. "
            "`status` is one of: `pending`, `processing`, `completed`, `failed`. "
            "When `completed`, `output_image` contains the URL of the processed PNG."
        ),
        responses={
            200: ImageUploadSerializer,
            404: OpenApiResponse(description="Job not found"),
        },
        tags=["Background Removal"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)