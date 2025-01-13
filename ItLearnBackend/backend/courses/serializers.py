from rest_framework import serializers
from .models import Course, Video
from useraccounts.serializers import UserModelDynamicSerializer

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['id', 'title', 'description', 'video_url', 'duration', 'order', 'is_preview']

class CourseDynamicSerializer(serializers.ModelSerializer):
    instructor = UserModelDynamicSerializer(fields=['id', 'email', 'name',], read_only=True)
    videos = VideoSerializer(many=True, read_only=True)
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    class Meta:
        model = Course
        fields = '__all__'