# Django imports
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

# Rest framework imports
from rest_framework import generics
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated


class ProductView(generics.GenericAPIView):
    """
    Implements the API for performing Operations on Product model.
    """
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    # @swagger_auto_schema(tags=['Authenticated'], operation_summary="Create a new product",
    #                      responses={201: openapi.Response("Successful creation of user with the returned user "
    #                                                       "information"),
    #                                 400: "If the data provided in the request is invalid",
    #                                 408: "If a timeout error occurs"})
    def post(self, request, *args, **kwargs):
        try:
            if User.objects.filter(email=request.data.get("email")).exists():
                return response(False, "Email ID already Exists", status.HTTP_400_BAD_REQUEST)
            user = self.get_serializer(data=request.data)
            if user.is_valid():
                with transaction.atomic():
                    user.save()
                return_data = User.objects.filter(email=request.data.get("email")) \
                    .values("id", "first_name", "last_name", "email", "account_created", "account_updated").first()
                return response(True, "User Created Successfully", status.HTTP_201_CREATED, return_data)
            return response(False, user.errors, status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return response(False, str(e), status.HTTP_408_REQUEST_TIMEOUT)
