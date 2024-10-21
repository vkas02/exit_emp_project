from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect
import pandas as pd
from django.views.decorators.csrf import csrf_exempt
from  rest_framework import  generics
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework import status
from .models import Employee, EmployeeTask, FeedbackQuestions, FeedbackAnswers, Department
from .serializers import EmployeeSerializer,FeedbackQuestionsSerializer,EmployeeTaskSerializer
from .utlis import notify_hr_of_completion
from rest_framework.decorators import permission_classes, api_view
from django.db.models import Q, Count, Case, When, F


# Create your views here.
def index(request):
    return HttpResponse('Index page')


class IsEmployee(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'employee') and request.user.employee.role == 'Employee'


class IsHR(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'employee') and request.user.employee.role == 'HR'

class IsHoD(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'employee') and request.user.employee.role == 'HoD'



def logout_user(request):
    logout(request)
    return redirect('login')



@csrf_exempt
@api_view(['GET'])
def dashboard(request):
    user = request.user

    role = user.employee.role
    if role == 'Employee':
        return handle_employee_role(request, user)
    elif role == 'HR':
        return handle_hr_role(request)
    elif role == 'HoD':
        return handle_hod_role(request, user)


@permission_classes([IsEmployee])
def handle_employee_role(request, user):
    try:
        employee = Employee.objects.get(user=user)
        tasks = EmployeeTask.objects.filter(employee=employee)
        all_task_completed = not EmployeeTask.objects.filter(employee=employee, status='rejected').exists()
        if all_task_completed:
            notify_hr_of_completion(employee)

        if request.method == 'POST':
            return handle_feedback_submission(request, employee)

        return get_employee_response(tasks)
    except Employee.DoesNotExist:
        return Response({'error': 'No employee found'}, status=status.HTTP_404_NOT_FOUND)


@csrf_exempt
@api_view(['GET','POST'])
@permission_classes([IsEmployee])
def handle_feedback_submission(request, employee):
    feedback_questions = FeedbackQuestions.objects.all()
    for question in feedback_questions:
        selected_choice = request.data.get(f'question_{question.id}')
        if selected_choice:
            FeedbackAnswers.objects.update_or_create(
                employee=employee,
                question=question,
                defaults={'selected_choice': selected_choice}
            )
    return Response({'message': 'Feedback submitted successfully.'}, status=status.HTTP_200_OK)

@permission_classes([IsEmployee])
def get_employee_response(tasks):
    tasks_data = EmployeeTaskSerializer(tasks, many=True).data
    feedback_questions = FeedbackQuestions.objects.all()
    feedback_questions_data = FeedbackQuestionsSerializer(feedback_questions, many=True).data
    response_data = {
        'tasks': tasks_data,
        'feedback_questions': feedback_questions_data
    }
    return Response(response_data, status=status.HTTP_200_OK)

@csrf_exempt
@permission_classes([IsHoD])
def handle_hod_role(request,user):
    try:
        employee=Employee.objects.get(user=user)
        department=employee.department
        pending_tasks=EmployeeTask.objects.filter(
            Q(status='pending') | Q(status='na'),
            task__departments=department
        )
        if request.method=='POST':
            return update_task_status(request)

        grouped_tasks_serialized=group_tasks_by_employee(pending_tasks)
        return Response({'grouped_tasks':grouped_tasks_serialized},status=status.HTTP_200_OK)
    except Employee.DoesNotExist:
        return Response({'error':'Invalid credentials'},status=status.HTTP_404_NOT_FOUND)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsHoD])
def update_task_status(request):
    employee_task_id=request.data.get('employee_task_id')
    action=request.data.get('action')

    try:
        employee_task = EmployeeTask.objects.get(id=employee_task_id)
        if action == 'approve':
            employee_task.status = 'approved'
        elif action == 'reject':
            employee_task.status = 'rejected'
        elif action == 'NA':
            employee_task.status = 'na'
        else:
            employee_task.status = 'pending'

        employee_task.save()
        return Response({'message':'Task updated successfully'},status=status.HTTP_200_OK)
    except EmployeeTask.DoesNotExist:
        return Response({'error':'Task not Found'},status=status.HTTP_200_OK)

@csrf_exempt
@permission_classes([IsHoD])
def group_tasks_by_employee(tasks):
    grouped_tasks={}
    for task in tasks:
        employee=task.employee
        if employee not in grouped_tasks:
            grouped_tasks[employee]=[]
        grouped_tasks[employee].append(task)

    return {str(employee.id):EmployeeTaskSerializer(tasks,many=True).data for employee,tasks in grouped_tasks.items()}


@csrf_exempt
@permission_classes([IsHR])
@api_view(['GET','POST'])
def handle_hr_role(request):
    sort_by,sort_direction,show_incomplete,search_query=get_hr_query_params(request)

    if request.method=='POST':
        response=handle_upload_data(request)

        if response['status'] == 'error':
            return Response({'error': response['message']}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': response['message']}, status=status.HTTP_200_OK)


    employees = Employee.objects.all().annotate(
        total_tasks=Count('tasks'),
        approved_tasks=Count(Case(When(tasks__status='approved', then=1))),
    ).annotate(
        progress=F('approved_tasks') * 100.0 / F('total_tasks')
    )

    if show_incomplete:
        employees = employees.filter(progress__lt=100)
    if search_query:
        employees = employees.filter(Q(name__icontains=search_query) | Q(user__username__icontains=search_query))

    employees = sort_employees(employees, sort_by, sort_direction)
    employees_data = EmployeeSerializer(employees, many=True).data

    return Response({
        'employees': employees_data,
        'sort_by': sort_by,
        'sort_direction': sort_direction,
        'show_incomplete': show_incomplete,
    }, status=status.HTTP_200_OK)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsHR])
def handle_upload_data(request):
    try:
        excel_file = request.FILES.get('excel_file')

        if not excel_file:
            return Response({'error': 'No file uploaded.'}, status=status.HTTP_400_BAD_REQUEST)

        excel_file.seek(0)

        df=pd.read_excel(excel_file,engine='openpyxl')
        required_columns = ['userID','first_name','last_name', 'email', 'department_name', 'password']

    except Exception as e:
        return Response({'error': f'Error reading the Excel file: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

    if not all(column in df.columns for column in required_columns):
        return {'status': 'error', 'message': 'Missing required columns in the Excel file.'}

    success_count=0
    error_count=0
    errors=[]

    for _, row in df.iterrows():
        username = row.get('userID')
        first_name = row.get('first_name')
        last_name = row.get('last_name')
        email = row.get('email')
        department_name = row.get('department_name')
        password = row.get('password')

        if not all([username, first_name, last_name, email, department_name, password]):
            errors.append(f'Missing required fields in the row for user {username or "unknown"}')
            error_count += 1
            continue

        try:
            department=Department.objects.get(name=department_name)
        except Department.DoesNotExist:
            errors.append(f'Department "${department_name}" doesnt exists for {username}')
            error_count+=1
            continue

        if User.objects.filter(username=username).exists():
            error_count+=1
            continue
        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    password=password
                )
                Employee.objects.create(
                    user=user,
                    name=first_name,
                    department=department,
                    role='Employee'
                )
                success_count += 1
        except Exception as e:
            errors.append(f'Error creating user "{username}": {str(e)}')
            error_count += 1
    response_data = {
        'success_count': success_count,
        'error_count': error_count,
        'errors': errors
    }
    return Response(response_data, status=status.HTTP_200_OK if success_count > 0 else status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@permission_classes([IsHR])
def get_hr_query_params(request):
    sort_by = request.GET.get('sort', 'name')
    sort_direction = request.GET.get('direction', 'desc')
    show_incomplete = request.GET.get('incomplete', 'false') == 'true'
    search_query = request.GET.get('search', '')
    return sort_by, sort_direction, show_incomplete, search_query


@csrf_exempt
@permission_classes([IsHR])
def sort_employees(employees, sort_by, sort_direction):
    valid_sorts = ['progress']
    valid_directions = ['asc', 'desc']

    if sort_by not in valid_sorts:
        sort_by = 'name'
    if sort_direction not in valid_directions:
        sort_direction = 'desc'

    if sort_by == 'progress':
        employees = employees.order_by('progress') if sort_direction == 'asc' else employees.order_by('-progress')
    else:
        employees = employees.order_by('name')
    return employees