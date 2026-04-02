from django.db import models

# Create your models here.
class ImageUpload(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
    ]
    input_image = models.ImageField(upload_to='uploads/')
    output_image = models.ImageField(upload_to='outputs/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)