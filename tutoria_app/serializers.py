from rest_framework import serializers
from .models import TutorSchedule 

class TutorScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TutorSchedule
        fields = '__all__'

    def create(self, validated_data):
        instance = TutorSchedule(**validated_data)
        instance.clean()  # Manually trigger validation logic
        instance.save()
        return instance

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.clean()  # Trigger validation
        instance.save()
        return instance
