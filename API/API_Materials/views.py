from django.contrib.auth import authenticate, login
from rest_framework import generics, permissions, viewsets, filters, mixins
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.models import User
from django_filters import rest_framework as filters2
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from rest_framework.response import Response
from django.http import HttpResponseForbidden, HttpResponseNotFound
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token

from .models import Material, MaterialCategory1, MaterialCategory2, MaterialCategory3, Supplier, Laboratory, Test, \
    DICStage, DICDatapoint, Model, ModelParams
from .serializers import MaterialSerializer, UserSerializer, Category1Serializer, Category2Serializer, \
    Category3Serializer, SupplierSerializer, LaboratorySerializer, RegisterSerializer, TestSerializer, \
    DICStageSerializer, DICDataSerializer, MaterialNameIdSerializer, ModelSerializer
from .permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly
from .filters import CategoryLowerFilter, CategoryMiddleFilter, CategoryUpperFilter, DICStageFilter, DICDataFilter
from .utils import process_test_data
from .pagination import DICDataPagination


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    if request.method == 'POST':
        data = request.data

        username = data.get('username', None)
        password = data.get('password', None)

        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                token = Token.objects.get_or_create(user=user)[0]
                data = {"token": token.key}

                return Response(status=200, data=data)
            else:
                return Response(status=400)
        else:
            return Response(status=404)


@api_view(['GET'])
def profile(request):
    if request.method == 'GET':
        user = request.user

        if user is not None:
            if user.is_active:
                data = {
                    "id": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "username": user.username,
                    "admin": user.is_staff
                }

                return Response(status=200, data=data)

            else:
                return Response(status=400)
        else:
            return Response(status=404)


class ModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    queryset = Model.objects.all()
    serializer_class = ModelSerializer
    filter_backends = (filters2.DjangoFilterBackend, filters.OrderingFilter)
    ordering = ("name",)
    ordering_fields = ('name', 'tag', 'id')


class RegisterUserAPIView(generics.CreateAPIView): # TODO destroy
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


class MaterialViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    filter_backends = (filters2.DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter)
    ordering = ("id",)
    ordering_fields = ('name', 'mat_id', 'entry_date', 'id', 'upper_category', 'middle_category', 'lower_category', 'submitted_by')
    search_fields = ('name', 'description',)

    def perform_create(self, serializer: MaterialSerializer):
        serializer.save(submitted_by=self.request.user)


class TestViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    queryset = Test.objects.all()
    serializer_class = TestSerializer
    filterset_fields = ["material", "submitted_by"]

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
    ordering = ("stage",)
    filterset_class = DICDataFilter
    pagination_class = DICDataPagination


class UserViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.DestroyModelMixin):
    permission_classes = [permissions.IsAdminUser]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters2.DjangoFilterBackend, filters.OrderingFilter)
    ordering = ("id", "username", "first_name", "last_name", "email")
    ordering_fields = ('username', 'id')


class SupplierViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    filter_backends = (filters2.DjangoFilterBackend, filters.OrderingFilter)
    ordering = ("id",)


class LaboratoryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    queryset = Laboratory.objects.all()
    serializer_class = LaboratorySerializer
    filter_backends = (filters2.DjangoFilterBackend, filters.OrderingFilter)
    ordering = ("id",)


class CategoriesUpperList(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    queryset = MaterialCategory1.objects.all()
    serializer_class = Category1Serializer
    filter_backends = (filters2.DjangoFilterBackend, filters.OrderingFilter)
    ordering = ("category",)
    ordering_fields = ('category', 'id')
    filterset_class = CategoryUpperFilter


class CategoriesMiddleList(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    queryset = MaterialCategory2.objects.all()
    serializer_class = Category2Serializer
    filter_backends = (filters2.DjangoFilterBackend, filters.OrderingFilter)
    ordering = ("category",)
    ordering_fields = ('category', 'id')
    filterset_class = CategoryMiddleFilter


class CategoriesLowerList(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    queryset = MaterialCategory3.objects.all()
    serializer_class = Category3Serializer
    filter_backends = (filters2.DjangoFilterBackend, filters.OrderingFilter)
    ordering = ("category",)
    ordering_fields = ('category', 'id')
    filterset_class = CategoryLowerFilter


class MaterialList(generics.ListAPIView):
    queryset = Material.objects.all()
    serializer_class = MaterialNameIdSerializer
    filter_backends = (filters2.DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter)
    ordering = ("id",)
    ordering_fields = ('name', 'id',)
    search_fields = ('name',)
    pagination_class = None


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
        return Response(status=204)


@transaction.atomic
@api_view(['POST', 'PUT'])
def upload_test_data(request, pk):
    try:
        test = Test.objects.get(pk=pk)
    except ObjectDoesNotExist:
        return HttpResponseNotFound()

    if request.user != test.submitted_by:
        return HttpResponseForbidden()

    override = request.query_params.get("override", False)
    if override:
        override = override.lower() in ["true", "1"]

    _3d = request.query_params.get("3d", False)
    if _3d:
        _3d = _3d.lower() in ["true", "1"]

    file_format = request.query_params.get("file_format", "aramis").lower()
    if file_format not in ["aramis", "matchid"]:
        data = {"message": f"Unrecognized file format: {file_format}."}
        return Response(status=400, data=data)

    existing_stages = {stage.stage_num for stage in test.stages.all()}
    if request.method == 'POST':
        if existing_stages:
            data = {"message": "Cannot POST test data, as it already exists."}
            return Response(status=400, data=data)

    test_data = request.FILES

    files = test_data.keys()

    if "stage_metadata.csv" not in files:
        data = {"message": "No stage metadata file provided."}
        return Response(status=400, data=data)

    if not (files-{"stage_metadata.csv"}):
        data = {"message": "Cannot POST/PUT test data, as no DIC files were uploaded."}
        return Response(status=400, data=data)

    stages, bad_format, duplicated_stages, not_in_metadata, skipped_files = process_test_data(test_data, file_format, _3d)

    if not_in_metadata:
        data = {"message": "Missings metadata for files.", "no_metadata": not_in_metadata}
        return Response(status=400, data=data)

    if bad_format:
        data = {"message": "Bad format found in input data files.", "bad_format_files": bad_format}
        return Response(status=400, data=data)

    if duplicated_stages:
        data = {"message": "Duplicated stages in uploaded data.", "duplicated_stages": duplicated_stages}
        return Response(status=400, data=data)

    if not stages:
        data = {"message": "Cannot POST/PUT test data, as no valid files were uploaded.",
                "skipped_files": skipped_files if skipped_files else None}
        return Response(status=400, data=data)

    read_stages = {stage[0] for stage in stages}
    already_in_db = read_stages.intersection(existing_stages)

    if already_in_db:
        if not override:
            data = {
                "message": "Uploaded stages already in DB. If you wish to override them set the \"override\" query param to true.",
                "overridden_stages": already_in_db}
            return Response(status=400, data=data)
        else:
            test.stages.filter(stage_num__in=already_in_db).delete()

    # Create data
    for stage, ts_def, load in stages:
        s = DICStage(test_id=pk, stage_num=stage, timestamp_def=ts_def, load=load)
        s.save()
        datapoint_list = []
        datapoints = stages[(stage, ts_def, load)]
        for datapoint in datapoints:
            datapoint_list.append(DICDatapoint(stage=s, **datapoint))

        DICDatapoint.objects.bulk_create(datapoint_list)

    data = {"created_stages": read_stages - already_in_db,
            "overridden_stages": already_in_db if already_in_db else None,
            "skipped_files": skipped_files if skipped_files else None}

    return Response(data=data)
