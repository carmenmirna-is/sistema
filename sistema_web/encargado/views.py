from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db import connection
from django.core.mail import send_mail

def dashboard_encargado(request):
    if not request.session.get('usuario_id') or request.session.get('tipo_usuario') != 'encargado':
        return redirect('login')

    return render(request, 'encargado/dashboard_encargado.html')

def solicitudes_pendientes(request):
    if not request.session.get('usuario_id') or request.session.get('tipo_usuario') != 'encargado':
        return redirect('login')

    encargado_id = request.session.get('usuario_id')  # Obtener el ID del encargado desde la sesión

    try:
        with connection.cursor() as cur:
            # Obtener el espacio asignado al encargado
            cur.execute("SELECT id FROM espacio WHERE encargado_id = %s", (encargado_id,))
            espacio = cur.fetchone()

            if espacio:
                espacio_id = espacio[0]
                # Obtener las solicitudes pendientes relacionadas con el espacio del encargado
                cur.execute(
                    "SELECT s.id, s.nombre_evento, s.fecha, u.nombre AS usuario_nombre "
                    "FROM solicitud s "
                    "JOIN usuario u ON s.usuario_id = u.id "
                    "WHERE s.estado = 'pendiente' AND s.espacio_id = %s",
                    (espacio_id,)
                )
                solicitudes = cur.fetchall()
            else:
                solicitudes = []  # Si el encargado no tiene un espacio asignado
    except Exception as e:
        return HttpResponse(f"Error: {e}", status=500)

    return render(request, 'encargado/solicitudes_pendientes.html', {'solicitudes': solicitudes})

def aprobar_solicitud(request, solicitud_id):
    if not request.session.get('usuario_id') or request.session.get('tipo_usuario') != 'encargado':
        return redirect('login')

    encargado_id = request.session.get('usuario_id')  # Obtener el ID del encargado desde la sesión

    try:
        with connection.cursor() as cur:
            # Verificar que la solicitud pertenezca al espacio del encargado
            cur.execute(
                "SELECT s.id, s.espacio_id "
                "FROM solicitud s "
                "JOIN espacio e ON s.espacio_id = e.id "
                "WHERE s.id = %s AND e.encargado_id = %s",
                (solicitud_id, encargado_id)
            )
            solicitud = cur.fetchone()

            if not solicitud:
                return HttpResponse("No tienes permiso para aprobar esta solicitud", status=403)

            # Aprobar la solicitud
            cur.execute(
                "UPDATE solicitud SET estado = 'aceptada' WHERE id = %s",
                (solicitud_id,)
            )
            connection.commit()

            # Obtener información del usuario y la solicitud
            cur.execute(
                "SELECT u.correo, s.nombre_evento "
                "FROM solicitud s "
                "JOIN usuario u ON s.usuario_id = u.id "
                "WHERE s.id = %s",
                (solicitud_id,)
            )
            resultado = cur.fetchone()
            if resultado:
                correo_usuario, nombre_evento = resultado

                # Enviar correo de notificación
                send_mail(
                    'Solicitud Aprobada',
                    f'Tu solicitud para el evento "{nombre_evento}" ha sido aprobada.',
                    'cibanezsanguino@gmail.com',  # Remitente
                    [correo_usuario],  # Destinatario
                    fail_silently=False,
                )
    except Exception as e:
        return HttpResponse(f"Error: {e}", status=500)

    return redirect('solicitudes_pendientes')

def rechazar_solicitud(request, solicitud_id):
    if not request.session.get('usuario_id') or request.session.get('tipo_usuario') != 'encargado':
        return redirect('login')

    encargado_id = request.session.get('usuario_id')  # Obtener el ID del encargado desde la sesión

    if request.method == 'POST':
        motivo_rechazo = request.POST.get('motivo_rechazo')

        try:
            with connection.cursor() as cur:
                # Verificar que la solicitud pertenezca al espacio del encargado
                cur.execute(
                    "SELECT s.id, s.espacio_id "
                    "FROM solicitud s "
                    "JOIN espacio e ON s.espacio_id = e.id "
                    "WHERE s.id = %s AND e.encargado_id = %s",
                    (solicitud_id, encargado_id)
                )
                solicitud = cur.fetchone()

                if not solicitud:
                    return HttpResponse("No tienes permiso para rechazar esta solicitud", status=403)

                # Rechazar la solicitud
                cur.execute(
                    "UPDATE solicitud SET estado = 'rechazada', motivo_rechazo = %s WHERE id = %s",
                    (motivo_rechazo, solicitud_id)
                )
                connection.commit()

                # Obtener información del usuario y la solicitud
                cur.execute(
                    "SELECT u.correo, s.nombre_evento "
                    "FROM solicitud s "
                    "JOIN usuario u ON s.usuario_id = u.id "
                    "WHERE s.id = %s",
                    (solicitud_id,)
                )
                resultado = cur.fetchone()
                if resultado:
                    correo_usuario, nombre_evento = resultado

                    # Enviar correo de notificación
                    send_mail(
                        'Solicitud Rechazada',
                        f'Tu solicitud para el evento "{nombre_evento}" ha sido rechazada. Motivo: {motivo_rechazo}',
                        'cibanezsanguino@gmail.com',  # Remitente
                        [correo_usuario],  # Destinatario
                        fail_silently=False,
                    )
        except Exception as e:
            return HttpResponse(f"Error: {e}", status=500)

        return redirect('solicitudes_pendientes')

    return render(request, 'encargado/rechazar_solicitud.html', {'solicitud_id': solicitud_id})

def solicitudes_aceptadas(request):
    if not request.session.get('usuario_id') or request.session.get('tipo_usuario') != 'encargado':
        return redirect('login')

    encargado_id = request.session.get('usuario_id')  # Obtener el ID del encargado desde la sesión

    try:
        with connection.cursor() as cur:
            # Obtener el espacio asignado al encargado
            cur.execute("SELECT id FROM espacio WHERE encargado_id = %s", (encargado_id,))
            espacio = cur.fetchone()

            if espacio:
                espacio_id = espacio[0]
                # Obtener las solicitudes aceptadas relacionadas con el espacio del encargado
                cur.execute(
                    "SELECT s.id, s.nombre_evento, s.fecha, u.nombre AS usuario_nombre "
                    "FROM solicitud s "
                    "JOIN usuario u ON s.usuario_id = u.id "
                    "WHERE s.estado = 'aceptada' AND s.espacio_id = %s",
                    (espacio_id,)
                )
                solicitudes = cur.fetchall()
            else:
                solicitudes = []  # Si el encargado no tiene un espacio asignado
    except Exception as e:
        return HttpResponse(f"Error: {e}", status=500)

    return render(request, 'encargado/solicitudes_aceptadas.html', {'solicitudes': solicitudes})

def listar_solicitudes(request):
    if not request.session.get('usuario_id') or request.session.get('tipo_usuario') != 'encargado':
        return redirect('login')

    encargado_id = request.session.get('usuario_id')  # Obtener el ID del encargado desde la sesión

    try:
        with connection.cursor() as cur:
            # Obtener el espacio asignado al encargado
            cur.execute("SELECT id FROM espacio WHERE encargado_id = %s", (encargado_id,))
            espacio = cur.fetchone()

            if espacio:
                espacio_id = espacio[0]
                # Obtener las solicitudes relacionadas con el espacio del encargado
                cur.execute(
                    "SELECT s.id, s.nombre_evento, s.fecha, u.nombre AS usuario_nombre, s.estado "
                    "FROM solicitud s "
                    "JOIN usuario u ON s.usuario_id = u.id "
                    "WHERE s.espacio_id = %s",
                    (espacio_id,)
                )
                solicitudes = cur.fetchall()
            else:
                solicitudes = []  # Si el encargado no tiene un espacio asignado
    except Exception as e:
        return HttpResponse(f"Error: {e}", status=500)

    return render(request, 'encargado/listar_solicitudes.html', {'solicitudes': solicitudes})