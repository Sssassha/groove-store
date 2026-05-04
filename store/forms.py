from django import forms
from .models import Product, Order

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'name', 'slug', 'description', 'price', 'old_price', 'stock', 'image', 'is_on_sale']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer_name', 'customer_phone', 'customer_email', 'address', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3}),
        }