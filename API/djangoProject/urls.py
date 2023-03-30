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
from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from API_Materials import views
from rest_framework.authtoken import views as views2

schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

router = DefaultRouter()
router.register(r'materials', views.MaterialViewSet, basename="materials")
router.register(r'users', views.UserViewSet, basename="users")
router.register(r'suppliers', views.SupplierViewSet, basename='suppliers')
router.register(r'labs', views.LaboratoryViewSet, basename='labs')
router.register(r'tests', views.TestViewSet, basename='tests')
router.register(r'DICstages', views.DICStageViewSet, basename='DICstages')
router.register(r'DICdata', views.DICDataViewSet, basename='DICdata')

urlpatterns = [
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('users/register/', views.RegisterUserAPIView.as_view()),
    path('users/login/', views.login_view),
    path('categories/', views.CategoriesList.as_view()),
    path('categories/upper', views.CategoriesUpperList.as_view()),
    path('categories/middle', views.CategoriesMiddleList.as_view()),
    path('categories/lower', views.CategoriesLowerList.as_view()),
    path('api-auth/', include('rest_framework.urls')),
    path('tests/<int:pk>/upload', views.upload_test_data),
    path('tests/<int:pk>/delete', views.delete_test_data),
    path('', include(router.urls))
]
