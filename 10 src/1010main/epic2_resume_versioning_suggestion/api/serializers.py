from rest_framework import serializers
from .models import Resume, ResumeVersion

class ResumeVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResumeVersion
        fields = '__all__'

class ResumeSerializer(serializers.ModelSerializer):
    versions = ResumeVersionSerializer(many=True, read_only=True)

    class Meta:
        model = Resume
        fields = ['id', 'name', 'user_id', 'created_at', 'updated_at', 'versions']
