from django.db import models

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Certification(models.Model):
    name = models.CharField(max_length=200)
    provider = models.CharField(max_length=100)
    required_skills = models.ManyToManyField(Skill, related_name='certifications')
    level = models.CharField(max_length=50)  # e.g., 'Beginner', 'Intermediate', 'Advanced'
    description = models.TextField()
    url = models.URLField(blank=True)

    def __str__(self):
        return f"{self.name} by {self.provider}"

class JobRole(models.Model):
    title = models.CharField(max_length=100)
    required_skills = models.ManyToManyField(Skill, related_name='job_roles')
    description = models.TextField()

    def __str__(self):
        return self.title

class UserProfile(models.Model):
    name = models.CharField(max_length=100)
    resume_text = models.TextField(blank=True)
    current_skills = models.ManyToManyField(Skill, related_name='users_with_skill')
    target_job_role = models.ForeignKey(JobRole, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return self.name