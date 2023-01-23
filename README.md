## How to run the API

* Make sure to install the requirements (this must only be done once) (you may create a virtual environment):

``` 
# in the API root (/API)
pip install -r requirements.txt
```

* Turning on API

``` 
python3 manage.py runserver 0.0.0.0:8000
```

* How to restart the db (needed when there are model changes)

``` 
rm -f db.sqlite3 
rm -r API_Materials/migrations/
python3 manage.py makemigrations API_Materials
python3 manage.py migrate
```

* Creating a super-user (or a "staff" user)

``` 
python3 manage.py createsuperuser
# then follow the instructions
```

API Documentation can be found in /swagger or /redoc

