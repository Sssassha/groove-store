from django.db import models
from django.urls import reverse

class Category(models.Model):
    """Категория товара (гитары, ударные, клавишные и т.д.)"""
    name = models.CharField(max_length=100, verbose_name='Название категории')
    slug = models.SlugField(unique=True, verbose_name='URL-метка')
    description = models.TextField(blank=True, verbose_name='Описание')
    image = models.ImageField(upload_to='categories/', blank=True, null=True, verbose_name='Изображение')
    
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('category_detail', args=[self.slug])

class Product(models.Model):
    """Товар (музыкальный инструмент)"""
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name='Категория')
    name = models.CharField(max_length=200, verbose_name='Название инструмента')
    slug = models.SlugField(unique=True, verbose_name='URL-метка')
    description = models.TextField(verbose_name='Описание')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    old_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='Старая цена')
    stock = models.PositiveIntegerField(default=0, verbose_name='Количество на складе')
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name='Изображение')
    is_on_sale = models.BooleanField(default=False, verbose_name='Акция')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    
    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])
    
    def get_discount_percent(self):
        """Вычисляет процент скидки"""
        if self.old_price and self.old_price > 0:
            return int((1 - self.price / self.old_price) * 100)
        return 0

class CartItem(models.Model):
    """Товар в корзине"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество')
    session_key = models.CharField(max_length=40, verbose_name='Ключ сессии')
    added_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    
    class Meta:
        verbose_name = 'Товар в корзине'
        verbose_name_plural = 'Товары в корзине'
    
    def get_total_price(self):
        """Общая стоимость товара в корзине"""
        return self.product.price * self.quantity

class Order(models.Model):
    """Заказ"""
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('processing', 'В обработке'),
        ('completed', 'Выполнен'),
        ('cancelled', 'Отменён'),
    ]
    
    customer_name = models.CharField(max_length=100, verbose_name='Имя')
    customer_phone = models.CharField(max_length=20, verbose_name='Телефон')
    customer_email = models.EmailField(verbose_name='Email')
    address = models.TextField(verbose_name='Адрес доставки')
    comment = models.TextField(blank=True, verbose_name='Комментарий к заказу')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name='Статус')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
    
    def __str__(self):
        return f'Заказ #{self.id} - {self.customer_name}'
    
    def get_total_amount(self):
        """Общая сумма заказа"""
        total = sum(item.get_total_price() for item in self.items.all())
        return total

class OrderItem(models.Model):
    """Товар в заказе"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='Заказ')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена на момент покупки')
    
    def get_total_price(self):
        return self.price * self.quantity


