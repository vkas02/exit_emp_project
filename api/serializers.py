from rest_framework import serializers
from .models import Employee,EmployeeTask,Department,FeedbackQuestions,FeedbackAnswers,Task
from django.contrib.auth.models import User



class EmployeeSerializer(serializers.ModelSerializer):
    total_tasks = serializers.IntegerField()
    approved_tasks = serializers.IntegerField()
    progress = serializers.FloatField()
    class Meta:
        model= Employee
        exclude = ['user']
        depth = 1


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model=Task
        fields='__all__'



class EmployeeTaskSerializer(serializers.ModelSerializer):
    task_name=serializers.CharField(source='task.name',read_only=True)
    department_name=serializers.CharField(source='task.departments.name',read_only=True)
    department_hod=serializers.CharField(source='task.departments.hod.first_name',read_only=True)
    class Meta:
        model=EmployeeTask
        fields = ['id','status','task_name','department_name','department_hod']


class FeedbackQuestionsSerializer(serializers.ModelSerializer):
    class Meta:
        model=FeedbackQuestions
        fields='__all__'


class FeedbackAnswersSerializer(serializers.ModelSerializer):
    class Meta:
        model=FeedbackAnswers
        fields='__all__'