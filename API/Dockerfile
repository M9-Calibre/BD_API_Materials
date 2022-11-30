# pull the official base image
FROM python:3

# set work directory
WORKDIR /djangoProject

# copy project
COPY . /djangoProject

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip 
RUN pip install -r requirements.txt

# migrate db
# RUN python manage.py migrate auth
# RUN python manage.py migrate

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]