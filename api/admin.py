from django.contrib import admin
from django.contrib.admin import ModelAdmin

from .models import Employee, Task, Department, EmployeeTask, FeedbackAnswers, FeedbackQuestions


# Register your models here.

class EmployeeAdmin(ModelAdmin):
    list_display = ['name','department','role']


class TaskAdmin(ModelAdmin):
    list_display = ['name','departments']


class DepartmentAdmin(ModelAdmin):
    list_display = ['name','hod']


admin.site.register(Employee,EmployeeAdmin)
admin.site.register(Task,TaskAdmin)
admin.site.register(Department,DepartmentAdmin)
admin.site.register(EmployeeTask)
admin.site.register(FeedbackAnswers)
admin.site.register(FeedbackQuestions)


