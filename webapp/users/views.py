# Python Imports
import base64
import logging

# Django imports
from django.contrib.auth import authenticate
from django.db import transaction
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from statsd.defaults.django import statsd

# Rest framework Imports
from rest_framework import status, generics
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

# Project Imports
from .models import User
from .serializers import UserCreateSerializer, UserUpdateSerializer, LoginSerializer, CreateSwaggerSerializer, \
    LoginSwaggerSerializer
from .utils import response

# To log the messages
logger = logging.getLogger(__name__)

class RegisterUser(generics.CreateAPIView):
    """
    Implements the API for registering a new user.
    No authentication is required to access this API.

    **POST**:
    Creates a new user in the database.

    """
    authentication_classes = []
    permission_classes = []
    serializer_class = UserCreateSerializer

    @swagger_auto_schema(tags=['Public'], operation_summary="Create a new user account",
                         responses={201: openapi.Response("Successful creation of user with the returned user "
                                                          "information", CreateSwaggerSerializer),
                                    400: "If the data provided in the request is invalid",
                                    408: "If a timeout error occurs"})
    def post(self, request, *args, **kwargs):
        try:
            statsd.incr("user_create")
            if User.objects.filter(username=request.data.get("username")).exists():
                return response(False, "Username ID already Exists", status.HTTP_400_BAD_REQUEST)
            user = self.get_serializer(data=request.data)
            if user.is_valid():
                logger.info("Saving user data")
                with transaction.atomic():
                    user.save()
                return_data = User.objects.filter(username=request.data.get("username")) \
                    .values("id", "first_name", "last_name", "username", "account_created", "account_updated").first()
                return response(True, "User Created Successfully", status.HTTP_201_CREATED, return_data, log_level="info")
            return response(False, user.errors, status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return response(False, str(e), status.HTTP_408_REQUEST_TIMEOUT)


class Login(generics.GenericAPIView):
    """
    Login API view.
    This class implements the logic for user login.

    **Returns**:
        response with authentication token and user data.

    """

    serializer_class = LoginSerializer
    authentication_classes = []
    permission_classes = []

    @staticmethod
    @swagger_auto_schema(tags=['Public'], operation_summary="Login User",
                         responses={200: openapi.Response("Successful login", LoginSwaggerSerializer),
                                    400: "If the data provided in the request is invalid",
                                    401: "If the User is unauthorized to login",
                                    408: "If a timeout error occurs"}
                         )
    def post(request, *args, **kwargs):
        try:
            statsd.incr("login")
            # check if the request contains necessary data
            if not request.data.get("username", None) or not request.data.get("password", None):
                return response(False, "Please provide login credentials", status.HTTP_400_BAD_REQUEST)

            # authenticate the user using provided credentials
            user = authenticate(request, username=request.data.get("username"), password=request.data.get("password"))
            if user is not None:

                # get user details
                user_details = User.objects.get(username=user.get_username())

                # generate token
                token = base64.b64encode(
                    f'{request.data.get("username")}:{request.data.get("password")}'.encode()).decode()

                # return response with token and user data
                return response(True, "Login Successful", status.HTTP_200_OK, data={
                    "first_name": user_details.first_name,
                    "last_name": user_details.last_name,
                    "username": user_details.username,
                    "access-token": token
                }, headers={
                    "access-token": token
                }, log_level="info")

            # return error if authentication fails
            return response(False, "Invalid Credentials", status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return response(False, str(e), status.HTTP_408_REQUEST_TIMEOUT)


class Users(generics.GenericAPIView):
    """
    User API

    This API is used to get and update the details of the user.

    - To get the details of the user with need the basic token in header which can be generated by login API.
    - To update the details of the user with need the basic token in header which can be generated by login API.
    """

    serializer_class = UserUpdateSerializer
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    @staticmethod
    @swagger_auto_schema(tags=['Authenticated'], operation_summary="Get User Account Information",
                         responses={200: openapi.Response("Fetched user data successfully", CreateSwaggerSerializer),
                                    404: "User not found in the system",
                                    403: "Not authorized to access other user's data",
                                    408: "If a timeout error occurs"}
                         )
    def get(request, *args, **kwargs):
        """
        Get the details of the user with the basic token in header which can be generated by login API and User id as
         parameter
        """

        try:
            statsd.incr("user_get")
            if not User.objects.filter(id=kwargs['userId']).exists():
                return response(False, "User {} does not exist".format(kwargs['userId']), status.HTTP_404_NOT_FOUND)

            if not kwargs['userId'] == request.user.id:
                return response(False, "You are not allowed to get this user", status.HTTP_403_FORBIDDEN)

            user_data = User.objects.filter(id=request.user.id).values("id", "first_name", "last_name", "username",
                                                                       "account_created", "account_updated")

            return response(True, "User data fetched successfully", status.HTTP_200_OK, data=user_data.first(), log_level="info")
        except Exception as e:
            return response(False, str(e), status.HTTP_408_REQUEST_TIMEOUT)

    @staticmethod
    @swagger_auto_schema(tags=['Authenticated'], operation_summary="Update User's account information",
                         responses={200: openapi.Response("Updated user data successfully", CreateSwaggerSerializer),
                                    404: "User not found in the system",
                                    403: "Not authorized to access other user's data",
                                    408: "If a timeout error occurs",
                                    400: "Bad Request"}
                         )
    def put(request, *args, **kwargs):
        """
        Update the details of the user with need the basic token in header which can be generated by login API
        and User id as parameter
        """

        try:
            statsd.incr("user_update")
            if not User.objects.filter(id=kwargs['userId']).exists():
                return response(False, "User {} does not exist".format(kwargs['userId']), status.HTTP_404_NOT_FOUND)

            if not kwargs['userId'] == request.user.id:
                return response(False, "You are not allowed to change this user's data", status.HTTP_403_FORBIDDEN)

            if not request.data:
                return response(False, "No data to update", status.HTTP_400_BAD_REQUEST)

            user = UserUpdateSerializer(request.user, data=request.data, partial=True)
            if user.is_valid(raise_exception=True):
                with transaction.atomic():
                    user.save()
                return response(True, "User Updated Successfully", status.HTTP_204_NO_CONTENT, show_data=True, log_level="info")
        except Exception as e:
            return response(False, str(e), status.HTTP_400_BAD_REQUEST)


class Health(APIView):
    """
    Health check API

    This API is used to check the health of the server and returns a success message and 200 status code if the server is running.

    ---

    **GET** - `/healthz/`

    **Returns**:
        `HTTP 200`: Health check successful
    """
    authentication_classes = []
    permission_classes = []

    @staticmethod
    @swagger_auto_schema(tags=['Unauthenticated'], operation_summary="Health endpoint",
                         responses={200: 'server responds with 200 OK if it is healhty.'})
    def get(request, *args, **kwargs):
        statsd.incr("Healthz")
        return response(True, "Health check successful", status.HTTP_200_OK, log_level="info")
