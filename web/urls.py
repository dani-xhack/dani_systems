from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/<int:post_id>/', views.blog_detail, name='blog_detail'),
    path('privacy/', views.privacy_policy, name='privacy'),
    path('offer/', views.public_offer, name='offer'),
    path('register/', views.register_user, {'role': 'client'}, name='register_client'),
    path('register/partner/', views.register_user, {'role': 'partner'}, name='register_partner'),
    path('cabinet/', views.cabinet, name='cabinet'),
    path('partner/', views.partner_cabinet, name='partner_cabinet'),
    path('partner/take/<int:ticket_id>/', views.take_ticket, name='take_ticket'),
    path('partner/drop/<int:ticket_id>/', views.drop_ticket, name='drop_ticket'),
    path('partner/complete/<int:ticket_id>/', views.complete_ticket, name='complete_ticket'),
    path('manage/', views.manage_tickets, name='manage_tickets'),
    path('manage/update/<int:ticket_id>/', views.update_ticket_admin, name='update_ticket_admin'),
    path('manage/review/<int:ticket_id>/', views.review_ticket_admin, name='review_ticket_admin'),
]

