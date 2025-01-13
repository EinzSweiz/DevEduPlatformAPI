from django.db import models
from useraccounts.models import User
from datetime import timezone

class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=100)
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='instructed_courses')
    created_at =  models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title
    
class Video(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='videos')
    title = models.CharField(max_length=255)
    description = models.TextField()
    video_url = models.URLField()
    duration = models.DurationField()
    order = models.PositiveIntegerField()
    is_preview = models.BooleanField(default=False)
    uplodated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['order']


class CoursesProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_progress')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='progress')
    current_video = models.ForeignKey(Video, on_delete=models.SET_NULL, null=True, blank=True)
    completed_videos = models.ManyToManyField(Video, related_name='completed_by_users')
    progress_percentage = models.FloatField(default=0.0)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def update_progress(self):
        total_videos = self.course.videos.count()
        if total_videos > 0:
            completed_count = self.completed_videos.count()
            self.progress_percentage = (completed_count / total_videos) * 100
            if self.progress_percentage == 100:
                self.completed_at = timezone.now()
        self.save()

    def __str__(self):
        return f"{self.user.username} - {self.course.title} Progress"
