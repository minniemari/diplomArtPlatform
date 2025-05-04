from django.contrib import admin
from django.contrib.auth.models import User
from .models import *

admin.site.register(Profile)
admin.site.register(File)
admin.site.register(Skills)
admin.site.register(Portfolio)
admin.site.register(Commission)
admin.site.register(Type)
admin.site.register(Orders)
admin.site.register(Delivers)
admin.site.register(Revisions)
admin.site.register(Birzha)
admin.site.register(UserResponse)
admin.site.register(BonusOption)
admin.site.register(Option)
admin.site.register(Chat)
admin.site.register(Message)
admin.site.register(DisputeMessage)


@admin.register(OrderCancellation)
class OrderCancellationAdmin(admin.ModelAdmin):
    list_display = ('order', 'reason', 'status', 'cancelled_by')
    list_filter = ('status', 'reason')
    readonly_fields = ('order', 'cancelled_by', 'reason', 'other_reason', 'created_at')
    fieldsets = (
        ('Основная информация', {
            'fields': ('order', 'cancelled_by', 'reason', 'other_reason', 'created_at')
        }),
        ('Решение модератора', {
            'fields': ('status',)
        }),
    )

    def save_model(self, request, obj, form, change):
        old_status = obj.order.status  # Получаем старый статус заказа
        super().save_model(request, obj, form, change)

        # Обновляем статус заказа только при изменении заявки
        if change:
            if obj.status == 'accepted':
                obj.order.status = 'cancelled'
                # Уведомления
                Notification.objects.create(
                    user=obj.order.customer,
                    message=f"Заявка на отмену одобрена. Заказ #{obj.order.id} отменён."
                )
                Notification.objects.create(
                    user=obj.order.artist,
                    message=f"Заявка на отмену одобрена. Заказ #{obj.order.id} отменён."
                )
            elif obj.status == 'rejected':
                obj.order.status = 'in_work'
                obj.order.save()
                # Уведомления
                Notification.objects.create(
                    user=obj.order.customer,
                    message=f"Заявка на отмену отклонена. Заказ #{obj.order.id} продолжается."
                )
                Notification.objects.create(
                    user=obj.order.artist,
                    message=f"Заявка на отмену отклонена. Заказ #{obj.order.id} продолжается."
                )
            obj.order.save()

@admin.register(DisputeChat)
class DisputeChatAdmin(admin.ModelAdmin):
    list_display = ('order', 'moderator', 'status', 'decision')
    list_filter = ('status', 'decision')
    readonly_fields = ('order', 'reason', 'created_at')
    fieldsets = (
        ('Основная информация', {
            'fields': ('order', 'moderator', 'reason', 'created_at')
        }),
        ('Решение модератора', {
            'fields': ('status', 'decision')
        }),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        # Обновление статуса заказа при решении
        if obj.status == 'resolved' and obj.decision:
            order = obj.order
            if obj.decision == 'accept':
                order.status = 'in_work'
            elif obj.decision == 'reject':
                order.status = 'accepted'
            order.save()

            # Уведомления участникам
            try:
                Notification.objects.create(
                    user=order.customer,
                    message=f"Модератор решил спор по заказу #{order.id}: {obj.get_decision_display()}"
                )
                Notification.objects.create(
                    user=order.artist,
                    message=f"Модератор решил спор по заказу #{order.id}: {obj.get_decision_display()}"
                )
            except Exception as e:
                pass  # Обработка ошибок уведомлений (опционально)

    def get_decision_display(self, obj):
        return obj.get_decision_display()

    get_decision_display.short_description = 'Решение'