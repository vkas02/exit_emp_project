from rest_framework import serializers
from .models import Employee,EmployeeTask,Department,FeedbackQuestions,FeedbackAnswers
from django.contrib.auth.models import User



class EmployeeSerializer(serializers.ModelSerializer):
    total_tasks = serializers.IntegerField()
    approved_tasks = serializers.IntegerField()
    progress = serializers.FloatField()
    class Meta:
        model= Employee
        exclude = ['user']
        depth = 1


class EmployeeTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model=EmployeeTask
        fields='__all__'


class FeedbackQuestionsSerializer(serializers.ModelSerializer):
    class Meta:
        model=FeedbackQuestions
        fields='__all__'


class FeedbackAnswersSerializer(serializers.ModelSerializer):
    class Meta:
        model=FeedbackAnswers
        fields='__all__'