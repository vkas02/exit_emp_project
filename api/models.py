from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Department(models.Model):
    name = models.CharField(max_length=200)
    hod = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name



class Employee(models.Model):
    Role_Choices = [
        ('Employee', 'Employee'),
        ('HR', 'HR'),
        ('HoD', 'HoD'),
    ]
    user=models.OneToOneField(User,on_delete=models.CASCADE, related_name='employee')
    name=models.CharField(max_length=100)
    department=models.ForeignKey(Department,on_delete=models.CASCADE)
    role=models.CharField(max_length=200,choices=Role_Choices)


    def __str__(self):
        return self.name


class Task(models.Model):
    name=models.CharField(max_length=200)
    departments=models.ForeignKey(Department,on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class EmployeeTask(models.Model):
    status_choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('na', 'NA'),
    ]
    employee=models.ForeignKey(Employee,on_delete=models.CASCADE,related_name='tasks')
    task=models.ForeignKey(Task,on_delete=models.CASCADE,related_name='employee_tasks')
    status= models.CharField(max_length=10,choices=status_choices,default='pending')

    def __str__(self):
        return f'{self.employee}-{self.task}'


class FeedbackQuestions(models.Model):
    question_text=models.CharField(max_length=200)
    choice=models.JSONField()

    def __str__(self):
        return self.question_text


class FeedbackAnswers(models.Model):
    employee=models.ForeignKey(Employee,on_delete=models.CASCADE)
    question= models.ForeignKey(FeedbackQuestions,on_delete=models.CASCADE)
    selected_choice=models.CharField(max_length=200)

    def __str__(self):
        return f'{self.employee}-{self.question}'


