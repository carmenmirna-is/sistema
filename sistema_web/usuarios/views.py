from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db import connection

def home(request):
    return render(request, 'usuarios/home.html')

def dashboard_usuario(request):
    if not request.session.get('usuario_id') or request.session.get('tipo_usuario') not in ['estudiante', 'autoridad']:
        return redirect('login')

    return render(request, 'usuarios/dashboard_usuario.html')

def registrar_usuario(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        correo = request.POST.get('correo')
        contraseña = request.POST.get('contraseña')
        tipo_usuario = request.POST.get('tipo_usuario')

        try:
            with connection.cursor() as cur:
                cur.execute(
                    "INSERT INTO usuario (nombre, correo, contraseña, tipo_usuario) VALUES (%s, %s, %s, %s)",
                    (nombre, correo, contraseña, tipo_usuario)
                )
                connection.commit()
        except Exception as e:
            return HttpResponse(f"Error: {e}", status=500)

        return redirect('login')

    return render(request, 'usuarios/registrar_usuario.html')

def login(request):
    error_message = None

    if request.method == 'POST':
        correo = request.POST.get('correo')
        contraseña = request.POST.get('contraseña')

        try:
            with connection.cursor() as cur:
                # Verificar en la tabla administrador
                cur.execute(
                    "SELECT id, nombre, 'administrador' AS tipo_usuario FROM administrador WHERE correo = %s AND contraseña = %s",
                    (correo, contraseña)
                )
                usuario = cur.fetchone()

                # Si no se encuentra en administrador, verificar en encargado
                if not usuario:
                    cur.execute(
                        "SELECT id, nombre, 'encargado' AS tipo_usuario FROM encargado WHERE correo = %s AND contraseña = %s",
                        (correo, contraseña)
                    )
                    usuario = cur.fetchone()

                # Si no se encuentra en encargado, verificar en usuario
                if not usuario:
                    cur.execute(
                        "SELECT id, nombre, tipo_usuario FROM usuario WHERE correo = %s AND contraseña = %s",
                        (correo, contraseña)
                    )
                    usuario = cur.fetchone()

        except Exception as e:
            return HttpResponse(f"Error: {e}", status=500)

        if usuario:
            request.session['usuario_id'] = usuario[0]
            request.session['nombre'] = usuario[1]
            request.session['tipo_usuario'] = usuario[2]

            if usuario[2] == 'administrador':
                return redirect('dashboard_administrador')
            elif usuario[2] == 'encargado':
                return redirect('dashboard_encargado')
            elif usuario[2] in ['estudiante', 'autoridad']:
                return redirect('dashboard_usuario')
            else:
                return HttpResponse("Tipo de usuario no válido", status=400)
        else:
            error_message = "Correo o contraseña incorrectos. Por favor, inténtalo de nuevo."

    return render(request, 'usuarios/login.html', {
        'error_message': error_message,
        'correo': request.POST.get('correo', '')
    })

def dashboard(request):
    if not request.session.get('usuario_id'):
        return redirect('login')

    usuario_id = request.session['usuario_id']
    tipo_usuario = request.session['tipo_usuario']

    return render(request, 'usuarios/dashboard.html', {
        'usuario_id': usuario_id,
        'tipo_usuario': tipo_usuario
    })

def logout(request):
    request.session.flush()  # Eliminar la sesión
    return redirect('login')

def enviar_solicitud(request):
    if not request.session.get('usuario_id'):
        return redirect('login')

    if request.method == 'POST':
        nombre_evento = request.POST.get('nombre_evento')
        fecha = request.POST.get('fecha')
        espacio_id = request.POST.get('espacio_id')
        usuario_id = request.session['usuario_id']

        try:
            with connection.cursor() as cur:
                cur.execute(
                    "INSERT INTO solicitud (nombre_evento, fecha, espacio_id, usuario_id, estado) "
                    "VALUES (%s, %s, %s, %s, 'pendiente')",
                    (nombre_evento, fecha, espacio_id, usuario_id)
                )
                connection.commit()
        except Exception as e:
            return HttpResponse(f"Error: {e}", status=500)

        return redirect('dashboard')

    # Si es GET, mostrar el formulario
    try:
        with connection.cursor() as cur:
            cur.execute("SELECT id, nombre FROM espacio")
            espacios = cur.fetchall()
    except Exception as e:
        return HttpResponse(f"Error: {e}", status=500)

    return render(request, 'usuarios/enviar_solicitud.html', {'espacios': espacios})
# Create your views here.
