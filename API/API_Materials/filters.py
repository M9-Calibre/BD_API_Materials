from django_filters import rest_framework as filters
from .models import MaterialCategory3, MaterialCategory2, MaterialCategory1, DICDatapoint, DICStage, InstitutionUser


class DICDataFilter(filters.FilterSet):
    test = filters.NumberFilter(field_name="stage__test", label="test")
    stage = filters.NumberFilter(field_name="stage", label="stage")

    class Meta:
        model = DICDatapoint
        fields = ["test", "stage"]


class DICStageFilter(filters.FilterSet):
    test = filters.NumberFilter(field_name="test", label="test")

    class Meta:
        model = DICStage
        fields = ["test"]


class CategoryLowerFilter(filters.FilterSet):
    upper_category = filters.CharFilter(field_name="upper_category__middle_category__category", label="upper_category")
    middle_category = filters.CharFilter(field_name="middle_category__category", label="middle_category")
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

class InstitutionUserFilter(filters.FilterSet):
    institution = filters.NumberFilter(field_name="institution", label="institution")
    user = filters.NumberFilter(field_name="user", label="user")

    class Meta:
        model = InstitutionUser
        fields = ["institution", "user", "has_active_institution"]