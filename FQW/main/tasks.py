from celery import shared_task
from .models import Orders
from django.utils import timezone

@shared_task
def check_deadlines():
    overdue_orders = Orders.objects.filter(
        deadline__lt=timezone.now().date(),
        status__in=['new', 'discussion', 'in_work']
    )
    for order in overdue_orders:
        order.status = 'cancelled'
        order.save()