from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import Material, MaterialCategory3, MaterialCategory2, MaterialCategory1, Test, ThermalProperties, \
    MechanicalProperties, PhysicalProperties, Laboratory, Supplier, Location
from django.contrib.auth.models import User


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


class MaterialSerializer(serializers.ModelSerializer):
    submitted_by = serializers.SlugRelatedField(many=False, read_only=True, slug_field='username')
    thermal_properties = ThermalPropsSerializer(many=False, required=False)
    mechanical_properties = MechanicalPropsSerializer(many=False, required=False)
    physical_properties = PhysicalPropsSerializer(many=False, required=False)

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
        instance.mat_id = validated_data.get('mat_id', instance.mat_id)
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
                thermal_props.thermal_conductivity = validated_thermal_props.get('thermal_conductivity',
                                                                                 thermal_props.thermal_conductivity)
                thermal_props.thermal_expansion_coef = validated_thermal_props.get('thermal_expansion_coef',
                                                                                   thermal_props.thermal_expansion_coef)
                thermal_props.specific_heat_capacity = validated_thermal_props.get('specific_heat_capacity',
                                                                                   thermal_props.specific_heat_capacity)
            else:
                thermal_props = ThermalProperties.objects.create(material=instance, **validated_thermal_props)
                instance.thermal_properties = thermal_props

        if validated_physical_props:
            if physical_props:
                physical_props.chemical_composition = validated_physical_props.get('chemical_composition',
                                                                                   physical_props.chemical_composition)
            else:
                physical_props = PhysicalProperties.objects.create(material=instance, **validated_physical_props)
                instance.physical_properties = physical_props

        if validated_mechanical_props:
            if mechanical_props:
                mechanical_props.tensile_strength = validated_mechanical_props.get('tensile_strength',
                                                                                   mechanical_props.tensile_strength)
                mechanical_props.thermal_conductivity = validated_mechanical_props.get('thermal_conductivity',
                                                                                       mechanical_props.thermal_conductivity)
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
                instance.mechanical_properties = mechanical_props

        instance.save()
        return instance

    class Meta:
        model = Material
        fields = ['id', 'name', 'category', 'description', 'submitted_by', 'mat_id', 'entry_date', 'source',
                  'designation', 'heat_treatment', 'thermal_properties', 'mechanical_properties', 'physical_properties']


class UserSerializer(serializers.ModelSerializer):
    materials = serializers.HyperlinkedRelatedField(many=True, queryset=Material.objects.all(),
                                                    view_name='materials-detail')
    tests = serializers.PrimaryKeyRelatedField(many=True, queryset=Test.objects.all())

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'email', 'materials', 'tests']


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=User.objects.all())])
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'first_name', 'last_name')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class Category3Serializer(serializers.ModelSerializer):
    materials = serializers.HyperlinkedRelatedField(many=True, view_name='materials-detail', read_only=True)

    class Meta:
        model = MaterialCategory3
        fields = ['id', 'upper_category', 'category', 'materials']


class Category2Serializer(serializers.ModelSerializer):
    lower_categories = Category3Serializer(read_only=True, many=True)

    class Meta:
        model = MaterialCategory2
        fields = ['upper_category', 'category', 'lower_categories']


class Category1Serializer(serializers.ModelSerializer):
    mid_categories = Category2Serializer(read_only=True, many=True)

    class Meta:
        model = MaterialCategory1
        fields = ['category', 'mid_categories']


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
                print(location_obj.supplier)
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
