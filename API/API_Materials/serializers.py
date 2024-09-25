from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.validators import UniqueValidator

from .models import Material, MaterialCategory3, MaterialCategory2, MaterialCategory1, Test, ThermalProperties, \
    MechanicalProperties, PhysicalProperties, Laboratory, Supplier, Location, DICStage, DICDatapoint, Model, ModelParams, Institution, InstitutionUser, \
    MaterialParams
from django.contrib.auth.models import User

from typing import Dict


class ModelSerializer(serializers.ModelSerializer):
    def validate_input(self, value):
        if isinstance(value, list):
            return value
        else:
            raise serializers.ValidationError("Input is not a list.")

    class Meta:
        model = Model
        fields = '__all__'


class ModelParamsSerializer(serializers.ModelSerializer):
    # test = serializers.PrimaryKeyRelatedField(many=False, read_only=False, queryset=Test.objects.all())
    user = serializers.SlugRelatedField(many=False, read_only=True, slug_field='username')
    submitted_by = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    name = serializers.CharField(source='model.name', read_only=True)
    function_name = serializers.CharField(source='model.function_name', read_only=True)

    # def validate(self, data):
    #     linked_obj = data['test']
    #     if linked_obj.submitted_by == self.context['request'].user:
    #         return data
    #     else:
    #         raise PermissionDenied(detail=None, code=None)

    def validate_params(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Params is not a dictionary.")

        model_id = self.initial_data.get("model", None)
        if not model_id:
            raise serializers.ValidationError("Not a valid model.")
        model = Model.objects.get(pk=model_id)

        keys = value.keys()
        required = set(model.input)

        if keys == required:
            return value
        raise serializers.ValidationError("Given params don't match model input.")

    class Meta:
        model = ModelParams
        fields = '__all__'

class MaterialParamsSerializer(serializers.ModelSerializer):
    submitted_by = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    submitted_by_username = serializers.ReadOnlyField(source="submitted_by.username")
    material = serializers.PrimaryKeyRelatedField(many=False, read_only=False, queryset=Material.objects.all())
    elastic_model_name = serializers.ReadOnlyField(source="elastic_model_params.model.name")
    yield_model_name = serializers.ReadOnlyField(source="yield_model_params.model.name")
    hardening_model_name = serializers.ReadOnlyField(source="hardening_model_params.model.name")

    class Meta:
        model = MaterialParams
        fields = '__all__'


class StageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = DICStage
        fields = ["id", "stage_num"]


class TestSerializer(serializers.ModelSerializer):
    submitted_by = serializers.SlugRelatedField(many=False, read_only=True, slug_field='username')
    material = serializers.PrimaryKeyRelatedField(many=False, read_only=False, queryset=Material.objects.all())
    stages = serializers.SerializerMethodField()

    class Meta:
        model = Test
        fields = '__all__'

    def get_stages(self, instance):
        stages = instance.stages.all().order_by('stage_num')
        return StageListSerializer(stages, many=True, read_only=True).data


class DICStageSerializer(serializers.ModelSerializer):
    test = serializers.PrimaryKeyRelatedField(many=False, read_only=False, queryset=Test.objects.all())

    def validate(self, data):
        linked_obj = data['test']
        if linked_obj.submitted_by == self.context['request'].user:
            return data
        else:
            raise PermissionDenied(detail=None, code=None)

    class Meta:
        model = DICStage
        exclude = ['id']


class DICDataSerializer(serializers.ModelSerializer):
    stage = serializers.PrimaryKeyRelatedField(many=False, read_only=False, queryset=DICStage.objects.all())

    def validate(self, data):
        linked_obj = data['stage']
        if linked_obj.test.submitted_by == self.context['request'].user:
            return data
        else:
            raise PermissionDenied(detail=None, code=None)

    class Meta:
        model = DICDatapoint
        exclude = ['id']


class ThermalPropsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThermalProperties
        exclude = ['id']


class MechanicalPropsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MechanicalProperties
        exclude = ['id']


class PhysicalPropsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhysicalProperties
        exclude = ['id']


class MaterialNameIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ['id', 'name', 'submitted_by']


class MaterialSerializer(serializers.ModelSerializer):
    upper_category = serializers.ReadOnlyField(source="category.middle_category.upper_category.category")
    middle_category = serializers.ReadOnlyField(source="category.middle_category.category")
    lower_category = serializers.ReadOnlyField(source="category.category")
    upper_category_id = serializers.ReadOnlyField(source="category.middle_category.upper_category.id")
    middle_category_id = serializers.ReadOnlyField(source="category.middle_category.id")
    user = serializers.ReadOnlyField(source="submitted_by.username")
    submitted_by = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    thermal_properties = ThermalPropsSerializer(many=False, required=False)
    mechanical_properties = MechanicalPropsSerializer(many=False, required=False)
    physical_properties = PhysicalPropsSerializer(many=False, required=False)
    category = serializers.PrimaryKeyRelatedField(many=False, queryset=MaterialCategory3.objects.all())
    tests = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    def create(self, validated_data):
        try:
            thermal_props = validated_data.pop("thermal_properties")
        except KeyError:
            thermal_props = None

        try:
            physical_props = validated_data.pop("physical_properties")
        except KeyError:
            physical_props = None

        try:
            mechanical_props = validated_data.pop("mechanical_properties")
        except KeyError:
            mechanical_props = None

        material_info = validated_data
        material = Material.objects.create(**material_info)
        if thermal_props:
            thermal_props = ThermalProperties.objects.create(material=material, **thermal_props)
            material.thermal_properties = thermal_props
            material.save()

        if mechanical_props:
            mechanical_props = MechanicalProperties.objects.create(material=material, **mechanical_props)
            material.mechanical_properties = mechanical_props
            material.save()

        if physical_props:
            physical_props = PhysicalProperties.objects.create(material=material, **physical_props)
            material.physical_properties = physical_props
            material.save()

        return material

    def update(self, instance: Material, validated_data: dict):
        instance.name = validated_data.get('name', instance.name)
        instance.category = validated_data.get('category', instance.category)
        instance.description = validated_data.get('description', instance.description)
        instance.source = validated_data.get('source', instance.source)
        instance.designation = validated_data.get('designation', instance.designation)
        instance.heat_treatment = validated_data.get('heat_treatment', instance.heat_treatment)

        validated_thermal_props = validated_data.get('thermal_properties')
        thermal_props = instance.thermal_properties

        validated_physical_props = validated_data.get('physical_properties')
        physical_props = instance.physical_properties

        validated_mechanical_props = validated_data.get('mechanical_properties')
        mechanical_props = instance.mechanical_properties

        if validated_thermal_props:
            if thermal_props:
                thermal_props.thermal_conductivity_tp = validated_thermal_props.get('thermal_conductivity_tp',
                                                                                    thermal_props.thermal_conductivity_tp)
                thermal_props.thermal_expansion_coef = validated_thermal_props.get('thermal_expansion_coef',
                                                                                   thermal_props.thermal_expansion_coef)
                thermal_props.specific_heat_capacity = validated_thermal_props.get('specific_heat_capacity',
                                                                                   thermal_props.specific_heat_capacity)
            else:
                thermal_props = ThermalProperties.objects.create(material=instance, **validated_thermal_props)
            thermal_props.save()
            instance.thermal_properties = thermal_props

        if validated_physical_props:
            if physical_props:
                physical_props.chemical_composition = validated_physical_props.get('chemical_composition',
                                                                                   physical_props.chemical_composition)
            else:
                physical_props = PhysicalProperties.objects.create(material=instance, **validated_physical_props)
            physical_props.save()
            instance.physical_properties = physical_props

        if validated_mechanical_props:
            if mechanical_props:
                mechanical_props.tensile_strength = validated_mechanical_props.get('tensile_strength',
                                                                                   mechanical_props.tensile_strength)
                mechanical_props.thermal_conductivity_mp = validated_mechanical_props.get('thermal_conductivity_mp',
                                                                                          mechanical_props.thermal_conductivity_mp)
                mechanical_props.reduction_of_area = validated_mechanical_props.get('reduction_of_area',
                                                                                    mechanical_props.reduction_of_area)
                mechanical_props.cyclic_yield_strength = validated_mechanical_props.get('cyclic_yield_strength',
                                                                                        mechanical_props.cyclic_yield_strength)
                mechanical_props.elastic_modulus = validated_mechanical_props.get('elastic_modulus',
                                                                                  mechanical_props.elastic_modulus)
                mechanical_props.poissons_ratio = validated_mechanical_props.get('poissons_ratio',
                                                                                 mechanical_props.poissons_ratio)
                mechanical_props.shear_modulus = validated_mechanical_props.get('shear_modulus',
                                                                                mechanical_props.shear_modulus)
                mechanical_props.yield_strength = validated_mechanical_props.get('yield_strength',
                                                                                 mechanical_props.yield_strength)
            else:
                mechanical_props = MechanicalProperties.objects.create(material=instance, **validated_mechanical_props)
            mechanical_props.save()
            instance.mechanical_properties = mechanical_props

        instance.save()
        return instance

    class Meta:
        model = Material
        fields = ['id', 'name', 'category', 'description', 'submitted_by', 'user', 'entry_date', 'source',
                  'designation', 'heat_treatment', 'thermal_properties', 'mechanical_properties', 'physical_properties',
                  'tests', 'upper_category', 'middle_category', 'lower_category', "upper_category_id",
                  "middle_category_id"]


class UserSerializer(serializers.ModelSerializer):
    materials = serializers.PrimaryKeyRelatedField(many=True, queryset=Material.objects.all())
    tests = serializers.PrimaryKeyRelatedField(many=True, queryset=Test.objects.all())

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'email', 'materials', 'tests']


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=User.objects.all())])
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    institution = serializers.IntegerField(required=False)

    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'first_name', 'last_name', 'institution')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'institution': {'required': False},
        }

    def validate_institution(self, value):
        institution = Institution.objects.filter(pk=value).first()
        if not institution:
            raise ValidationError("Given Institution does not exist.")
        return institution

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        if "institution" in validated_data:
            institution_user = InstitutionUser(
                user=user,
                institution=validated_data.get('institution', None))
            institution_user.save()
        return user



class Category3Serializer(serializers.ModelSerializer):
    materials = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    middle_category = serializers.PrimaryKeyRelatedField(many=False, read_only=False,
                                                         queryset=MaterialCategory2.objects.all())
    upper_category = serializers.ReadOnlyField(source="middle_category.upper_category.id")
    upper_name = serializers.ReadOnlyField(source="middle_category.upper_category.category")
    middle_name = serializers.ReadOnlyField(source="middle_category.category")

    class Meta:
        model = MaterialCategory3
        fields = ['id', 'category', 'middle_category', 'middle_name', 'upper_category', 'upper_name', 'materials']


class Category2Serializer(serializers.ModelSerializer):
    lower_categories = Category3Serializer(read_only=True, many=True)
    upper_category = serializers.PrimaryKeyRelatedField(many=False, read_only=False,
                                                        queryset=MaterialCategory1.objects.all())
    upper_name = serializers.ReadOnlyField(source="upper_category.category")

    class Meta:
        model = MaterialCategory2
        fields = ['id', 'category', 'upper_category', 'upper_name', 'lower_categories']


class Category1Serializer(serializers.ModelSerializer):
    mid_categories = Category2Serializer(read_only=True, many=True)

    class Meta:
        model = MaterialCategory1
        fields = ['id', 'category', 'mid_categories']


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        exclude = ['supplier', 'id']


class LaboratorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Laboratory
        fields = '__all__'


class SupplierSerializer(serializers.ModelSerializer):
    locations = LocationSerializer(many=True, required=False, source="supplier_locations")

    class Meta:
        model = Supplier
        fields = '__all__'

    def create(self, validated_data):
        try:
            locations = validated_data.pop("supplier_locations")
        except KeyError:
            locations = None

        supplier = Supplier(**validated_data)

        objs = []
        if locations:
            for location in locations:
                location_obj = Location(supplier=supplier, **location)
                objs.append(location_obj)

        supplier.save()
        for location in objs:
            location.save()

        return supplier

    def update(self, instance: Supplier, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.material_types = validated_data.get("material_types", instance.material_types)
        instance.country = validated_data.get("country", instance.country)
        instance.about = validated_data.get("about", instance.about)
        instance.applications = validated_data.get("applications", instance.applications)
        instance.headquarters = validated_data.get("headquarters", instance.headquarters)
        instance.website = validated_data.get("website", instance.website)
        instance.year_founded = validated_data.get("year_founded", instance.year_founded)
        instance.type = validated_data.get("type", instance.type)
        instance.patents = validated_data.get("patents", instance.patents)
        instance.industries = validated_data.get("industries", instance.industries)
        instance.processing_capabilities = validated_data.get("processing_capabilities",
                                                              instance.processing_capabilities)
        instance.quality_certifications = validated_data.get("quality_certifications", instance.quality_certifications)
        instance.certifications = validated_data.get("certifications", instance.certifications)
        instance.extra_services = validated_data.get("extra_services", instance.extra_services)

        validated_locations = validated_data.get('supplier_locations', [])
        if validated_locations:
            instance.supplier_locations.all().delete()
            locations = []
            for location in validated_locations:
                location_obj = Location(supplier=instance, **location)
                locations.append(location_obj)

        instance.save()
        for location in locations:
            location.save()

        return instance


class InstitutionSerializer(serializers.ModelSerializer):
    users = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Institution
        fields = '__all__'


class InstitutionUserSerializer(serializers.ModelSerializer):
    institution = serializers.PrimaryKeyRelatedField(many=False, read_only=False, queryset=Institution.objects.all())
    user = serializers.PrimaryKeyRelatedField(many=False, read_only=False, queryset=User.objects.all())

    class Meta:
        model = InstitutionUser
        fields = '__all__'  # ['id', 'username', 'email', 'first_name', 'last_name', 'institution']

