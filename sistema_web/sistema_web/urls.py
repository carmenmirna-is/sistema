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
from administrador import views as administrador_views
from django.conf.urls import handler404

handler404 = 'sistema_web.views.custom_404'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', usuarios_views.home, name='home'),  # Ruta raíz
    path('registrar/', usuarios_views.registrar_usuario, name='registrar_usuario'),
    path('login/', usuarios_views.login, name='login'),
    path('dashboard/', usuarios_views.dashboard_usuario, name='dashboard_usuario'),
    path('dashboard-administrador/', administrador_views.dashboard_administrador, name='dashboard_administrador'),
    path('dashboard-encargado/', encargado_views.dashboard_encargado, name='dashboard_encargado'),
    path('dashboard/', usuarios_views.dashboard, name='dashboard'),
    path('logout/', usuarios_views.logout, name='logout'),
    path('enviar-solicitud/', usuarios_views.enviar_solicitud, name='enviar_solicitud'),
    path('solicitudes/', encargado_views.listar_solicitudes, name='listar_solicitudes'),
    path('solicitudes_pendientes/', encargado_views.solicitudes_pendientes, name='solicitudes_pendientes'),
    path('aprobar-solicitud/<int:solicitud_id>/', encargado_views.aprobar_solicitud, name='aprobar_solicitud'),
    path('rechazar-solicitud/<int:solicitud_id>/', encargado_views.rechazar_solicitud, name='rechazar_solicitud'),
    path('solicitudes-aceptadas/', encargado_views.solicitudes_aceptadas, name='solicitudes_aceptadas'),
    path('reportes/generar/', reportes_views.generar_reportes, name='generar_reportes'),
    path('reportes/generar/reporte/', reportes_views.generar_reporte, name='generar_reporte'),
    path('registrar-espacio/', administrador_views.registrar_espacio, name='registrar_espacio'),
    path('registrar-encargado/', administrador_views.registrar_encargado, name='registrar_encargado'),
    path('listar-espacios/', administrador_views.listar_espacios, name='listar_espacios'),
    path('editar-espacio/<int:espacio_id>/', administrador_views.editar_espacio, name='editar_espacio'),
    path('eliminar-espacio/<int:espacio_id>/', administrador_views.eliminar_espacio, name='eliminar_espacio'),
    path('listar-encargados/', administrador_views.listar_encargados, name='listar_encargados'),
    path('editar-encargado/<int:encargado_id>/', administrador_views.editar_encargado, name='editar_encargado'),
    path('eliminar-encargado/<int:encargado_id>/', administrador_views.eliminar_encargado, name='eliminar_encargado'),
    path('espacios-disponibles/', usuarios_views.espacios_disponibles, name='espacios_disponibles'),
]
