from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('products/', views.product_list, name='product_list'),
    path('category/<slug:category_slug>/', views.product_list, name='category_detail'),
    path('product/<slug:category_slug>/<slug:product_slug>/', views.product_detail, name='product_detail'),
    path('product/create/', views.product_create, name='product_create'),
    path('product/update/<int:pk>/', views.product_update, name='product_update'),
    path('cart/', views.cart_view, name='cart'),
    path('order/', views.order_create, name='order_create'),
    path('order/success/<int:order_id>/', views.order_success, name='order_success'),
    path('contacts/', views.contacts, name='contacts'),
]