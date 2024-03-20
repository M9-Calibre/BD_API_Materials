from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Institution(models.Model):
    name = models.CharField(max_length=100, unique=True)
    country = models.CharField(max_length=50)


class InstitutionUser(models.Model):
    institution = models.ForeignKey(Institution, models.CASCADE, related_name='users', blank=True, null=True)
    user = models.OneToOneField(User, models.CASCADE, related_name='institution_user')
    has_active_institution = models.BooleanField(default=False)


class MaterialCategory1(models.Model):
    category = models.CharField(max_length=25, unique=True)


class MaterialCategory2(models.Model):
    upper_category = models.ForeignKey(MaterialCategory1, models.CASCADE, related_name='mid_categories')
    category = models.CharField(max_length=25, unique=True)


class MaterialCategory3(models.Model):
    middle_category = models.ForeignKey(MaterialCategory2, models.CASCADE, related_name='lower_categories')
    category = models.CharField(max_length=25, unique=True)


class ThermalProperties(models.Model):
    thermal_expansion_coef = models.JSONField(null=True)
    specific_heat_capacity = models.JSONField(null=True)
    thermal_conductivity_tp = models.JSONField(null=True)


class MechanicalProperties(models.Model):
    tensile_strength = models.FloatField()
    thermal_conductivity_mp = models.FloatField()
    reduction_of_area = models.FloatField()
    cyclic_yield_strength = models.FloatField()
    elastic_modulus = models.JSONField(null=True)
    poissons_ratio = models.JSONField(null=True)
    shear_modulus = models.JSONField(null=True)
    yield_strength = models.JSONField(null=True)


class PhysicalProperties(models.Model):
    chemical_composition = models.JSONField(null=True)


class Material(models.Model):
    name = models.CharField(max_length=150, unique=True)
    category = models.ForeignKey(MaterialCategory3, models.CASCADE, related_name='materials')
    description = models.TextField(null=True, blank=True)
    submitted_by = models.ForeignKey(User, models.SET_NULL, null=True, related_name='materials')
    entry_date = models.DateField(auto_now_add=True)
    source = models.CharField(max_length=150)
    designation = models.CharField(max_length=50)
    heat_treatment = models.CharField(max_length=150)
    thermal_properties = models.OneToOneField(ThermalProperties, models.CASCADE, null=True)
    mechanical_properties = models.OneToOneField(MechanicalProperties, models.CASCADE, null=True)
    physical_properties = models.OneToOneField(PhysicalProperties, models.CASCADE, null=True)


class Test(models.Model):
    submitted_by = models.ForeignKey(User, models.SET_NULL, null=True, related_name='tests')
    material = models.ForeignKey(Material, models.CASCADE, related_name='tests')
    name = models.CharField(max_length=50)
    DIC_params = models.JSONField()

    class Meta:
        unique_together = ('material', 'name')


class Model(models.Model):
    name = models.CharField(max_length=50)
    tag = models.CharField(max_length=30)
    category = models.CharField(max_length=15)
    function_name = models.CharField(max_length=50)
    input = models.JSONField()

class MaterialParams(models.Model):
    material = models.ForeignKey(Material, models.CASCADE, related_name='params')
    name = models.CharField(max_length=50)
    submitted_by = models.ForeignKey(User, models.SET_NULL, null=True, related_name='material_params')
    # hardening_model_params = models.ForeignKey(ModelParams, models.CASCADE, related_name='hardening_material_params')
    # elastic_model_params = models.ForeignKey(ModelParams, models.CASCADE, related_name='elastic_material_params')
    # yield_model_params = models.ForeignKey(ModelParams, models.CASCADE, related_name='yield_material_params')

class ModelParams(models.Model):
    model = models.ForeignKey(Model, models.CASCADE, related_name='params')
    material_param = models.ForeignKey(MaterialParams, models.CASCADE, related_name='model_params')
    submitted_by = models.ForeignKey(User, models.SET_NULL, null=True, related_name='params')
    params = models.JSONField()  # {"x": 10, "z": 40, "output_do_outro" : 30} // {"input": [12, 1, 3.4], "output":}

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['model', 'material_param'], name='unique_model_params')
        ]

class DICStage(models.Model):
    test = models.ForeignKey(Test, models.CASCADE, related_name='stages')
    stage_num = models.IntegerField()
    timestamp_def = models.FloatField()
    load = models.FloatField()

    class Meta:
        unique_together = ('test', 'stage_num')


class DICDatapoint(models.Model):
    stage = models.ForeignKey(DICStage, models.CASCADE)
    x = models.FloatField()
    y = models.FloatField()
    z = models.FloatField(null=True)
    displacement_x = models.FloatField()
    displacement_y = models.FloatField()
    displacement_z = models.FloatField(null=True)
    strain_x = models.FloatField(null=True)
    strain_y = models.FloatField(null=True)
    strain_xy = models.FloatField(null=True)
    strain_major = models.FloatField(null=True)
    strain_minor = models.FloatField(null=True)
    thickness_reduction = models.FloatField(null=True)

    class Meta:
        unique_together = ('stage', 'x', 'y')


class Entity(models.Model):
    name = models.CharField(max_length=100, unique=True)
    material_types = models.JSONField(null=True)
    country = models.CharField(max_length=50)
    about = models.TextField(null=True)


class Supplier(Entity):
    applications = models.JSONField(null=True)
    headquarters = models.CharField(max_length=100)
    website = models.CharField(max_length=250, null=True)
    year_founded = models.IntegerField()
    type = models.CharField(max_length=50)
    patents = models.TextField(null=True)
    industries = models.CharField(max_length=500)
    processing_capabilities = models.CharField(max_length=500, null=True)
    quality_certifications = models.CharField(max_length=500, null=True)
    certifications = models.CharField(max_length=500, null=True)
    extra_services = models.TextField(null=True)


class Location(models.Model):
    supplier = models.ForeignKey(Supplier, models.CASCADE, related_name="supplier_locations")
    name = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=50)

    class Meta:
        unique_together = ('supplier', 'name')


class Laboratory(Entity):
    # TODO
    pass