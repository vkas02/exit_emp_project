from django.urls import path,include
from . import views

urlpatterns = [
    # path('',views.index,name='index'),
    path('dashboard',views.dashboard,name='dashboard'),
    path('logout',views.logout,name='logout'),
    path('employee/submit_feedback/', views.handle_feedback_submission, name='submit_feedback'),
    path('hod/update_task/', views.update_task_status, name='update_task_status'),
    path('hr/upload_excel/', views.handle_upload_data, name='upload_excel'),


]
