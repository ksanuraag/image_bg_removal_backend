# import os
# from celery import Celery
# from kombu import Queue

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

# app = Celery("project")
# app.config_from_object("django.conf:settings", namespace="CELERY")
# app.autodiscover_tasks()

# app.conf.task_queues = (
#     Queue("default", priority=5),
#     Queue("bg_removal", priority=8),    # dedicated queue for image tasks
# )

# app.conf.task_routes = {
#     "remover.process_image": {"queue": "bg_removal"},
# }

# app.conf.update(
#     task_acks_late=True,
#     task_reject_on_worker_lost=True,
#     task_ignore_result=True,
#     worker_max_tasks_per_child=500,     # recycle worker to free rembg model memory
#     worker_max_memory_per_child=512000, # 512 MB — rembg model is large
#     broker_connection_retry_on_startup=True,
#     worker_pool="solo", 
# )
import os
from celery import Celery
from kombu import Queue

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

app = Celery("project")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.task_queues = (
    Queue("default", priority=5),
    Queue("bg_removal", priority=8),
)

app.conf.task_routes = {
    "remover.process_image": {"queue": "bg_removal"},
}

app.conf.update(
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_ignore_result=True,
    worker_max_tasks_per_child=200,
    worker_max_memory_per_child=300000,  # 300 MB — rembg u2netp is much lighter
    broker_connection_retry_on_startup=True,
    worker_concurrency=1,
)