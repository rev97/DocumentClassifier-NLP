"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from django.views.generic import TemplateView
from backend.backend.views import main_api,view_pdf,model_training_api,get_trained_model,home,check_task_status

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', main_api),
    path('view-pdf/', view_pdf, name='view_pdf'),
    path('train-model/', model_training_api, name='train_model'),
    path('get-model/', get_trained_model, name='get_model'),
    path('job-status/', check_task_status, name='check_task_status'),
    # Define a catch-all URL pattern to serve the React application
    re_path(r'^.*$', TemplateView.as_view(template_name='index.html')),
]
