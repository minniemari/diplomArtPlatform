import os
from collections import defaultdict
from django.utils.timezone import now
from django.db import models
from django.contrib.auth.models import User

# Модель профиля
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    specialization = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    ratings = models.FloatField(default=0)
    image = models.ImageField(upload_to='profiles/', blank=True, null = True)
    skills = models.ManyToManyField('Skills')
    commission = models.ManyToManyField('Commission', blank=True)

    def __str__(self):
        return self.user.username

# Модель навыков
class Skills(models.Model):
    name = models.CharField(max_length=255)

# Модель портфолио
class Portfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='portfolio/')
    description = models.TextField()

    def __str__(self):
        return f"Портфолио {self.user.username}"

# Модель коммишки
class Commission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    type = models.ForeignKey('Type', on_delete=models.CASCADE)
    description = models.TextField()
    needsForOrder = models.TextField(default="Не указано")
    options = models.ManyToManyField('Option',blank=True)
    image = models.ImageField(upload_to='commissions/')
    created_at = models.DateTimeField(auto_now_add=True)
    bonus_options = models.ManyToManyField('BonusOption', blank=True)

    @property
    def min_price(self):
        """ Минимальная цена среди всех опций """
        return self.options.aggregate(models.Min('price'))['price__min'] or 0

    @min_price.setter
    def min_price(self, value):
        self._min_price = value

    @property
    def deadline(self):
        """ Минимальный срок среди всех опций """
        return self.options.aggregate(models.Min('deadline'))['deadline__min'] or 0

    def __str__(self):
        return self.title

# Модель типов иллюстраций
class Type(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

# Модель заказов
class Orders(models.Model):
    STATUS_CHOICES = [
        ('new', 'Создан'),
        ('discussion', 'Обсуждение'),
        ('in_work', 'В работе'),
        ('on_review', 'На проверке'),
        ('accepted', 'Принят'),
        ('cancelled', 'Отменён')
    ]

    artist= models.ForeignKey(User, on_delete=models.CASCADE, related_name='artist_orders')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_orders')
    portfolio = models.ForeignKey(Portfolio, on_delete=models.SET_NULL, null=True, blank=True)
    status =  models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    detail = models.ManyToManyField('Option', blank=True)
    deadline = models.DateField(help_text='Дата завершения')
    description = models.TextField()
    files = models.FileField('File', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def update_status(self, new_status):
        """Обновляет статус заказа и фиксирует изменение"""
        if new_status in dict(self.STATUS_CHOICES):
            OrderStatus.objects.create(order=self, status=new_status)
            self.status = new_status
            self.save()
        else:
            raise ValueError("Недопустимый статус")

    def __str__(self):
        return f"Заказ #{self.id} ({self.get_status_display()})"

# Модель доставки заказа
class Delivers(models.Model):
    order = models.ForeignKey(Orders, on_delete=models.CASCADE)
    artist = models.ForeignKey(User, on_delete=models.CASCADE)
    images = models.ManyToManyField('ImageStorage', blank=True)
    files = models.ManyToManyField('File', blank=True)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Доставка для заказа #{self.order.id}"

# Модель отзывов
class Revisions(models.Model):
    delivery = models.ForeignKey(Delivers, on_delete=models.CASCADE)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    images = models.ManyToManyField('ImageStorage', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.FloatField()

    def __str__(self):
        return f"Правка #{self.delivery.id}"

# Модель биржи заказов
class Birzha(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    file = models.FileField(upload_to='bids/', blank=True, null=True)
    type = models.ForeignKey('Type', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    increasedPrice = models.BooleanField(default=False)

    def __str__(self):
        return self.title

# Модель отмены заказа
class OrderCancellation(models.Model):
    order = models.ForeignKey(Orders, on_delete=models.CASCADE)
    cancelled_by = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Отмена заказа #{self.order.id}"

# Модель откликов
class UserResponse(models.Model):
    artist = models.ForeignKey(User, on_delete=models.CASCADE, related_name='responses_as_artist')  # Художник откликается на биржу
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='responses_as_customer')  # Заказчик откликается на коммишку
    birzha = models.ForeignKey(Birzha, on_delete=models.CASCADE, null=True, blank=True)  # Отклик на биржу
    commission = models.ForeignKey(Commission, on_delete=models.CASCADE, null=True, blank=True)  # Отклик на коммишку
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    technical_task = models.TextField(blank=True, null=True)  # Техническое задание
    files = models.ManyToManyField('File', blank=True)  # Возможность прикреплять файлы
    delivery_time = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Проверка, что указано только одно из двух полей: birzha или commission
        if self.birzha and self.commission:
            raise ValueError("Отклик не может быть одновременно на биржу и на коммишку")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Отклик от #{self.user.id}"

# Модель дополнительных опций
class BonusOption(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    deadline = models.IntegerField()

    def __str__(self):
        return self.name

# Модель пакетов
class Option(models.Model):
    PACKAGE_CHOICES = [
        ('BASIC', 'Базовый'),
        ('STANDARD', 'Стандартный'),
        ('PREMIUM', 'Премиум'),
    ]

    package_type = models.CharField(max_length=10, choices=PACKAGE_CHOICES)  # Тип пакета
    description = models.TextField()
    is_sketch = models.BooleanField(default=False)
    for_print = models.BooleanField(default=False)
    difficult_bg = models.BooleanField(default=False)
    full_height = models.BooleanField(default=False)
    details = models.BooleanField(default=False)
    vector = models.BooleanField(default=False)
    psd = models.BooleanField(default=False)
    amount = models.IntegerField()
    deadline = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.get_package_type_display()} - {self.price}₽"

# Модель чата
class Chat(models.Model):
    order = models.ForeignKey(Orders, on_delete=models.CASCADE, null=True, blank=True)
    participants = models.ManyToManyField(User)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Чат для заказа #{self.order.id}"

# Модель сообщений
class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Сообщение от #{self.sender.username}"

# Модель спорного чата
class DisputeChat(models.Model):
    order = models.ForeignKey(Orders, on_delete=models.CASCADE)
    moderator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='moderated_disputes')
    participants = models.ManyToManyField(User, related_name='dispute_chats')
    created_at = models.DateTimeField(auto_now_add=True)
    reason = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'На рассмотрении'),
            ('resolved', 'Решено'),
            ('rejected', 'Отказано'),
        ],
        default='pending'
    )

    def __str__(self):
        return f"Спорный чат для заказа #{self.order.id}"

# Модель сообщений в спорном чате
class DisputeMessage(models.Model):
    dispute_chat = models.ForeignKey(DisputeChat, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Сообщение в споре от #{self.sender.username}"


#Модель истории изменений статусов заказа
class OrderStatus(models.Model):
    order = models.ForeignKey(Orders, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=20, choices=Orders.STATUS_CHOICES)
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Заказ {self.order.id}: {self.get_status_display()} ({self.changed_at})"

# Модель файлов
class File(models.Model):
    FILE_TYPES = [
        ('image', 'Изображение'),
        ('document', 'Документ'),
        ('other', 'Другое')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='files/')
    file_type = models.CharField(max_length=10, choices=FILE_TYPES, default='other')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def filename(self):
        return os.path.basename(self.file.name)

    def __str__(self):
        return f"{self.filename()} ({self.get_file_type_display()})"

class ImageStorage(models.Model):
    image = models.ImageField(upload_to='images/')