from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Employee,EmployeeTask,Department,FeedbackQuestions,FeedbackAnswers,Task


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):

        data = super().validate(attrs)

        user = self.user
        role = user.employee.role if hasattr(user, 'employee') else None

        data['role'] = role

        return data

class EmployeeSerializer(serializers.ModelSerializer):
    total_tasks = serializers.IntegerField(read_only=True)
    progress = serializers.FloatField(read_only=True)
    name = serializers.CharField(source='user.username', read_only=True,allow_null=True)
    department_name=serializers.CharField(source='department.name')

    class Meta:
        model = Employee
        fields = ['id', 'name', 'total_tasks', 'progress','role','department_name']



class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model=Task
        fields='__all__'



class EmployeeTaskSerializer(serializers.ModelSerializer):
    task_name=serializers.CharField(source='task.name',read_only=True)
    emp_name=serializers.CharField(source='employee.name')

    class Meta:
        model=EmployeeTask
        fields = ['id','emp_name','status','task_name']

    def get_department_hod(self, obj):
        if obj.task.departments.hod:
            return f"{obj.task.departments.hod.first_name} {obj.task.departments.hod.last_name}"
        return "No HoD assigned"


class EmployeeTaskSerializerN(serializers.ModelSerializer):
    task_name=serializers.CharField(source='task.name',read_only=True)
    department_name=serializers.CharField(source='task.departments.name',read_only=True)
    department_hod=serializers.SerializerMethodField()

    class Meta:
        model=EmployeeTask
        fields = ['id','status','task_name','department_name','department_hod']

    def get_department_hod(self, obj):
        department = getattr(obj.task, 'departments', None)
        if department and department.hod:
            return f"{department.hod.first_name} {department.hod.last_name}"
        return "No HoD assigned"


class FeedbackQuestionsSerializer(serializers.ModelSerializer):
    class Meta:
        model=FeedbackQuestions
        fields='__all__'


class FeedbackAnswersSerializer(serializers.ModelSerializer):
    class Meta:
        model=FeedbackAnswers
        fields='__all__'