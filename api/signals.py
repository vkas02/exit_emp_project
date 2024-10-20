from .models import Employee,EmployeeTask,Task,Department
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save,sender=Employee)
def assign_task_to_employee(sender,instance,created,**kwargs):
    if created:
        tasks=Task.objects.all()
        for task in tasks:
            EmployeeTask.objects.create(employee=instance,task=task)



