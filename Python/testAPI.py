from API import *
import json

# token = MaterialAPI.authenticate("afonso", "1234")

# material_list = MaterialAPI.get_materials()

categories_tree = get_categories(CategoriesDisplayModes.Tree)

for upper, mid_dict in categories_tree.items():
    print(upper)
    for mid, lower_list in mid_dict.items():
        print("\t",mid)
        for lower in lower_list:
            print("\t\t",lower)

categories_lists = get_categories()

for category in categories_lists["lower"]:
    print(category)

# MaterialAPI.Material("ABCDE", )

# for material in material_list:
#     print(material.to_json())


