from django.shortcuts import render, redirect
from django.http import HttpResponse
from sistema_web.db import get_db_connection
from django.core.mail import send_mail

def solicitudes_pendientes(request):
    if not request.session.get('usuario_id'):
        return redirect('login')

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT s.id, s.nombre_evento, s.fecha, u.nombre AS usuario_nombre "
            "FROM solicitud s "
            "JOIN usuario u ON s.usuario_id = u.id "
            "WHERE s.estado = 'pendiente'"
        )
        solicitudes = cur.fetchall()
    except Exception as e:
        return HttpResponse(f"Error: {e}", status=500)
    finally:
        cur.close()
        conn.close()

    return render(request, 'encargado/solicitudes_pendientes.html', {'solicitudes': solicitudes})

def aprobar_solicitud(request, solicitud_id):
    if not request.session.get('usuario_id'):
        return redirect('login')

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Aprobar la solicitud
        cur.execute(
            "UPDATE solicitud SET estado = 'aceptada' WHERE id = %s",
            (solicitud_id,)
        )
        conn.commit()

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
                'tu_correo@gmail.com',  # Remitente
                [correo_usuario],  # Destinatario
                fail_silently=False,
            )
    except Exception as e:
        return HttpResponse(f"Error: {e}", status=500)
    finally:
        cur.close()
        conn.close()

    return redirect('solicitudes_pendientes')

def rechazar_solicitud(request, solicitud_id):
    if not request.session.get('usuario_id'):
        return redirect('login')

    if request.method == 'POST':
        motivo_rechazo = request.POST.get('motivo_rechazo')

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            # Rechazar la solicitud
            cur.execute(
                "UPDATE solicitud SET estado = 'rechazada', motivo_rechazo = %s WHERE id = %s",
                (motivo_rechazo, solicitud_id)
            )
            conn.commit()

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
                    'tu_correo@gmail.com',  # Remitente
                    [correo_usuario],  # Destinatario
                    fail_silently=False,
                )
        except Exception as e:
            return HttpResponse(f"Error: {e}", status=500)
        finally:
            cur.close()
            conn.close()

        return redirect('solicitudes_pendientes')

    return render(request, 'encargado/rechazar_solicitud.html', {'solicitud_id': solicitud_id})

def solicitudes_aceptadas(request):
    if not request.session.get('usuario_id'):
        return redirect('login')

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT s.id, s.nombre_evento, s.fecha, u.nombre AS usuario_nombre "
            "FROM solicitud s "
            "JOIN usuario u ON s.usuario_id = u.id "
            "WHERE s.estado = 'aceptada'"
        )
        solicitudes = cur.fetchall()
    except Exception as e:
        return HttpResponse(f"Error: {e}", status=500)
    finally:
        cur.close()
        conn.close()

    return render(request, 'encargado/solicitudes_aceptadas.html', {'solicitudes': solicitudes})
# Create your views here.
