from vxformsapi.vxformsapi.API import *

token = authenticate_from_json("secret_login.json")

# Category creating restricted to admin users, i.e. only credentials with admnistrator priviledges will be able to run these commands

cat1 = LowerCategory(MiddleCategory(UpperCategory("Metal"), "Steel"), "Alloy Steel").register(token)
cat2 = LowerCategory(cat1.middle, "Another Steel").register(token)
cat3 = LowerCategory(MiddleCategory(cat1.middle.upper, "Aluminium"), "Special Aluminium").register(token)
cat4 = LowerCategory(MiddleCategory(UpperCategory("Other"), "Other"), "Other").register(token)
cat5 = LowerCategory(MiddleCategory(cat4.middle.upper, "Middle Example"), "Lower Example").register(token)

# Category fetching is available without any kind of authentication (any user can run this)

categories_tree = get_categories(CategoriesDisplayModes.Tree)

"""
Tree Format
{
    upper_category1: {
        middle_category1: [lower_category1, lower_category2, ...],
        middle_category2: [lower_category3, ...],
        ...
    },
    upper_category2: {
        middle_category3: [lower_category4, ...],
        ...
    },
    ...
}
"""

for upper, mid_dict in categories_tree.items():
    print(upper)
    for mid, lower_list in mid_dict.items():
        print("\t",mid)
        for lower in lower_list:
            print("\t\t",lower)

print("==================================================")

categories_lists = get_categories()
print(f"Lower: {categories_lists['lower']}")
print(f"Middle: {categories_lists['middle']}")
print(f"Upper: {categories_lists['upper']}")



