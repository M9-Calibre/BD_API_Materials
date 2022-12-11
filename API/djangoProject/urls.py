"""djangoProject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import path, include

from API_Materials import views


urlpatterns = [
    path('users/register/', views.register_user),
    path('users/login/', views.login_user),
    path('users/', views.UserList.as_view()),
    path('users/<int:pk>/', views.UserDetail.as_view()),
    path('categories/upper', views.Categories1List.as_view()),
    path('categories/middle', views.Categories2List.as_view()),
    path('categories/lower', views.Categories3List.as_view()),
    path('materials/', views.MaterialList.as_view()),
    path('materials/<int:pk>/', views.MaterialDetail.as_view(), name='material_detail'),
    path('api-auth/', include('rest_framework.urls'))
]
