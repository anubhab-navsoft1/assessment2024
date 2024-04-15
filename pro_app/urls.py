from django.urls import path
from . import views
urlpatterns = [
    path('lists/', views.ProductListCreateAPIView.as_view(), name = 'product lists'),
    path('lists/<uuid:prod_id>/',views.ProductListCreateAPIView.as_view(), name = 'prod update'),
    path('delete/<uuid:prod_id>/',views.DeleteProductView.as_view(), name = 'prod delete')
]