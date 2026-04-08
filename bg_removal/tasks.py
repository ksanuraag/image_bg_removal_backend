# import logging
# import os
# from io import BytesIO

# from celery import shared_task
# from celery.signals import worker_process_init
# from django.core.files.base import ContentFile
# from PIL import Image
# from transparent_background import Remover

# from .models import ImageUpload

# logger = logging.getLogger(__name__)

# _remover = None  # per-worker singleton


# @worker_process_init.connect
# def init_remover(**kwargs):
#     """Called once per Celery worker process after fork — safe for CUDA/torch."""
#     global _remover

#     _remover = Remover(mode="base")
#     logger.info("Remover model loaded in worker process (PID %s)", os.getpid())


# @shared_task(
#     name="remover.process_image",
#     bind=True,
#     max_retries=2,
#     default_retry_delay=10,
#     ignore_result=True,
# )
# def process_image(self, image_id: int) -> None:
#     global _remover

#     # Fallback: if somehow called without worker_process_init (e.g. eager mode)
#     if _remover is None:
#         _remover = Remover(mode="fast")

#     try:
#         obj = ImageUpload.objects.get(pk=image_id)
#     except ImageUpload.DoesNotExist:
#         logger.error("ImageUpload %s not found.", image_id)
#         return

#     obj.status = "processing"
#     obj.save(update_fields=["status"])

#     try:
#         obj.input_image.open("rb")
#         input_bytes = obj.input_image.read()
#         obj.input_image.close()

#         img = Image.open(BytesIO(input_bytes)).convert("RGB")
#         max_size = 1024
#         if max(img.size) > max_size:
#             img.thumbnail((max_size, max_size), Image.LANCZOS)
#         output_img = _remover.process(img, type="rgba")

#         buf = BytesIO()
#         output_img.save(buf, format="PNG")
#         output_bytes = buf.getvalue()

#         original_name = os.path.basename(obj.input_image.name)
#         stem = os.path.splitext(original_name)[0]
#         output_name = f"bg_removed_{stem}.png"

#         obj.output_image.save(output_name, ContentFile(output_bytes, name=output_name), save=False)
#         obj.status = "completed"
#         obj.save(update_fields=["output_image", "status"])

#         logger.info("Background removal complete for ImageUpload %s", image_id)

#     except Exception as exc:
#         logger.error("Background removal failed for ImageUpload %s: %s", image_id, exc, exc_info=True)
#         try:
#             raise self.retry(exc=exc)
#         except self.MaxRetriesExceededError:
#             obj.status = "failed"
#             obj.save(update_fields=["status"])
import logging
import os
from io import BytesIO

from celery import shared_task
from django.core.files.base import ContentFile
from PIL import Image
from rembg import remove, new_session

from .models import ImageUpload

logger = logging.getLogger(__name__)

# u2netp is ~5 MB vs u2net's 170 MB — perfect for t2.small
_session = None

def get_session():
    global _session
    if _session is None:
        _session = new_session("u2netp")
        logger.info("rembg session created (PID %s)", os.getpid())
    return _session


@shared_task(
    name="remover.process_image",
    bind=True,
    max_retries=2,
    default_retry_delay=10,
    ignore_result=True,
)
def process_image(self, image_id: int) -> None:
    try:
        obj = ImageUpload.objects.get(pk=image_id)
    except ImageUpload.DoesNotExist:
        logger.error("ImageUpload %s not found.", image_id)
        return

    obj.status = "processing"
    obj.save(update_fields=["status"])

    try:
        obj.input_image.open("rb")
        input_bytes = obj.input_image.read()
        obj.input_image.close()

        img = Image.open(BytesIO(input_bytes)).convert("RGB")

        # Downscale to save RAM — u2netp works well at 512px
        max_size = 512
        if max(img.size) > max_size:
            img.thumbnail((max_size, max_size), Image.LANCZOS)

        # rembg works on raw bytes — convert PIL → bytes → rembg → PIL
        buf_in = BytesIO()
        img.save(buf_in, format="PNG")
        buf_in.seek(0)

        output_bytes = remove(buf_in.getvalue(), session=get_session())

        original_name = os.path.basename(obj.input_image.name)
        stem = os.path.splitext(original_name)[0]
        output_name = f"bg_removed_{stem}.png"

        obj.output_image.save(
            output_name,
            ContentFile(output_bytes, name=output_name),
            save=False,
        )
        obj.status = "completed"
        obj.save(update_fields=["output_image", "status"])
        logger.info("Background removal complete for ImageUpload %s", image_id)

    except Exception as exc:
        logger.error(
            "Background removal failed for ImageUpload %s: %s",
            image_id, exc, exc_info=True,
        )
        try:
            raise self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            obj.status = "failed"
            obj.save(update_fields=["status"])