from django.contrib.auth import authenticate, login
from rest_framework import generics, permissions, viewsets, filters
from rest_framework.decorators import api_view
from django.contrib.auth.models import User
from django_filters import rest_framework as filters2
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.response import Response
from django.http import HttpResponseForbidden, HttpResponseNotFound, HttpResponse
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token

from .models import Material, MaterialCategory1, MaterialCategory2, MaterialCategory3, Supplier, Laboratory, Test, \
    DICStage, DICDatapoint
from .serializers import MaterialSerializer, UserSerializer, Category1Serializer, Category2Serializer, \
    Category3Serializer, SupplierSerializer, LaboratorySerializer, RegisterSerializer, TestSerializer, \
    DICStageSerializer, DICDataSerializer, CategoriesSerializer
from .permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly
from .filters import CategoryLowerFilter, CategoryMiddleFilter, CategoryUpperFilter, DICStageFilter, DICDataFilter
from .utils import process_test_data
from .pagination import DICDataPagination


@api_view(['POST'])
def login_view(request):
    if request.method == 'POST':
        data = request.data

        username = data.get('username', None)
        password = data.get('password', None)

        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                token = Token.objects.get(user=user)
                data = {"token": token.key}

                return Response(status=200, data=data)
            else:
                return Response(status=400)
        else:
            return Response(status=404)


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
    filter_backends = (filters2.DjangoFilterBackend, filters.OrderingFilter)
    ordering = ("stage_num",)
    filterset_class = DICStageFilter


class DICDataViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = DICDatapoint.objects.all()
    serializer_class = DICDataSerializer
    filter_backends = (filters2.DjangoFilterBackend, filters.OrderingFilter)
    ordering = ("stage", "index_x", "index_y")
    filterset_class = DICDataFilter
    pagination_class = DICDataPagination


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


@api_view(['DELETE'])
def delete_test_data(request, pk):
    try:
        test = Test.objects.get(pk=pk)
    except ObjectDoesNotExist:
        return HttpResponseNotFound()

    if request.user != test.submitted_by:
        return HttpResponseForbidden()

    existing_stages = {stage.stage_num for stage in test.stages.all()}
    if request.method == 'DELETE':
        if not existing_stages:
            data = {"message": "Cannot DELETE test data as it doesn't exist."}
            return Response(status=404, data=data)

        DICStage.objects.filter(test=test).delete()
        return Response()


@transaction.atomic
@api_view(['POST', 'PUT'])
def upload_test_data(request, pk):
    try:
        test = Test.objects.get(pk=pk)
    except ObjectDoesNotExist:
        return HttpResponseNotFound()

    if request.user != test.submitted_by:
        return HttpResponseForbidden()

    existing_stages = {stage.stage_num for stage in test.stages.all()}
    if request.method == 'POST':
        if existing_stages:
            data = {"message": "Cannot POST test data, as it already exists."}
            return Response(status=400, data=data)

    test_data = request.FILES
    stages, bad_format, duplicated_stages = process_test_data(test_data)

    if duplicated_stages:
        data = {"message": "Duplicated stages in uploaded data.", "duplicated_stages": duplicated_stages}
        return Response(status=400, data=data)

    read_stages = {stage[0] for stage in stages}
    already_in_db = read_stages.intersection(existing_stages)

    if already_in_db:
        if not request.query_params.get("override", None):
            data = {
                "message": "Uploaded stages already in DB. If you wish to override them set the \"override\" query param to true.",
                "overridden_stages": already_in_db}
            return Response(status=400, data=data)
        else:
            test.stages.filter(stage_num__in=already_in_db).delete()

    # Create data
    for stage, ts_undef, ts_def in stages:
        s = DICStage(test_id=pk, stage_num=stage, timestamp_undef=ts_undef, timestamp_def=ts_def)
        s.save()
        datapoint_list = list()
        datapoint_dict = stages[(stage, ts_undef, ts_def)]
        for datapoint in datapoint_dict:
            data = datapoint_dict[datapoint]
            datapoint_list.append(DICDatapoint(stage=s, index_x=datapoint[0], index_y=datapoint[1], x=data["x"],
                                               y=data["y"], z=data["z"], displacement_x=data["displacement_x"],
                                               displacement_y=data["displacement_y"],
                                               displacement_z=data["displacement_z"],
                                               strain_x=data["strain_x"], strain_y=data["strain_y"],
                                               strain_major=data["strain_major"], strain_minor=data["strain_minor"],
                                               thickness_reduction=data["thickness_reduction"]))
        DICDatapoint.objects.bulk_create(datapoint_list)

    data = {"created_stages": read_stages - already_in_db, "overridden_stages": already_in_db if already_in_db else None}

    return HttpResponse(data=data)
