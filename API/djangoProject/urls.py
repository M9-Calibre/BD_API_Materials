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
router.register(r'institutions', views.InstitutionViewSet, basename='institutions')
router.register(r'institution_users', views.InstitutionUserViewSet, basename='institution_users')
router.register(r'suppliers', views.SupplierViewSet, basename='suppliers')
router.register(r'labs', views.LaboratoryViewSet, basename='labs')
router.register(r'tests', views.TestViewSet, basename='tests')
router.register(r'DICstages', views.DICStageViewSet, basename='DICstages')
router.register(r'DICdata', views.DICDataViewSet, basename='DICdata')
router.register(r'categories/upper', views.CategoriesUpperList, basename='categories_upper')
router.register(r'categories/middle', views.CategoriesMiddleList, basename='categories_middle')
router.register(r'categories/lower', views.CategoriesLowerList, basename='categories_lower')
router.register(r'models', views.ModelViewSet, basename='models')
router.register(r'modelparams', views.ModelParamsViewSet, basename='modelparams')
router.register(r'materialparams', views.MaterialParamsViewSet, basename='materialparams')
router.register(r'tests/params', views.ModelParamsViewSet, basename='tests_params')

urlpatterns = [
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('users/register/', views.RegisterUserAPIView.as_view()),
    path('users/login/', views.login_view),
    path('users/profile/', views.profile),
    path('materials/list/', views.MaterialList.as_view()),
    path('api-auth/', include('rest_framework.urls')),
    path('tests/<int:pk>/upload_dic/', views.upload_dic_files),
    path('tests/<int:pk>/upload_metadata/', views.upload_metadata),
    path('tests/<int:pk>/download/', views.get_test_data),
    path('tests/<int:pk>/delete/', views.delete_test_data),
    path('models/points/', views.get_model_graph),
    path("tests", views.get_model_graph),
    path('deletematerial/<int:material_id>/', views.DeleteMaterialByPostView.as_view(), name='delete_material'),
    path('', include(router.urls))
]
