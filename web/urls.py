from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('cabinet/', views.cabinet, name='cabinet'),
    path('partner/', views.partner_cabinet, name='partner_cabinet'),
    path('partner/take/<int:ticket_id>/', views.take_ticket, name='take_ticket'),
    path('partner/drop/<int:ticket_id>/', views.drop_ticket, name='drop_ticket'),
    path('partner/complete/<int:ticket_id>/', views.complete_ticket, name='complete_ticket'),
    path('manage/', views.manage_tickets, name='manage_tickets'),
    path('manage/update/<int:ticket_id>/', views.update_ticket_admin, name='update_ticket_admin'),
    path('manage/review/<int:ticket_id>/', views.review_ticket_admin, name='review_ticket_admin'),
]

