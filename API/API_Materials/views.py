import json

from rest_framework import generics, permissions, viewsets
from rest_framework.decorators import api_view
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from rest_framework.permissions import AllowAny

from .models import Material, MaterialCategory1, MaterialCategory2, MaterialCategory3, Supplier, Laboratory
from .serializers import MaterialSerializer, UserSerializer, Category1Serializer, Category2Serializer, \
    Category3Serializer, SupplierSerializer, LaboratorySerializer, RegisterSerializer
from .permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly


# Create your views here.
@api_view(['GET'])
def login_user(request):
    request_json = json.loads(request.body.decode())
    try:
        username = request_json["username"]
        password = request_json["password"]
    except KeyError:
        response = HttpResponseBadRequest()
        response.reason_phrase = "Missing registration parameter."
        return response

    user = authenticate(username=username, password=password)

    if user:
        token = Token.objects.get(user=user)
        response = JsonResponse({"token": token.key})
        response.status_code = 200
        response.reason_phrase = "Login successful."
        return response
    response = HttpResponseForbidden()
    response.reason_phrase = "Wrong credentials."
    return response


class MaterialViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer

    def perform_create(self, serializer: MaterialSerializer):
        serializer.save(submitted_by=self.request.user)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAdminUser]
    queryset = User.objects.all()
    serializer_class = UserSerializer


class RegisterUserAPIView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


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


class CategoriesMiddleList(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrReadOnly]
    queryset = MaterialCategory2.objects.all()
    serializer_class = Category2Serializer


class CategoriesLowerList(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrReadOnly]
    queryset = MaterialCategory3.objects.all()
    serializer_class = Category3Serializer
