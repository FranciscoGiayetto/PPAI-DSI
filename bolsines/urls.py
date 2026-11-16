from django.urls import path
from django.views.generic import RedirectView

from .views import auth_views, seguimiento_views

urlpatterns = [
    path('', RedirectView.as_view(url='/seguimiento/', permanent=False)),
    path('login/', auth_views.login_view, name='login'),
    path('logout/', auth_views.logout_view, name='logout'),
    path('dashboard/', auth_views.dashboard_view, name='dashboard'),
    path('seguimiento/', seguimiento_views.seguimiento_view, name='seguimiento'),
    path('seguimiento/<int:nro_bolsin>/notificar/', seguimiento_views.notificar_ubicacion_view, name='notificar_ubicacion'),
]
