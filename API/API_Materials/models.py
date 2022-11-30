from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class MaterialCategory1(models.Model):
    category = models.CharField(max_length=25, unique=True, primary_key=True)


class MaterialCategory2(models.Model):
    upper_category = models.ForeignKey(MaterialCategory1, models.CASCADE)
    sub_category = models.CharField(max_length=25, unique=True, primary_key=True)


class MaterialCategory3(models.Model):
    upper_category = models.ForeignKey(MaterialCategory2, models.CASCADE)
    sub_category = models.CharField(max_length=25, unique=True, primary_key=True)


class ThermalProperties(models.Model):
    thermal_expansion_coef = models.JSONField()
    specific_heat_capacity = models.JSONField()
    thermal_conductivity = models.JSONField()


class MechanicalProperties(models.Model):
    tensile_strength = models.IntegerField(null=True)
    thermal_conductivity = models.DecimalField(null=True, decimal_places=2, max_digits=6)
    reduction_of_area = models.DecimalField(null=True, decimal_places=2, max_digits=5)  # percentage
    cyclic_yield_strength = models.IntegerField(null=True)
    elastic_modulus = models.JSONField()
    poissons_ratio = models.JSONField()
    shear_modulus = models.JSONField()
    yield_strength = models.JSONField()


class PhysicalProperties(models.Model):
    chemical_composition = models.JSONField()


class Material(models.Model):
    name = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey(MaterialCategory3, models.CASCADE)
    description = models.TextField(null=True, blank=True)
    submitted_by = models.ForeignKey(User, models.SET_NULL, null=True)
    mat_id = models.IntegerField(unique=True)
    entry_date = models.DateField()  # TODO is this date created? If so add auto_now_add = True
    source = models.CharField(max_length=50)
    designation = models.CharField(max_length=25)
    heat_treatment = models.CharField(max_length=50)
    thermal_properties = models.OneToOneField(ThermalProperties, models.CASCADE)
    mechanical_properties = models.OneToOneField(MechanicalProperties, models.CASCADE)
    physical_properties = models.OneToOneField(PhysicalProperties, models.CASCADE)


class Model(models.Model):
    material = models.ForeignKey(Material, models.CASCADE)
    name = models.CharField(max_length=50)
    equation = models.CharField(max_length=50)
    parameters = models.JSONField()
    parametersKPI = models.JSONField()
    model_file = models.FileField()


class Test(models.Model):
    user = models.ForeignKey(User, models.SET_NULL, null=True)
    material = models.ForeignKey(Material, models.CASCADE)
    name = models.CharField(max_length=50)
    DIC_params = models.JSONField()
    thermog_params = models.JSONField(null=True)


class DICStage(models.Model):
    test = models.ForeignKey(Test, models.CASCADE)
    stage_num = models.IntegerField()
    timestamp_undef = models.DecimalField(decimal_places=6, max_digits=10)  # maybe not needed
    timestamp_def = models.DecimalField(decimal_places=6, max_digits=10)
    ambient_temperature = models.DecimalField(decimal_places=2, max_digits=5)
    load = models.DecimalField(decimal_places=2, max_digits=5)  # TODO check digits for this
    # TODO AD-Channels ?


class DICDatapoint(models.Model):
    stage = models.ForeignKey(DICStage, models.CASCADE)
    index_x = models.IntegerField()
    index_y = models.IntegerField()
    x = models.DecimalField(decimal_places=6, max_digits=8)
    y = models.DecimalField(decimal_places=6, max_digits=8)
    z = models.DecimalField(decimal_places=6, max_digits=8)
    displacement_x = models.DecimalField(decimal_places=6, max_digits=8)
    displacement_y = models.DecimalField(decimal_places=6, max_digits=8)
    displacement_z = models.DecimalField(decimal_places=6, max_digits=8)
    strain_x = models.DecimalField(decimal_places=6, max_digits=8, null=True)
    strain_y = models.DecimalField(decimal_places=6, max_digits=8, null=True)
    strain_major = models.DecimalField(decimal_places=6, max_digits=8, null=True)
    strain_minor = models.DecimalField(decimal_places=6, max_digits=8, null=True)
    thickness_reduction = models.DecimalField(decimal_places=6, max_digits=8, null=True)


# TODO thermog


class Entity(models.Model):
    material_types = models.CharField(max_length=100, null=True)
    country = models.CharField(max_length=25)
    about = models.TextField()


class Supplier(Entity):
    applications = models.CharField(max_length=100, null=True)
    year_founded = models.IntegerField()
    patents = models.CharField(max_length=250)
    certifications = models.CharField(max_length=250)
    # TODO more fields?


class Location(models.Model):
    supplier = models.ForeignKey(Supplier, models.CASCADE)
    number = models.IntegerField()
    postal_code = models.CharField(max_length=25)
    street = models.CharField(max_length=100)


class Laboratory(Entity):
    # TODO
    pass
