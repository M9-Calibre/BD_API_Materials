import io
import json
import zipfile
import os

import django_filters
import pandas as pd
from dj_rest_auth.views import PasswordResetView
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import F
from django.http import HttpResponseForbidden, HttpResponseNotFound, HttpResponse
from django_filters import rest_framework as filters2
from rest_framework import generics, permissions, viewsets, filters, mixins
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .filters import CategoryLowerFilter, CategoryMiddleFilter, CategoryUpperFilter, DICStageFilter, DICDataFilter, \
    InstitutionUserFilter, MaterialParamsFilter
from .models import Material, MaterialCategory1, MaterialCategory2, MaterialCategory3, Supplier, Laboratory, Test, \
    DICStage, DICDatapoint, Model, ModelParams, Institution, InstitutionUser, MaterialParams
from .pagination import DICDataPagination
from .permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly
from .serializers import MaterialSerializer, UserSerializer, Category1Serializer, Category2Serializer, \
    Category3Serializer, SupplierSerializer, LaboratorySerializer, RegisterSerializer, TestSerializer, \
    DICStageSerializer, DICDataSerializer, MaterialNameIdSerializer, ModelSerializer, ModelParamsSerializer, \
    CustomPasswordResetSerializer, InstitutionSerializer, InstitutionUserSerializer, MaterialParamsSerializer
from .DIC_interaction import process_dic_data, update_metadata
from .models_scripts.points_generation import generate_points


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
    ordering = ("-name",)
    ordering_fields = ('name', 'tag', 'id')
    filterset_fields = ["category"]


class ModelParamsViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    queryset = ModelParams.objects.all()
    serializer_class = ModelParamsSerializer
    filter_backends = (filters2.DjangoFilterBackend,)
    filterset_fields = ["model", "submitted_by", "model__category"]

    def perform_create(self, serializer: ModelParamsSerializer):
        serializer.save(submitted_by=self.request.user)


class MaterialParamsViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOwnerOrReadOnly]
    queryset = MaterialParams.objects.all()
    serializer_class = MaterialParamsSerializer
    filter_backends = (filters2.DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter)
    # ordering = ("id",)
    # ordering_fields = ('id',)
    # search_fields = ('name', 'country')
    filterset_class = MaterialParamsFilter

    def perform_create(self, serializer: ModelParamsSerializer):
        serializer.save(submitted_by=self.request.user)


class RegisterUserAPIView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


class InstitutionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    queryset = Institution.objects.all()
    serializer_class = InstitutionSerializer


class InstitutionUserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    queryset = InstitutionUser.objects.all()
    serializer_class = InstitutionUserSerializer
    filter_backends = (filters2.DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter)
    ordering = ("id",)
    ordering_fields = ('id',)
    # search_fields = ('name', 'country')
    filterset_class = InstitutionUserFilter
    # filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    # ordering = ("name",)


class MaterialViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    filter_backends = (filters2.DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter)
    ordering = ("id",)
    ordering_fields = ('name', 'entry_date', 'id', 'upper_category', 'middle_category', 'lower_category', 'user')
    search_fields = ('name', 'description',)

    def perform_create(self, serializer: MaterialSerializer):
        serializer.save(submitted_by=self.request.user)

    def get_queryset(self):
        query = super().get_queryset().annotate(upper_category=F('category__middle_category__upper_category__category'),
                                                middle_category=F('category__middle_category__category'),
                                                lower_category=F('category__category'),
                                                user=F('submitted_by__username'))
        return query


class TestViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    queryset = Test.objects.all()
    serializer_class = TestSerializer
    filterset_fields = ["material", "submitted_by"]

    def perform_create(self, serializer: TestSerializer):
        serializer.save(submitted_by=self.request.user)


class DICStageViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = DICStage.objects.all()
    serializer_class = DICStageSerializer
    filter_backends = (filters2.DjangoFilterBackend, filters.OrderingFilter)
    ordering = ("stage_num",)
    filterset_class = DICStageFilter


class DICDataViewSet(viewsets.ReadOnlyModelViewSet):
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
def upload_dic_files(request, pk):
    # print(f"{request.body=}")
    # print(f"{json.loads(request.body)=}")
    # teste = request.body
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
    if file_format not in ["aramis", "matchid", "matchid_multiple_files"]:
        data = {"message": f"Unrecognized file format: {file_format}."}
        return Response(status=400, data=data)

    file_identifiers = request.POST.get("file_identifiers")
    print(f"{request.POST=}")
    # print(f"{teste=}")
    existing_stages = {stage.stage_num for stage in test.stages.all()}
    if request.method == 'POST':
        if existing_stages:
            data = {"message": "Cannot POST test data, as it already exists."}
            return Response(status=400, data=data)

    test_data = request.FILES

    files = test_data.keys()

    if file_format != "matchid_multiple_files" and not (files - {"stage_metadata.csv"}):
        data = {"message": "Cannot POST/PUT test data, as no DIC files were uploaded."}
        return Response(status=400, data=data)

    stages, bad_format, duplicated_stages, not_in_metadata, skipped_files = process_dic_data(test_data, file_format,
                                                                                             _3d, file_identifiers)

    if not not_in_metadata and not bad_format and not duplicated_stages and not stages and not skipped_files:
        data = {"message": "Bad format of metadata file."}
        return Response(status=400, data=data)

    # if not_in_metadata:
    #     data = {"message": "Missing metadata for files.", "no_metadata": not_in_metadata}
    #     return Response(status=400, data=data)

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


@transaction.atomic
@api_view(['POST'])
def upload_metadata(request, pk):
    try:
        test = Test.objects.get(pk=pk)
    except ObjectDoesNotExist:
        return HttpResponseNotFound()

    if request.user != test.submitted_by:
        return HttpResponseForbidden()

    test_data = request.FILES
    stage_metadata_file = test_data.get("stage_metadata.csv")

    if not stage_metadata_file:
        data = {"message": "No stage metadata file provided."}
        return Response(status=400, data=data)

    existing_stages = [stage for stage in test.stages.all()]
    not_in_metadata, invalid_metadata, dic_stages = update_metadata(stage_metadata_file, existing_stages)

    if invalid_metadata:
        data = {"message": "Bad format of metadata file."}
        return Response(status=400, data=data)

    if not_in_metadata:
        data = {"message": "Missing metadata for files.", "no_metadata": not_in_metadata}
        return Response(status=400, data=data)

    DICStage.objects.bulk_update(dic_stages, fields=['timestamp_def', 'load'])

    data = {"updated_stages": [stage.stage_num for stage in dic_stages],
            "message": "Metadata updated successfully."}

    return Response(data=data)

@api_view(['GET'])
def get_test_data(request, pk):
    try:
        test = Test.objects.get(pk=pk)
    except ObjectDoesNotExist:
        return HttpResponseNotFound()

    existing_stages = {stage.stage_num for stage in test.stages.all()}
    if request.method == 'GET':
        if not existing_stages:
            data = {"message": "Cannot GET test data as it doesn't exist."}
            return Response(status=404, data=data)

    _3d = request.query_params.get("3d", False)
    if _3d:
        _3d = _3d.lower() in ["true", "1"]

    files = ['stage_metadata.csv']
    with open('stage_metadata.csv', 'w') as metadata:
        for stage in test.stages.all():
            stage: DICStage
            metadata.write(f'{stage.stage_num},{stage.timestamp_def},{stage.load}\n')
            if _3d:
                headers = ['coor.X [mm]', 'coor.Y [mm]', 'coor.Z [mm]', 'disp.Horizontal Displacement U [mm]',
                           'disp.Vertical Displacement V [mm]', 'disp.Out-Of-Plane: W [mm]',
                           'strain.Strain-global frame: Exx [ ]', 'strain.Strain-global frame: Eyy [ ]',
                           'strain.Strain-global frame: Exy [ ]', 'strain.Strain-major: E1 [ ]',
                           'strain.Strain-minor: E2 [ ]', 'deltaThick: dThick [ ]']
                datapoint: DICDatapoint
                data = [
                    [datapoint.x, datapoint.y, datapoint.z, datapoint.displacement_x, datapoint.displacement_y,
                     datapoint.displacement_z, datapoint.strain_x, datapoint.strain_y, datapoint.strain_xy,
                     datapoint.strain_major, datapoint.strain_minor, datapoint.thickness_reduction]
                    for datapoint in stage.dicdatapoint_set.all()]
            else:
                headers = ['coor.X [mm]', 'coor.Y [mm]', 'disp.Horizontal Displacement U [mm]',
                           'disp.Vertical Displacement V [mm]', 'strain.Strain-global frame: Exx [ ]',
                           'strain.Strain-global frame: Eyy [ ]', 'strain.Strain-global frame: Exy [ ]',
                           'strain.Strain-major: E1 [ ]', 'strain.Strain-minor: E2 [ ]', 'deltaThick: dThick [ ]']
                datapoint: DICDatapoint
                data = [
                    [datapoint.x, datapoint.y, datapoint.displacement_x, datapoint.displacement_y, datapoint.strain_x,
                     datapoint.strain_y, datapoint.strain_xy, datapoint.strain_major, datapoint.strain_minor,
                     datapoint.thickness_reduction]
                    for datapoint in stage.dicdatapoint_set.all()]

            df = pd.DataFrame(data, columns=headers)
            file_name = f'stage_{stage.stage_num}.csv'
            df.to_csv(file_name, index=False)
            files.append(file_name)

    buffer = io.BytesIO()
    zip_file = zipfile.ZipFile(buffer, 'w')
    for file in files:
        zip_file.write(file, compress_type=zipfile.ZIP_DEFLATED)
        os.remove(file)
    zip_file.close()

    response = HttpResponse(buffer.getvalue())
    response['Content-Type'] = 'application/x-zip-compressed'
    response['Content-Disposition'] = f'attachment; filename=test_{test.id}_data.zip'
    return response


@api_view(['POST'])
def get_model_graph(request):
    data = request.data
    function_type = data.get("function_type", "")
    args = data.get("arguments", {})
    function = data.get("function", "")
    # hardening_args = data.get("hardening_arguments", {})
    # hardening_function = data.get("hardening_function", "")
    # yield_args = data.get("yield_arguments", {})
    # yield_function = data.get("yield_function", "")
    # elastic_args = data.get("elastic_arguments", {})
    # elastic_function = data.get("elastic_function", "")

    if function_type not in ["hardening", "yield", "elastic"]:
        return Response(status=400, data={"message": f"Invalid function type. Given function type was "
                                                     f"'{function_type}'. Valid function types are: 'hardening', "
                                                     f"'yield' and 'elastic'."})

    # hardening_points, yield_points, elastic_points, hardening_x, elastic_x = generate_points(hardening_args, yield_args,
    #                                                                                          elastic_args,
    #                                                                                          hardening_function,
    #                                                                                          yield_function,
    #                                                                                          elastic_function)

    points, inpt = generate_points(function_type, args, function)

    data = {
        "points": points,
        "x": inpt
    }

    return Response(status=200, data=data)


## Password Reset
class CustomPasswordResetView(PasswordResetView):
    serializer_class = CustomPasswordResetSerializer
