import uuid
from django.db import models

class Resume(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    user_id = models.CharField(max_length=36)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['user_id'])]

    def __str__(self):
        return f"{self.name} ({self.id})"

class ResumeVersion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    resume = models.ForeignKey(Resume, related_name='versions', on_delete=models.CASCADE)
    file_path = models.CharField(max_length=512)
    file_name = models.CharField(max_length=255)
    file_size = models.IntegerField()
    file_type = models.CharField(max_length=50)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['resume'])]

    def __str__(self):
        return f"Version {self.id} of {self.resume.name}"

    @property
    def s3_key(self):
        return f"resumes/{self.resume.user_id}/{self.resume.id}/{self.id}/{self.file_name}"
