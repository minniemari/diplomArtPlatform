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
admin.site.register(OrderCancellation)
admin.site.register(UserResponse)
admin.site.register(BonusOption)
admin.site.register(Option)
admin.site.register(Chat)
admin.site.register(Message)
admin.site.register(DisputeChat)
admin.site.register(DisputeMessage)
