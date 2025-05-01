from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
import threading
from django.utils import timezone
from datetime import timedelta
from .models import *


# @receiver(post_save, sender=User)
# def create_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)
#
# @receiver(post_save, sender=User)
# def save_profile(sender, instance, **kwargs):
#     instance.profile.save()
@receiver(post_save, sender=UserResponse)
def auto_delete_response(sender, instance, created, **kwargs):
    if created:
        def delete_if_unused():
            from .models import Orders
            try:
                response = UserResponse.objects.get(id=instance.id)
                # Проверка: есть ли заказ на отклик
                if not Orders.objects.filter(response=response).exists():
                    response.delete()
                    print(f"[!] Удалён отклик #{response.id}, не принятый за 7 дней")
            except UserResponse.DoesNotExist:
                pass  # Уже удалён

        delay = 7 * 24 * 60 * 60  # 7 дней в секундах
        threading.Timer(delay, delete_if_unused).start()

@receiver(post_save, sender=Orders)
def order_status_change(sender, instance, **kwargs):
    if instance.status == 'in_work':
        # Отправляем уведомление только, не изменяя данные
        Notification.objects.create(
            user=instance.customer,
            message=f"Художник начал работу над заказом #{instance.id}"
        )

@receiver(post_save, sender=Revisions)
def new_revision(sender, instance, **kwargs):
    Notification.objects.create(
        user=instance.delivery.artist,
        message=f"Заказчик отправил правки к заказу #{instance.delivery.order.id}"
    )

@receiver(post_save, sender=DisputeChat)
def new_dispute(sender, instance, **kwargs):
    participants = instance.participants.all()
    for user in participants:
        Notification.objects.create(
            user=user,
            message=f"Новый спор по заказу #{instance.order.id}"
        )