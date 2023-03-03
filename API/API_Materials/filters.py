from django_filters import rest_framework as filters
from .models import MaterialCategory3, MaterialCategory2, MaterialCategory1


class CategoryLowerFilter(filters.FilterSet):
    upper_category = filters.CharFilter(field_name="upper_category__upper_category__category", label="upper_category")
    middle_category = filters.CharFilter(field_name="upper_category__category", label="middle_category")
    category = filters.CharFilter(field_name="category", label="category")

    class Meta:
        model = MaterialCategory3
        fields = ["upper_category", "middle_category", "category"]


class CategoryMiddleFilter(filters.FilterSet):
    upper_category = filters.CharFilter(field_name="upper_category__category", label="upper_category")
    middle_category = filters.CharFilter(field_name="category", label="middle_category")

    class Meta:
        model = MaterialCategory2
        fields = ["upper_category", "middle_category"]


class CategoryUpperFilter(filters.FilterSet):
    upper_category = filters.CharFilter(field_name="category", label="upper_category")

    class Meta:
        model = MaterialCategory1
        fields = ["upper_category"]



