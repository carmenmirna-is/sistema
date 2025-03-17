"""
URL configuration for sistema_web project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from usuarios import views as usuarios_views
from encargado import views as encargado_views
from reportes import views as reportes_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', usuarios_views.home, name='home'),  # Ruta raíz
    path('registrar/', usuarios_views.registrar_usuario, name='registrar_usuario'),
    path('login/', usuarios_views.login, name='login'),
    path('dashboard/', usuarios_views.dashboard, name='dashboard'),
    path('logout/', usuarios_views.logout, name='logout'),
    path('enviar-solicitud/', usuarios_views.enviar_solicitud, name='enviar_solicitud'),
    path('solicitudes-pendientes/', encargado_views.solicitudes_pendientes, name='solicitudes_pendientes'),
    path('aprobar-solicitud/<int:solicitud_id>/', encargado_views.aprobar_solicitud, name='aprobar_solicitud'),
    path('rechazar-solicitud/<int:solicitud_id>/', encargado_views.rechazar_solicitud, name='rechazar_solicitud'),
    path('solicitudes-aceptadas/', encargado_views.solicitudes_aceptadas, name='solicitudes_aceptadas'),
    path('reporte-pdf/', reportes_views.generar_reporte_pdf, name='reporte_pdf'),
    path('reporte-excel/', reportes_views.generar_reporte_excel, name='reporte_excel'),
    path('reporte-word/', reportes_views.generar_reporte_word, name='reporte_word'),
]
