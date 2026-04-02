from rest_framework import serializers
from .models import ImageUpload

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_SIZE_MB = 10


class ImageUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageUpload
        fields = ["id", "input_image", "output_image", "status", "created_at"]
        read_only_fields = ["output_image", "status", "created_at"]


class ImageUploadCreateSerializer(serializers.Serializer):
    image = serializers.ImageField(
        help_text=f"JPEG, PNG, or WebP image. Maximum size: {MAX_SIZE_MB} MB."
    )

    def validate_image(self, value):
        if value.content_type not in ALLOWED_MIME_TYPES:
            raise serializers.ValidationError(
                f"Unsupported file type '{value.content_type}'. "
                f"Allowed: {', '.join(ALLOWED_MIME_TYPES)}."
            )
        if value.size > MAX_SIZE_MB * 1024 * 1024:
            raise serializers.ValidationError(
                f"File too large. Maximum size is {MAX_SIZE_MB} MB."
            )
        return value