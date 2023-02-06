# Django imports
from django.urls import path

from product.views import (
    ProductCreateView,
    ProductGetView
)

app_name = "product"
urlpatterns = [
    path("", view=ProductCreateView.as_view(), name="product_create"),
    path("<int:id>", view=ProductGetView.as_view(), name="product_get"),
]
