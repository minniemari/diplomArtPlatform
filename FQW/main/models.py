import os
from collections import defaultdict
from django.utils.timezone import now, timedelta
from django.db import models
from django.contrib.auth.models import User

# Модель профиля
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    specialization = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    ratings = models.FloatField(default=0)
    image = models.ImageField(upload_to='profiles/', blank=True, null = True, default='default_avatar.png')
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
    commission = models.ForeignKey('Commission', on_delete=models.SET_NULL, null=True, blank=True, related_name='portfolio_works')

    def __str__(self):
        return f"Портфолио {self.user.username}"

# Модель коммишки
class Commission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    type = models.ForeignKey('Type', on_delete=models.CASCADE)
    description = models.TextField()
    needsForOrder = models.TextField(default="Не указано")
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
    response = models.OneToOneField('UserResponse', on_delete=models.SET_NULL, null=True, blank=True)
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
            # OrderStatus.objects.create(order=self, status=new_status)
            self.status = new_status
            self.save()
        else:
            raise ValueError("Недопустимый статус")

    def __str__(self):
        return f"Заказ #{self.id} ({self.get_status_display()})"

    def start_work(self):
        self.status = 'in_work'
        self.save()

    def cancel_by_artist(self):
        self.status = 'cancelled'
        self.save()
        # Логика уведомления заказчика

    def submit_for_review(self, files, comment):
        deliver = Delivers.objects.create(
            order=self,
            artist=self.artist,
            images=files,
            comment=comment
        )
        self.status = 'on_review'
        self.save()

    def accept_order(self):
        self.status = 'accepted'
        self.save()

    def has_active_dispute(self):
        return self.disputechat_set.filter(status='pending').exists()

    def can_cancel(self):
        # Проверяем, есть ли уже 3 заявки на отмену
        return self.ordercancellation_set.count() < 3

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


# Модель доставки заказа
class Delivers(models.Model):
    order = models.ForeignKey(Orders, on_delete=models.CASCADE, related_name='delivers')
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

class Review(models.Model):
    order = models.ForeignKey(Orders, on_delete=models.CASCADE)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    communication_rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    result_rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    recommend_rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    image = models.ImageField(upload_to='reviews/')
    created_at = models.DateTimeField(auto_now_add=True)


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
    ORDER_CANCELLATION_REASONS = [
        ('style', 'Не устраивает стиль'),
        ('tz', 'Не соблюдено ТЗ'),
        ('other', 'Другое'),
    ]
    order = models.ForeignKey(Orders, on_delete=models.CASCADE)
    cancelled_by = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.CharField(max_length=255, choices=ORDER_CANCELLATION_REASONS)
    other_reason = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'На рассмотрении'), ('accepted', 'Принято'), ('rejected', 'Отказано')],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Отмена заказа #{self.order.id}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.status == 'accepted':
            self.order.status = 'cancelled'
            self.order.save()


# Модель дополнительных опций
class BonusOption(models.Model):
    name = models.CharField(verbose_name='Название', max_length=255)
    price = models.DecimalField(verbose_name='Цена', max_digits=10, decimal_places=2)
    description = models.TextField(verbose_name='Описание')
    deadline = models.IntegerField(verbose_name='Срок выполнения (дней)')

    def __str__(self):
        return self.name

# Модель пакетов
class Option(models.Model):
    PACKAGE_CHOICES = [
        ('BASIC', 'Базовый'),
        ('STANDARD', 'Стандартный'),
        ('PREMIUM', 'Премиум'),
    ]
    commission = models.ForeignKey(
        'Commission',
        on_delete=models.CASCADE,
        related_name='options'
    )
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

#Модель откликов
class UserResponse(models.Model):
    # Основные связи
    artist = models.ForeignKey(User, on_delete=models.CASCADE, related_name='responses_as_artist')  # Художник откликается на биржу
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='responses_as_customer')  # Заказчик откликается на коммишку
    birzha = models.ForeignKey('Birzha', on_delete=models.CASCADE, null=True, blank=True)  # Отклик на биржу
    commission = models.ForeignKey('Commission', on_delete=models.CASCADE, null=True, blank=True)  # Отклик на коммишку

    # Поля, заполняемые на страницах offer_service и order_form
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Стоимость
    description = models.TextField(blank=True, null=True)  # Описание
    technical_task = models.TextField(blank=True, null=True)  # Техническое задание
    files = models.ManyToManyField('File', blank=True)  # Прикрепленные файлы
    delivery_time = models.IntegerField()  # Срок выполнения (в днях)

    # Поля для хранения данных о выбранном пакете
    package_type = models.CharField(max_length=10, choices=Option.PACKAGE_CHOICES, blank=True, null=True)  # Тип пакета
    package_description = models.TextField(blank=True, null=True)  # Описание пакета
    package_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Цена пакета
    package_deadline = models.IntegerField(blank=True, null=True)  # Срок выполнения пакета

    # Дополнительные опции
    selected_bonus_options = models.ManyToManyField('BonusOption', blank=True)  # Выбранные дополнительные опции

    # Временные метки
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Проверка, что указано только одно из двух полей: birzha или commission
        if self.birzha and self.commission:
            raise ValueError("Отклик не может быть одновременно на биржу и на коммишку")

        # Установка срока действия отклика (7 дней)
        if not self.created_at:
            self.created_at = now()
            self.expires_at = self.created_at + timedelta(days=7)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Отклик от #{self.artist.id} на {self.birzha or self.commission}"

# Модель чата
class Chat(models.Model):
    order = models.OneToOneField(Orders, on_delete=models.CASCADE, related_name='chat', null=True, blank=True)
    participants = models.ManyToManyField(User)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Чат для заказа #{self.order.id}"

# Модель сообщений
class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    images = models.ManyToManyField('ImageStorage', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Сообщение от #{self.sender.username}"

# Модель спорного чата
class DisputeChat(models.Model):
    order = models.ForeignKey(Orders, on_delete=models.CASCADE)
    moderator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='moderated_disputes',limit_choices_to={'is_superuser': True})
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
    decision = models.CharField(
        max_length=10,
        choices=[
            ('accept', 'Принять сторону заказчика'),
            ('reject', 'Принять сторону художника'),
        ],
        blank=True,
        null=True
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

class FavoriteCommission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_commissions')
    commission = models.ForeignKey(Commission, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

class FavoriteArtist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_artists')
    artist = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorited_by_users')
    created_at = models.DateTimeField(auto_now_add=True)


class Notification(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'  # Добавьте эту строку
    )
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Уведомление для {self.user.username}"

class RevisionRequest(models.Model):
    order = models.ForeignKey(
        Orders,
        on_delete=models.CASCADE,
        related_name='revision_requests'
    )
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)