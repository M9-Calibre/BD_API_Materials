from API import *

# token = authenticate("afonso", "1234")

# material_list = get_materials()

# category = get_category(1)

# categories_tree = get_categories(CategoriesDisplayModes.Tree)

# for upper, mid_dict in categories_tree.items():
#     print(upper)
#     for mid, lower_list in mid_dict.items():
#         print("\t",mid)
#         for lower in lower_list:
#             print("\t\t",lower)

# categories_lists = get_categories()

# for category in categories_lists["lower"]:
#     print(category)

# poissons_ratio = {
#     "100": 1.23,
#     "200": 3.45
# }

# mec_props = MechanicalProperties(thermal_conductivity=3.4, poissons_ratio=poissons_ratio)

# material = Material("56534", category, 12, "AAA", "AAA", "AAA", description="Example", mechanical_properties=mec_props)

# register_material(token, material)

# for material in material_list:
#     print(material.to_json())

#test = Test()

print(get_material(8).name)


