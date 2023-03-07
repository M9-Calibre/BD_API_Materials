import json

from rest_framework import generics, permissions, viewsets, filters
from rest_framework.decorators import api_view
from django.contrib.auth.models import User
from django_filters import rest_framework as filters2
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
    DICStageSerializer, DICDataSerializer, CategoriesSerializer
from .permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly
from .filters import CategoryLowerFilter, CategoryMiddleFilter, CategoryUpperFilter
from .utils import process_test_data


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
    filter_backends = (filters2.DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter)
    ordering = ("id",)
    ordering_fields = ('name', 'mat_id', 'entry_date')
    search_fields = ('name', 'description',)

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


class CategoriesList(generics.ListAPIView):
    queryset = MaterialCategory3.objects.all()
    serializer_class = CategoriesSerializer


@api_view(['POST'])
def upload_test_data(request, pk):
    # TODO check user's permission
    test_data = request.FILES
    stages = process_test_data(test_data)
    to_save = dict()
    stage_list = list()
    for stage, ts_undef, ts_def in stages:
        s = DICStage(test_id=pk, stage_num=stage, timestamp_undef=ts_undef, timestamp_def=ts_undef)
        stage_list.append(s)
        datapoint_list = list()
        datapoint_dict = stages[(stage, ts_undef, ts_def)]
        for datapoint in datapoint_dict:
            data = datapoint_dict[datapoint]
            datapoint_list.append(DICDatapoint(stage=s, index_x=datapoint[0], index_y=datapoint[1], x=data["x"],
                                    y=data["y"], z=data["z"], displacement_x=data["displacement_x"],
                                    displacement_y=data["displacement_y"], displacement_z=data["displacement_z"],
                                    strain_x=data["strain_x"], strain_y=data["strain_y"],
                                    strain_major=data["strain_major"], strain_minor=data["strain_minor"],
                                    thickness_reduction=data["thickness_reduction"]))
        to_save[stage] = datapoint_list

    for stage in stage_list:
        stage.save()
    for stage in to_save:
        for datapoint in to_save[stage]:
            datapoint.save()

    return Response()

