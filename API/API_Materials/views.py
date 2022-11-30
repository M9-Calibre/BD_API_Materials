import json

from rest_framework.decorators import api_view
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseForbidden


# Create your views here.
@api_view(['POST'])
def register_user(request):
    request_json = json.loads(request.body.decode())
    print(request_json)
    try:
        username = request_json["username"]
        password = request_json["password"]
        email = request_json["email"]
        first_name = request_json["first_name"]
        last_name = request_json["last_name"]
    except KeyError:
        response = HttpResponseBadRequest()
        response.reason_phrase = "Missing registration parameter."
        return response

    if username in [user.username for user in User.objects.all()]:
        response = HttpResponse()
        response.status_code = 409
        response.reason_phrase = "Username already taken."
        return response

    user = User.objects.create_user(username, email, password)
    user.first_name = first_name
    user.last_name = last_name

    user.save()
    token = Token.objects.create(user=user)
    response = JsonResponse({"token": token.key})
    response.status_code = 200
    response.reason_phrase = "Registration completed successfully."
    return response


@api_view(['GET'])
def login_user(request):
    request_json = json.loads(request.body.decode())
    print(request_json)
    try:
        username = request_json["username"]
        password = request_json["password"]
    except KeyError:
        response = HttpResponseBadRequest()
        response.reason_phrase = "Missing registration parameter."
        return response

    user = authenticate(username=username, password=password)

    if user:
        token = Token.objects.get(user=user)
        response = JsonResponse({"token": token.key})
        response.status_code = 200
        response.reason_phrase = "Login successful."
        return response
    response = HttpResponseForbidden()
    response.reason_phrase = "Wrong credentials."
    return response
