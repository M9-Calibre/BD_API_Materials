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

    def __str__(self):
        return f"{self.upper_category.upper_category.category}->{self.upper_category.category}->{self.category}"


class ThermalProperties(models.Model):
    thermal_expansion_coef = models.JSONField(null=True)
    specific_heat_capacity = models.JSONField(null=True)
    thermal_conductivity_tp = models.JSONField(null=True)


class MechanicalProperties(models.Model):
    tensile_strength = models.IntegerField(null=True)
    thermal_conductivity_mp = models.DecimalField(null=True, decimal_places=2, max_digits=6)
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
    name = models.CharField(max_length=50)
    tag = models.CharField(max_length=30)
    input = models.CharField(max_length=50)
    output = models.CharField(max_length=50)
    parameters = models.JSONField()


class Test(models.Model):
    submitted_by = models.ForeignKey(User, models.SET_NULL, null=True, related_name='tests')
    material = models.ForeignKey(Material, models.CASCADE, related_name='tests')
    name = models.CharField(max_length=50)
    DIC_params = models.JSONField()

    class Meta:
        unique_together = ('material', 'name')


class MaterialModelParams(models.Model):
    test = models.ForeignKey(Test, models.CASCADE, related_name='params')
    model = models.ForeignKey(Model, models.CASCADE, related_name='params')
    submitted_by = models.ForeignKey(User, models.SET_NULL, null=True, related_name='params')
    params = models.JSONField()

    class Meta:
        unique_together = ("test", "model", "submitted_by")


class DICStage(models.Model):
    test = models.ForeignKey(Test, models.CASCADE, related_name='stages')
    stage_num = models.IntegerField()
    timestamp_def = models.FloatField()
    # ambient_temperature = models.DecimalField(decimal_places=2, max_digits=5, null=True)  # TODO: Where to find in the file
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
