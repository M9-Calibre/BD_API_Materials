import json

from rest_framework import generics, permissions, viewsets
from rest_framework.decorators import api_view
from django.contrib.auth.models import User
from django_filters import rest_framework as filters
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.authentication import BasicAuthentication
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from .models import Material, MaterialCategory1, MaterialCategory2, MaterialCategory3, Supplier, Laboratory, Test, \
    DICStage, DICDatapoint
from .serializers import MaterialSerializer, UserSerializer, Category1Serializer, Category2Serializer, \
    Category3Serializer, SupplierSerializer, LaboratorySerializer, RegisterSerializer, TestSerializer,  \
    DICStageSerializer, DICDataSerializer
from .permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly
from .filters import CategoryLowerFilter, CategoryMiddleFilter, CategoryUpperFilter


# Create your views here.
class LogInView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        content = {
            'user': str(request.user),  # `django.contrib.auth.User` instance.
            'auth': str(request.auth),  # None
        }
        return Response(content)


class RegisterUserAPIView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


class MaterialViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer

    def perform_create(self, serializer: MaterialSerializer):
        serializer.save(submitted_by=self.request.user)


class TestViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    queryset = Test.objects.all()
    serializer_class = TestSerializer
    filterset_fields = ["material"]

    def perform_create(self, serializer: TestSerializer):
        serializer.save(submitted_by=self.request.user)


class DICStageViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = DICStage.objects.all()
    serializer_class = DICStageSerializer


class DICDataViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = DICDatapoint.objects.all()
    serializer_class = DICDataSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAdminUser]
    queryset = User.objects.all()
    serializer_class = UserSerializer


class SupplierViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer


class LaboratoryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    queryset = Laboratory.objects.all()
    serializer_class = LaboratorySerializer


class CategoriesUpperList(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrReadOnly]
    queryset = MaterialCategory1.objects.all()
    serializer_class = Category1Serializer
    filterset_class = CategoryUpperFilter


class CategoriesMiddleList(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrReadOnly]
    queryset = MaterialCategory2.objects.all()
    serializer_class = Category2Serializer
    filterset_class = CategoryMiddleFilter


class CategoriesLowerList(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrReadOnly]
    queryset = MaterialCategory3.objects.all()
    serializer_class = Category3Serializer
    filterset_class = CategoryLowerFilter
