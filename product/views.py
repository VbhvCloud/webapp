# Python imports
from PIL import Image
import boto3
import environ
import json
import logging
import os

# Django imports
from django.db import transaction
from statsd.defaults.django import statsd

# Rest framework imports
from rest_framework import generics, status
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated

# Project imports
from .models import Product, ProductImage
from .serializers import ProductSerializer, ProductUpdateSerializer, ProductImageSerializer
from webapp.users.utils import response

logger = logging.getLogger(__name__)

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
            statsd.incr("product_create")
            # Check if product with the same SKU already exists
            if Product.objects.filter(sku=request.data.get("sku")).exists():
                return response(False, "Product with this SKU {} already exist".format(request.data.get("sku")), status.HTTP_400_BAD_REQUEST)

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
                return response(True, "Product Created Successfully", status.HTTP_201_CREATED, product.data, log_level="info")
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
    http_method_names = ['get', 'patch', 'delete', 'put']
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ProductUpdateSerializer

    def get_permissions(self):
        """
        Returns permission classes based on the request method.
        """
        if self.request.method in ['PATCH', 'DELETE', 'PUT']:
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
            statsd.incr("product_get")
            # Check if the requested Product exists in the database
            if not Product.objects.filter(id=kwargs['id']).exists():
                return response(False, "Product {} does not exist".format(kwargs['id']), status.HTTP_404_NOT_FOUND)

            # Retrieve the Product data from the database
            product_data = Product.objects.filter(id=kwargs['id']).values().first()

            # Return a success response with the Product data
            return response(True, "Product data fetched successfully", status.HTTP_200_OK, data=product_data, log_level="info")
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
            statsd.incr("product_patch")
            # Check if the requested Product exists in the database
            if not Product.objects.filter(id=kwargs['id']).exists():
                return response(False, "Product {} does not exist".format(kwargs['id']), status.HTTP_404_NOT_FOUND)

            if request.data.get("quantity", None) and type(request.data.get("quantity")) is str:
                return response(False, "quantity field cannot be of type string", status.HTTP_400_BAD_REQUEST)

            # Retrieve the Product object from the database
            product = Product.objects.get(id=kwargs['id'])

            # Check if the requesting user is the owner of the Product
            if not product.owner_user == request.user:
                return response(False, "You are not allowed to change this product's data", status.HTTP_403_FORBIDDEN)

            # Check if the request data is empty
            if not request.data:
                return response(False, "No data to update", status.HTTP_400_BAD_REQUEST)

            # Check if the SKU of the Product exists in the request data, and it is different from the current SKU
            # and a Product with the new SKU already exists in the database
            if request.data.get("sku", False) and \
                    request.data['sku'] != product.sku and Product.objects.filter(sku=request.data['sku']).exists():
                return response(False, "Product with this SKU {} already exists".format(request.data['sku']), status.HTTP_400_BAD_REQUEST)

            # Get the serializer with the current product instance and request data
            serializer = self.get_serializer(instance=product, data=request.data, partial=True)

            # Validate the serializer data
            if serializer.is_valid():
                # Save the changes in the database using transaction
                with transaction.atomic():
                    serializer.save()
                return response(True, "Product data updated successfully", status.HTTP_204_NO_CONTENT, show_data=True, log_level="info")
            else:
                return response(False, serializer.errors, status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Return the error message with a timeout status code in case of any unexpected error
            return response(False, str(e), status.HTTP_408_REQUEST_TIMEOUT)

    def put(self, request, *args, **kwargs):
        """
        Handle PUT request to update a specific Product.
        Returns a response with success or failure message and relevant HTTP status code.

        :param request: The incoming request
        :param args: Additional positional arguments
        :param kwargs: Additional keyword arguments, including the `id` of the Product to update
        :return: A response object with success or failure message and relevant HTTP status code
        """
        try:
            statsd.incr("product_update")
            # Check if the requested Product exists in the database
            if not Product.objects.filter(id=kwargs['id']).exists():
                return response(False, "Product {} does not exist".format(kwargs['id']), status.HTTP_404_NOT_FOUND)

            if request.data.get("quantity", None) and type(request.data.get("quantity")) is str:
                return response(False, "quantity field cannot be of type string", status.HTTP_400_BAD_REQUEST)

            # Retrieve the Product object from the database
            product = Product.objects.get(id=kwargs['id'])

            # Check if the requesting user is the owner of the Product
            if not product.owner_user == request.user:
                return response(False, "You are not allowed to change this product's data", status.HTTP_403_FORBIDDEN)

            # Check if the request data is empty
            if not request.data:
                return response(False, "No data to update", status.HTTP_400_BAD_REQUEST)

            # Check if the SKU of the Product exists in the request data and it is different from the current SKU
            # and a Product with the new SKU already exists in the database
            if request.data.get("sku", False) and \
                    request.data['sku'] != product.sku and Product.objects.filter(sku=request.data['sku']).exists():
                return response(False, "Product with this SKU {} already exists".format(request.data['sku']), status.HTTP_400_BAD_REQUEST)

            # Get the serializer with the current product instance and request data
            serializer = self.get_serializer(instance=product, data=request.data)

            # Validate the serializer data
            if serializer.is_valid():
                # Save the changes in the database using transaction
                logger.info("Updating Product Data")
                with transaction.atomic():
                    serializer.save()
                return response(True, "Product data updated successfully", status.HTTP_204_NO_CONTENT, show_data=True, log_level="info")
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
            statsd.incr("product_delete")
            # Check if the requested Product exists in the database
            if not Product.objects.filter(id=kwargs['id']).exists():
                return response(False, "Product {} does not exist".format(kwargs['id']), status.HTTP_404_NOT_FOUND)

            # Retrieve the Product object from the database
            product = Product.objects.get(id=kwargs['id'])

            # Check if the requesting user is the owner of the Product
            if not product.owner_user == request.user:
                return response(False, "You are not allowed to delete this product's data", status.HTTP_403_FORBIDDEN)
            
            # Deleting images related to product
            # Extract the object keys
            keys = [obj['s3_bucket_path'] for obj in ProductImage.objects.filter(product=product).values("s3_bucket_path")]

            # Delete the objects in batches of up to 1000
            batches = [keys[i:i+1000] for i in range(0, len(keys), 1000)]
            use_profile = environ.Env().bool("USE_PROFILE", default=False)

            
            try:
                s3 = boto3.Session(profile_name='dev').client('s3') if use_profile else boto3.client("s3")
                logger.error("Deleting all images from s3 realted to the image")
                for batch in batches:
                    delete_params = {'Bucket': environ.Env().str("S3_BUCKET"), 'Delete': {'Objects': [{'Key': obj_key} for obj_key in batch]}}
                    s3.delete_objects(**delete_params)
            except Exception as e:
                logger.error("Couldn't delete Images from S3, deleteing product only : {}".format(str(e)))


            # Delete the Product from the database
            logger.info("Deleting product")
            product.delete()

            # Return success message and relevant HTTP status code
            return response(True, "Product deleted successfully", status.HTTP_204_NO_CONTENT, show_data=True, log_level="info")
        except Exception as e:
            # Return failure message and relevant HTTP status code in case of an error
            return response(False, str(e), status.HTTP_408_REQUEST_TIMEOUT)


class ProductImageGetDeleteView(generics.RetrieveDestroyAPIView):
    """
    View for retrieving and deleting a Product's Image.
    Uses BasicAuthentication for authentication and
    requires the user to be authenticated.
    Uses ProductUpdateSerializer for updating a Product.
    """
    http_method_names = ['get', 'delete']
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ProductImageSerializer

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
            statsd.incr("image_get")
            # Check if the requested Product exists in the database
            if not Product.objects.filter(id=kwargs['id']).exists():
                return response(False, "Product {} does not exist".format(kwargs['id']), status.HTTP_404_NOT_FOUND)

            # Retrieve the Product data from the database
            product = Product.objects.get(id=kwargs['id'])

            if not ProductImage.objects.filter(image_id=kwargs['image_id'], product=product).exists():
                return response(False, "Image id associated with this product does not exist",
                                status.HTTP_404_NOT_FOUND)

            # Check if the requesting user is the owner of the Product
            if not product.owner_user == request.user:
                return response(False, "You are not allowed to get this product's data", status.HTTP_403_FORBIDDEN)

            image_data = ProductImage.objects.filter(image_id=kwargs['image_id']).values().first()

            # Return a success response with the Image data
            return response(True, "Image data fetched successfully", status.HTTP_200_OK, data=image_data, log_level="info")
        except Exception as e:
            # Return a failure response with the error message in case of an exception
            return response(False, str(e), status.HTTP_408_REQUEST_TIMEOUT)

    def delete(self, request, *args, **kwargs):
        """
        Handle DELETE request to delete a specific Product's Image.
        Returns a response with success or failure message and relevant HTTP status code.

        :param request: The incoming request
        :param args: Additional positional arguments
        :param kwargs: Additional keyword arguments, including the `id` of the Product and Image to delete
        :return: A response object with success or failure message and relevant HTTP status code
        """
        try:
            statsd.incr("image_delete")
            # Check if the requested Product exists in the database
            if not Product.objects.filter(id=kwargs['id']).exists():
                return response(False, "Product {} does not exist".format(kwargs['id']), status.HTTP_404_NOT_FOUND)

            # Retrieve the Product object from the database
            product = Product.objects.get(id=kwargs['id'])

            if not ProductImage.objects.filter(image_id=kwargs['image_id'], product=product).exists():
                return response(False, "Image id associated with this product does not exist",
                                status.HTTP_404_NOT_FOUND)

            # Check if the requesting user is the owner of the Product
            if not product.owner_user == request.user:
                return response(False, "You are not allowed to delete this product's data", status.HTTP_403_FORBIDDEN)

            # Retrieve the Image object from the database
            image = ProductImage.objects.get(image_id=kwargs['image_id'])
            use_profile = environ.Env().bool("USE_PROFILE", default=False)

            # Delete the image from s3
            try:
                logger.info("Deleting object from S3")
                s3 = boto3.Session(profile_name='dev').client('s3') if use_profile else boto3.client("s3")
                s3.delete_object(Bucket=environ.Env().str("S3_BUCKET"), Key=image.s3_bucket_path)

            except Exception as e:
                send_to_sns_topic(image.s3_bucket_path, image.file_name, False, str(e), product.owner_user.username)
                return response(False, str(e), status.HTTP_400_BAD_REQUEST)
            
            send_to_sns_topic(image.s3_bucket_path, image.file_name, True, "Image Deleted", product.owner_user.username)

            # Delete the Image from the database
            image.delete()

            # Return success message and relevant HTTP status code
            return response(True, "Image deleted successfully", status.HTTP_204_NO_CONTENT, show_data=True, log_level="info")
        except Exception as e:
            # Return failure message and relevant HTTP status code in case of an error
            return response(False, str(e), status.HTTP_408_REQUEST_TIMEOUT)


class ProductImageGetPostView(generics.ListCreateAPIView):
    """
    View for retrieving and deleting a Product's Image.
    Uses BasicAuthentication for authentication and
    requires the user to be authenticated.
    Uses ProductImageSerializer for updating a Product's Image.
    """
    http_method_names = ['get', 'post']
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ProductImageSerializer

    def list(self, request, *args, **kwargs):
        """
        Handle GET request to retrieve a Product's Image list.
        Returns a response with success or failure message and relevant HTTP status code.

        :param request: The incoming request
        :param args: Additional positional arguments
        :param kwargs: Additional keyword arguments, including the `id` of the Product to retrieve
        :return: A response object with success or failure message and relevant HTTP status code
        """
        try:
            statsd.incr("image_list")
            # Check if the requested Product exists in the database
            if not Product.objects.filter(id=kwargs['id']).exists():
                return response(False, "Product {} does not exist".format(kwargs['id']), status.HTTP_404_NOT_FOUND)

            # Retrieve the Product object from the database
            product = Product.objects.get(id=kwargs['id'])

            # Check if the requesting user is the owner of the Product
            if not product.owner_user == request.user:
                return response(False, "You are not allowed to get this product's data", status.HTTP_403_FORBIDDEN)

            image_data = ProductImage.objects.filter(product=product).values()

            # Return a success response with the Product data
            return response(True, "Product data fetched successfully", status.HTTP_200_OK, data=image_data,
                            show_data=True, log_level="info")
        except Exception as e:
            # Return a failure response with the error message in case of an exception
            return response(False, str(e), status.HTTP_408_REQUEST_TIMEOUT)

    def create(self, request, *args, **kwargs):
        """
        Handle POST request to add a specific Product's Image.
        Returns a response with success or failure message and relevant HTTP status code.

        :param request: The incoming request
        :param args: Additional positional arguments
        :param kwargs: Additional keyword arguments, including the `id` of the Product.
        :return: A response object with success or failure message and relevant HTTP status code
        """
        try:
            statsd.incr("image_create")
            # Check if the requested Product exists in the database
            if not Product.objects.filter(id=kwargs['id']).exists():
                return response(False, "Product {} does not exist".format(kwargs['id']), status.HTTP_404_NOT_FOUND)

            # Retrieve the Product object from the database
            product = Product.objects.get(id=kwargs['id'])

            # Check if the requesting user is the owner of the Product
            if not product.owner_user == request.user:
                return response(False, "You are not allowed to Update this product's data", status.HTTP_403_FORBIDDEN)

            if not request.FILES.get("image", False):
                return response(False, "Please select image as form-data", status.HTTP_400_BAD_REQUEST)

            try:
                file_stream = request.FILES["image"].read()
                Image.open(request.FILES["image"])
            except Exception as e:
                return response(False, "Invalid image : {}".format(str(e)), status.HTTP_400_BAD_REQUEST)

            use_profile = environ.Env().bool("USE_PROFILE", default=False)

            logger.info("Create product and updating bucket path")
            serializer = ProductImage(product=product, file_name=request.FILES["image"].name)
            serializer.save()
            serializer.s3_bucket_path = "{}/{}/{}".format(product.id, serializer.image_id, serializer.file_name)
            serializer.save()
            data = ProductImage.objects.filter(image_id=serializer.image_id).values().first()

            try:
                logger.info("Connecting to S3 to upload file")
                s3 = boto3.Session(profile_name='dev').client('s3') if use_profile else boto3.client("s3")
                s3.put_object(Body=file_stream, Bucket=environ.Env().str("S3_BUCKET"), Key=serializer.s3_bucket_path)

            except Exception as e:
                send_to_sns_topic(serializer.s3_bucket_path, serializer.file_name, False, str(e), product.owner_user.username)
                return response(False, str(e), status.HTTP_400_BAD_REQUEST)
            
            send_to_sns_topic(serializer.s3_bucket_path, serializer.file_name, True, "Image Uploaded", product.owner_user.username)

            # Return success message and relevant HTTP status code
            return response(True, "Image Uploaded successfully", status.HTTP_201_CREATED, data, log_level="info")
        except Exception as e:
            # Return failure message and relevant HTTP status code in case of an error
            return response(False, str(e), status.HTTP_408_REQUEST_TIMEOUT)
        
def send_to_sns_topic(image_path, image_name, status, message, user_email):
    
    aws_region = os.getenv("AWS_REGION")
    sns_topic_arn = os.getenv("SNS_TOPIC_ARN")

    use_profile = environ.Env().bool("USE_PROFILE", default=False)

    # Create an SNS client
    sns_client = boto3.Session(profile_name='dev').client('sns', region_name=aws_region) if use_profile else boto3.client('sns', region_name=aws_region)

    # Message to be sent to the SNS topic
    notification = json.dumps({
        "image_path": image_path,
        "image_name": image_name,
        "status": status,
        "message": message,
        "user_email": user_email
    })

    # Publish the message to the SNS topic
    sns_client.publish(
        TopicArn=sns_topic_arn,
        Message=notification,
        Subject='Image Action',
    )

    logger.info("Message Published")
