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
    department_hod=serializers.SerializerMethodField()
    employee_name=serializers.CharField(source='employee.name',read_only=True)
    class Meta:
        model=EmployeeTask
        fields = ['id','employee_name','status','task_name',]

    def get_department_hod(self, obj):
        if obj.task.departments.hod:
            return f"{obj.task.departments.hod.first_name} {obj.task.departments.hod.last_name}"
        return "No HoD assigned"


class FeedbackQuestionsSerializer(serializers.ModelSerializer):
    class Meta:
        model=FeedbackQuestions
        fields='__all__'


class FeedbackAnswersSerializer(serializers.ModelSerializer):
    class Meta:
        model=FeedbackAnswers
        fields='__all__'