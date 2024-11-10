from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView

from . import views
from .serializers import CustomTokenObtainPairSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


urlpatterns = [
    # path('',views.index,name='index'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('logout', views.logout, name='logout'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('employee/submit_feedback/', views.handle_feedback_submission, name='submit_feedback'),
    path('hod/update_task/', views.update_task_status, name='update_task_status'),
    path('hr/upload_excel/', views.handle_upload_data, name='upload_excel'),
    path('hr/<int:employee_id>',views.employee_tasklist_view,name='employee_tasklist_view')

]
