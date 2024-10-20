from django.core.mail import send_mail
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from exit_emp import settings
from .models import Task,EmployeeTask,Employee,Department

def notify_hods_of_new_employee(employee):

    departments = Department.objects.all()
    for department in departments:
        hod = department.hod
        if hod and hod.email:
            send_mail(
                subject='New Employee Created',
                message=f'A new employee named {employee.name} has applied for approval.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[hod.email],
                fail_silently=False,
            )



def notify_hr_of_completion(employee):
    hrs = Employee.objects.filter(role='HR')

    for hr in hrs:
        if hr and hr.user.email:
            send_mail(
                subject='Employee Tasks Completed',
                message=f'All tasks for employee {employee.name} have been completed.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[hr.email],
                fail_silently=False,
            )


