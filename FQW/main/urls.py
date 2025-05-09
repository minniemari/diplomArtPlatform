from django.urls import path,include
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from . import views
from django.conf.urls.static import static
# from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import *

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('', views.home, name='home'),
    path('create-commission/', views.create_commission, name='create_commission'),
    path('commission/<int:pk>/', views.commission_detail, name='commission_detail'),
    path('profile/', views.profile, name='profile'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('create-bid/', views.create_bid, name='create_bid'),
    path('commissions/', views.commissions_catalog, name='commissions_catalog'),
    path('bazaar/', views.bazaar_catalog, name='bazaar_catalog'),
    path('bazaar/<int:bid_id>/offer/', views.offer_service, name='offer_service'),
    path('commission/<int:pk>/order/', views.order_form, name='order_form'),
    path('commission_success/',views.commission_success, name='commission_success'),
    path('toggle-favorite-commission/<int:commission_id>/', views.toggle_favorite_commission, name='toggle_favorite_commission'),
    path('toggle-favorite-artist/<int:artist_id>/', views.toggle_favorite_artist, name='toggle_favorite_artist'),
    path('add-portfolio/', add_portfolio, name='add_portfolio'),
    path('edit-profile/', edit_profile, name='edit_profile'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('order/<int:pk>/', views.order_detail_view, name='order_detail'),
    path('order/<int:pk>/action/', views.order_actions, name='order_actions'),
    path('order/<int:pk>/submit-delivery/', views.submit_delivery, name='submit_delivery'),
    path('order/<int:pk>/leave-review/', views.leave_review, name='leave_review'),
    path('send-message/<int:order_id>/', views.send_message, name='send_message'),
    path('notifications/', views.NotificationListView.as_view(), name='notifications_list'),
    path('order/<int:pk>/start-work/', views.start_work, name='start_work'),
    path('order/<int:pk>/edit-order/', views.edit_order, name='edit_order'),
    path('order/<int:pk>/cancel/', views.cancel_order, name='cancel_order'),
    path('leave_review/<int:pk>/', views.leave_review, name='leave_review'),
    path('order/<int:pk>/request-revisions/', views.request_revisions, name='request_revisions'),
    path('profile/<str:username>/', profile_detail, name='profile_detail'),
    path('handle_revision/<int:pk>/<str:action>/', handle_revision, name='handle_revision'),
    path('dispute/<int:pk>/<str:decision>/', resolve_dispute, name='resolve_dispute'),
    path('dispute/<int:pk>/', views.dispute_chat, name='dispute_chat'),
    path('allNotifications',views.notifications_list, name='notifications_list'),
    path('allFavorites',views.favorites_list, name='favorites_list'),
    path('commission/delete/<int:commission_id>/', delete_commission, name='delete_commission'),
    path('bazaar/delete/<int:bid_id>/', delete_bazaar, name='delete_bazaar'),
    path('portfolio/delete/<int:portfolio_id>/', delete_portfolio, name='delete_portfolio'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
