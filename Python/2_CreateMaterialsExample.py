from VxFormsAPI.VxFormsAPI.API import *

token = authenticate("tester", "secretPass1234")

# Creating a material

thermal_expansion_coef = {
    "20": 1.15,
    "200": 1.27,
    "300": 1.32
}

specific_heat_capacity = {
    "20": 430,
    "200": 499,
    "300": 517
}

thermal_conductivity = {
    "20": 34.9,
    "200": 38,
    "300": 37.8
}

tp = ThermalProperties(thermal_expansion_coef=thermal_expansion_coef, specific_heat_capacity=specific_heat_capacity, 
                       thermal_conductivity=thermal_conductivity)

elastic_modulus = {
    "-100": 217,
    "20": 214,
    "200": 202,
    "300": 192
}

poissons_ratio = {
    "20": 0.283,
    "200": 0.292,
    "300": 0.294
}

shear_modulus = {
    "20": 82.8,
    "200": 77.9,
    "300": 74.9
}

yield_strength = {
    "20": 280,
    "200": 224,
    "300": 221
}

mp = MechanicalProperties(tensile_strength=500, thermal_conductivity=46.8, reduction_of_area=41.4, cyclic_yield_strength=250, 
                          elastic_modulus=elastic_modulus, poissons_ratio=poissons_ratio, shear_modulus=shear_modulus,
                          yield_strength=yield_strength)

chemical_composition = {
    "C": 0.105,
    "Si": 0.24,
    "Mn": 0.43,
    "P": 0.012,
    "S": 0.014,
    "Cr": 2.29,
    "Mo": 1.004,
    "Ni": 0.16,
    "Cu": 0.9,
    "Ti": 0.03,
    "V": 0.02,
    "Al": 0.02
}

pp = PhysicalProperties(chemical_composition=chemical_composition)

category = get_category_by_name("Alloy Steel")

material = Material(name="EN 10028-2 Grade 10CrMo9-10 normalized and tempered (+NT)", category=category,
                    source="Boller C, Seeger T. Materials data for cyclic loading, Part B. Amsterdam: Elsevier; 1987",
                    designation="DIN 10 CrMo 9 10", heat_treatment="Normalized & tempered, 950°C/30min air, 750°C/2h air", 
                    thermal_properties=tp, mechanical_properties=mp, physical_properties=pp).register(token)

# Another material

category = get_category_by_name("Other")

material2 = Material("Example Material", category=category, source="The source of the material.",
                     heat_treatment="The heat treatment of the material.", description="Material description.",
                     designation="ABCDEFG").register(token)

# Fetching the stored materials

for material in get_materials():
    print(material.id, material.name, material.submitted_by, material.date, material.user)
