from rest_framework.pagination import PageNumberPagination
from .models import Material, MaterialCategory3, MaterialCategory1


class DICDataPagination(PageNumberPagination):
    page_size = 1000
    page_size_query_param = "page_size"
    max_page_size = 10000


class AllMaterialsPagination(PageNumberPagination):
    page_size = Material.objects.count()
    page_size_query_param = "page_size"


class AllCategoriesPagination(PageNumberPagination):
    page_size = MaterialCategory3.objects.count()
    page_size_query_param = "page_size"


class AllUpperCategoriesPagination(PageNumberPagination):
    page_size = MaterialCategory1.objects.count()
    page_size_query_param = "page_size"
