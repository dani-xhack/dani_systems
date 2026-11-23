from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.utils.safestring import mark_safe

admin.site.site_url = '/manage/'
admin.site.site_header = mark_safe(
    'Dani Systems | '
    '<a href="/register/" target="_blank" style="color:#38bdf8;font-size:13px;margin-left:12px;">\U0001f517 Регистрация клиента</a> '
    '<a href="/register/partner/" target="_blank" style="color:#4ade80;font-size:13px;margin-left:12px;">\U0001f517 Регистрация партнёра</a>'
)

def custom_logout(request):
    logout(request)
    return redirect('/login/')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='web/login.html'), name='login'),
    path('logout/', custom_logout, name='logout'),
    path('', include('web.urls')),
]

