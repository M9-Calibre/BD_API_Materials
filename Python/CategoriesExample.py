from API import *

token = authenticate("afonso", "1234") # admin user

cat1 = LowerCategory(MiddleCategory(UpperCategory("Metal"), "Steel"), "Alloy Steel")
cat2 = LowerCategory(cat1.middle, "Another Steel")
cat3 = LowerCategory(MiddleCategory(cat1.middle.upper, "Aluminium"), "Special Aluminium")
cat4 = LowerCategory(MiddleCategory(UpperCategory("Other"), "Other"), "Other")

cat1 = register_category(token, cat1)
cat2 = register_category(token, cat2)
cat3 = register_category(token, cat3)
cat4 = register_category(token, cat4)

categories_tree = get_categories(CategoriesDisplayModes.Tree)

for upper, mid_dict in categories_tree.items():
    print(upper)
    for mid, lower_list in mid_dict.items():
        print("\t",mid)
        for lower in lower_list:
            print("\t\t",lower)

