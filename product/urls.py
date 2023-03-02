# Django imports
from django.urls import path

from product.views import (
    ProductCreateView,
    ProductGetView,
    ProductImageGetPostView,
    ProductImageGetDeleteView
)

app_name = "product"
urlpatterns = [
    path("", view=ProductCreateView.as_view(), name="product_create"),
    path("<int:id>", view=ProductGetView.as_view(), name="product_get"),
    path("<int:id>/image", view=ProductImageGetPostView.as_view(), name="image_create"),
    path("<int:id>/image/<int:image_id>", view=ProductImageGetDeleteView.as_view(), name="image_get"),
]
