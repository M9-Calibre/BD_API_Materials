from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class MaterialCategory1(models.Model):
    category = models.CharField(max_length=25, unique=True)


class MaterialCategory2(models.Model):
    upper_category = models.ForeignKey(MaterialCategory1, models.CASCADE, related_name='mid_categories')
    category = models.CharField(max_length=25)

    class Meta:
        unique_together = ('upper_category', 'category')


class MaterialCategory3(models.Model):
    upper_category = models.ForeignKey(MaterialCategory2, models.CASCADE, related_name='lower_categories')
    category = models.CharField(max_length=25, unique=True)

    class Meta:
        unique_together = ('upper_category', 'category')


class ThermalProperties(models.Model):
    thermal_expansion_coef = models.JSONField(null=True)
    specific_heat_capacity = models.JSONField(null=True)
    thermal_conductivity = models.JSONField(null=True)


class MechanicalProperties(models.Model):
    tensile_strength = models.IntegerField(null=True)
    thermal_conductivity = models.DecimalField(null=True, decimal_places=2, max_digits=6)
    reduction_of_area = models.DecimalField(null=True, decimal_places=2, max_digits=5)  # percentage
    cyclic_yield_strength = models.IntegerField(null=True)
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
    mat_id = models.IntegerField(unique=True)
    entry_date = models.DateField(auto_now_add=True)
    source = models.CharField(max_length=150)
    designation = models.CharField(max_length=50)
    heat_treatment = models.CharField(max_length=150)
    thermal_properties = models.OneToOneField(ThermalProperties, models.CASCADE, null=True)
    mechanical_properties = models.OneToOneField(MechanicalProperties, models.CASCADE, null=True)
    physical_properties = models.OneToOneField(PhysicalProperties, models.CASCADE, null=True)


# we keep parameters, the equation
class Model(models.Model):
    material = models.ForeignKey(Material, models.CASCADE)
    name = models.CharField(max_length=50)
    equation = models.CharField(max_length=50)
    parameters = models.JSONField()
    parametersKPI = models.JSONField()
    model_file = models.FileField()


# maybe discretize DIC metadata
class Test(models.Model):
    submitted_by = models.ForeignKey(User, models.SET_NULL, null=True, related_name='tests')
    material = models.ForeignKey(Material, models.CASCADE, related_name='tests')
    name = models.CharField(max_length=50)
    DIC_params = models.JSONField()
    thermog_params = models.JSONField(null=True)

    class Meta:
        unique_together = ('material', 'name')


class DICStage(models.Model):
    test = models.ForeignKey(Test, models.CASCADE)
    stage_num = models.IntegerField()
    timestamp_undef = models.DecimalField(decimal_places=6, max_digits=10)  # maybe not needed
    timestamp_def = models.DecimalField(decimal_places=6, max_digits=10)
    ambient_temperature = models.DecimalField(decimal_places=2, max_digits=5)
    load = models.DecimalField(decimal_places=2, max_digits=5)

    class Meta:
        unique_together = ('test', 'stage_num')


class DICDatapoint(models.Model):
    stage = models.ForeignKey(DICStage, models.CASCADE)
    index_x = models.IntegerField()  # in mm
    index_y = models.IntegerField()  # in mm
    x = models.DecimalField(decimal_places=6, max_digits=8)
    y = models.DecimalField(decimal_places=6, max_digits=8)
    z = models.DecimalField(decimal_places=6, max_digits=8, null=True)
    displacement_x = models.DecimalField(decimal_places=6, max_digits=8)
    displacement_y = models.DecimalField(decimal_places=6, max_digits=8)
    displacement_z = models.DecimalField(decimal_places=6, max_digits=8, null=True)
    strain_x = models.DecimalField(decimal_places=6, max_digits=8, null=True)
    strain_y = models.DecimalField(decimal_places=6, max_digits=8, null=True)
    strain_major = models.DecimalField(decimal_places=6, max_digits=8, null=True)
    strain_minor = models.DecimalField(decimal_places=6, max_digits=8, null=True)
    thickness_reduction = models.DecimalField(decimal_places=6, max_digits=8, null=True)

    class Meta:
        unique_together = ('stage', 'index_x', 'index_y')


class ThermogStage(models.Model):
    test = models.ForeignKey(Test, models.CASCADE)
    stage_num = models.IntegerField()

    class Meta:
        unique_together = ('test', 'stage_num')


class ThermogDatapoint(models.Model):
    stage = models.ForeignKey(ThermogStage, models.CASCADE)
    # TODO


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
