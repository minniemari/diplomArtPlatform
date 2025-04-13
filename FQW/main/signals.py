from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile
import threading
from django.utils import timezone
from datetime import timedelta
from .models import UserResponse


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
