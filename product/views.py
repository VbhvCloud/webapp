# Django imports
from django.db import transaction

# Rest framework imports
from rest_framework import generics, status
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated

# Project imports
from .models import Product
from .serializers import ProductSerializer, ProductUpdateSerializer
from webapp.users.utils import response


class ProductCreateView(generics.CreateAPIView):
    """
    View for creating a new Product.
    Uses BasicAuthentication for authentication and
    requires the user to be authenticated.
    Uses ProductSerializer for serializing and validating data.
    """
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ProductSerializer

    def post(self, request, *args, **kwargs):
        """
        Handles POST request for creating a new Product.
        Returns a response with success or failure message and relevant status code.
        """
        try:
            # Check if product with the same SKU already exists
            if Product.objects.filter(sku=request.data.get("sku")).exists():
                return response(False, "Product with this SKU already exist", status.HTTP_400_BAD_REQUEST)

            if type(request.data.get("quantity")) is str:
                return response(False, "quantity field cannot be of type string", status.HTTP_400_BAD_REQUEST)

            # Add owner_user to request data
            request.data.update({"owner_user": request.user.id})

            # Validate the incoming data using ProductSerializer
            product = self.get_serializer(data=request.data)

            if product.is_valid():
                # Save the product in database in an atomic transaction
                with transaction.atomic():
                    product.save()
                # Return success response with product data
                return response(True, "Product Created Successfully", status.HTTP_201_CREATED, product.data)
            else:
                # Return error response with serializer errors
                return response(False, product.errors, status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Return error response with exception message
            return response(False, str(e), status.HTTP_408_REQUEST_TIMEOUT)


class ProductGetView(generics.RetrieveUpdateDestroyAPIView):
    """
    View for retrieving, updating or deleting a Product.
    Uses BasicAuthentication for authentication and
    requires the user to be authenticated.
    Uses ProductUpdateSerializer for updating a Product.
    """
    http_method_names = ['get', 'patch', 'delete']
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ProductUpdateSerializer

    def get_permissions(self):
        """
        Returns permission classes based on the request method.
        """
        if self.request.method in ['PATCH', 'DELETE']:
            return [permission() for permission in self.permission_classes]
        else:
            return []

    def get(self, request, *args, **kwargs):
        """
        Handle GET request to retrieve a Product.
        Returns a response with success or failure message and relevant HTTP status code.

        :param request: The incoming request
        :param args: Additional positional arguments
        :param kwargs: Additional keyword arguments, including the `id` of the Product to retrieve
        :return: A response object with success or failure message and relevant HTTP status code
        """
        try:
            # Check if the requested Product exists in the database
            if not Product.objects.filter(id=kwargs['id']).exists():
                return response(False, "Product does not exist", status.HTTP_404_NOT_FOUND)

            # Retrieve the Product data from the database
            product_data = Product.objects.filter(id=kwargs['id']).values().first()

            # Return a success response with the Product data
            return response(True, "Product data fetched successfully", status.HTTP_200_OK, data=product_data)
        except Exception as e:
            # Return a failure response with the error message in case of an exception
            return response(False, str(e), status.HTTP_408_REQUEST_TIMEOUT)

    def patch(self, request, *args, **kwargs):
        """
        Handle PATCH request to update a specific Product.
        Returns a response with success or failure message and relevant HTTP status code.

        :param request: The incoming request
        :param args: Additional positional arguments
        :param kwargs: Additional keyword arguments, including the `id` of the Product to update
        :return: A response object with success or failure message and relevant HTTP status code
        """
        try:
            # Check if the requested Product exists in the database
            if not Product.objects.filter(id=kwargs['id']).exists():
                return response(False, "Product does not exist", status.HTTP_404_NOT_FOUND)

            if request.data.get("quantity", None) and type(request.data.get("quantity")) is str:
                return response(False, "quantity field cannot be of type string", status.HTTP_400_BAD_REQUEST)

            # Retrieve the Product object from the database
            product = Product.objects.get(id=kwargs['id'])

            # Check if the requesting user is the owner of the Product
            if not product.owner_user == request.user:
                return response(False, "You are not allowed to change this product's data", status.HTTP_403_FORBIDDEN)

            # Check if the request data is empty
            if not request.data:
                return response(False, "No data to update", status.HTTP_204_NO_CONTENT)

            # Check if the SKU of the Product exists in the request data and it is different from the current SKU
            # and a Product with the new SKU already exists in the database
            if request.data.get("sku", False) and \
                request.data['sku'] != product.sku and \
                Product.objects.filter(sku=request.data['sku']).exists():
                return response(False, "Product with this SKU already exists", status.HTTP_400_BAD_REQUEST)

            # Get the serializer with the current product instance and request data
            serializer = self.get_serializer(instance=product, data=request.data, partial=True)

            # Validate the serializer data
            if serializer.is_valid():
                # Save the changes in the database using transaction
                with transaction.atomic():
                    serializer.save()
                # Retrieve the updated product from the database
                product = Product.objects.filter(sku=serializer.data.get('sku')).values().first()
                return response(True, "Product data updated successfully", status.HTTP_200_OK, data=product)
            else:
                return response(False, serializer.errors, status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Return the error message with a timeout status code in case of any unexpected error
            return response(False, str(e), status.HTTP_408_REQUEST_TIMEOUT)

    def delete(self, request, *args, **kwargs):
        """
        Handle DELETE request to delete a specific Product.
        Returns a response with success or failure message and relevant HTTP status code.

        :param request: The incoming request
        :param args: Additional positional arguments
        :param kwargs: Additional keyword arguments, including the `id` of the Product to delete
        :return: A response object with success or failure message and relevant HTTP status code
        """
        try:
            # Check if the requested Product exists in the database
            if not Product.objects.filter(id=kwargs['id']).exists():
                return response(False, "Product does not exist", status.HTTP_404_NOT_FOUND)

            # Retrieve the Product object from the database
            product = Product.objects.get(id=kwargs['id'])

            # Check if the requesting user is the owner of the Product
            if not product.owner_user == request.user:
                return response(False, "You are not allowed to delete this product's data", status.HTTP_403_FORBIDDEN)

            # Delete the Product from the database
            product.delete()

            # Return success message and relevant HTTP status code
            return response(True, "Product deleted successfully", status.HTTP_204_NO_CONTENT)
        except Exception as e:
            # Return failure message and relevant HTTP status code in case of an error
            return response(False, str(e), status.HTTP_408_REQUEST_TIMEOUT)
