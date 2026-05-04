from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Product, Category, CartItem, Order, OrderItem
from .forms import ProductForm, OrderForm
from django.urls import reverse

def index(request):
    """Главная страница"""
    products_on_sale = Product.objects.filter(is_on_sale=True)[:4]
    new_products = Product.objects.all().order_by('-created_at')[:4]
    categories = Category.objects.all()
    
    context = {
        'products_on_sale': products_on_sale,
        'new_products': new_products,
        'categories': categories,
    }
    return render(request, 'store/index.html', context)

def product_list(request, category_slug=None):
    """Список товаров"""
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=category)
    else:
        category = None
        products = Product.objects.all()
    
    categories = Category.objects.all()
    
    context = {
        'products': products,
        'category': category,
        'categories': categories,
    }
    return render(request, 'store/product_list.html', context)

def product_detail(request, category_slug, product_slug):
    """Просмотр товара"""
    product = get_object_or_404(Product, slug=product_slug, category__slug=category_slug)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart_item, created = CartItem.objects.get_or_create(
            product=product,
            session_key=request.session.session_key or request.session.create(),
            defaults={'quantity': quantity}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        messages.success(request, f'{product.name} добавлен в корзину!')
        return redirect('cart')
    
    return render(request, 'store/product_detail.html', {'product': product})

def product_create(request):
    """Добавление товара (админ-панель)"""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, 'Товар успешно добавлен!')
            return redirect('product_detail', category_slug=product.category.slug, product_slug=product.slug)
    else:
        form = ProductForm()
    
    return render(request, 'store/product_form.html', {'form': form, 'title': 'Добавить товар'})

def product_update(request, pk):
    """Редактирование товара"""
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Товар обновлён!')
            return redirect('product_detail', category_slug=product.category.slug, product_slug=product.slug)
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'store/product_form.html', {'form': form, 'title': 'Редактировать товар'})

def cart_view(request):
    """Корзина"""
    session_key = request.session.session_key or request.session.create()
    cart_items = CartItem.objects.filter(session_key=session_key)
    total = sum(item.get_total_price() for item in cart_items)
    
    if request.method == 'POST':
        item_id = request.POST.get('remove_item')
        if item_id:
            CartItem.objects.filter(id=item_id, session_key=session_key).delete()
            messages.success(request, 'Товар удалён из корзины')
            return redirect('cart')
    
    context = {
        'cart_items': cart_items,
        'total': total,
    }
    return render(request, 'store/cart.html', context)

def order_create(request):
    """Оформление заказа"""
    session_key = request.session.session_key or request.session.create()
    cart_items = CartItem.objects.filter(session_key=session_key)
    
    if not cart_items:
        messages.warning(request, 'Корзина пуста')
        return redirect('product_list')
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save()
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
            cart_items.delete()
            messages.success(request, f'Заказ #{order.id} оформлен!')
            return redirect('order_success', order_id=order.id)
    else:
        form = OrderForm()
    
    total = sum(item.get_total_price() for item in cart_items)
    
    context = {
        'form': form,
        'cart_items': cart_items,
        'total': total,
    }
    return render(request, 'store/order_form.html', context)

def order_success(request, order_id):
    """Страница успешного заказа"""
    order = get_object_or_404(Order, pk=order_id)
    return render(request, 'store/order_success.html', {'order': order})

def contacts(request):
    """Страница контактов"""
    return render(request, 'store/contacts.html')