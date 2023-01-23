from API import *

# superuser must be created as indicated in README.md
username_staff = "afonso"
password_staff = "1234"

# Create some users

username_teresa = "teresa123"
password_teresa = "aseret321_"
first_name = "Teresa"
last_name = "Matos"
email = "teresa@example.pt"

x = register_user(username_teresa, password_teresa, first_name, last_name, email)
print(f"Register Teresa: {x.status_code}")

username_bob = "Bob123"
password_bob = "Bobby321_"
first_name = "Bob"
last_name = "Bobby"
email = "bob@example.pt"

x = register_user(username_bob, password_bob, first_name, last_name, email)
print(f"Register Bob: {x.status_code}")

# Get user list (should have 3 users)

print(get_user_list(username_staff,password_staff)['results'])

# Create come categories as superuser

# Upper
x = create_upper_category(username_staff, password_staff, "Metal")
print(f"Create upper category Metal: {x.status_code}")

x = create_upper_category(username_staff, password_staff, "Glass")
print(f"Create upper category Glass: {x.status_code}")

x = create_upper_category(username_staff, password_staff, "Other")
print(f"Create upper category Other: {x.status_code}")

# Middle
x = create_middle_category(username_staff, password_staff, "Metal", "Steel")
print(f"Create middle category Metal->Steel: {x.status_code}")



