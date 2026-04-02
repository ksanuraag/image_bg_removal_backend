from django.urls import path
from .views import RemoveBGView,ImageStatusView

urlpatterns = [
    path('remove-bg/', RemoveBGView.as_view()),
    path("status/<int:pk>/", ImageStatusView.as_view(), name="image-status"),
]