from django.shortcuts import render, redirect
from django.http import HttpResponse
from sistema_web.db import get_db_connection
from django.shortcuts import render

def home(request):
    return render(request, 'usuarios/home.html')

def registrar_usuario(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        correo = request.POST.get('correo')
        contraseña = request.POST.get('contraseña')
        tipo_usuario = request.POST.get('tipo_usuario')

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO usuario (nombre, correo, contraseña, tipo_usuario) VALUES (%s, %s, %s, %s)",
                (nombre, correo, contraseña, tipo_usuario)
            )
            conn.commit()
        except Exception as e:
            return HttpResponse(f"Error: {e}", status=500)
        finally:
            cur.close()
            conn.close()

        return redirect('login')

    return render(request, 'usuarios/registrar_usuario.html')

def login(request):
    if request.method == 'POST':
        correo = request.POST.get('correo')
        contraseña = request.POST.get('contraseña')

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "SELECT id, nombre, tipo_usuario FROM usuario WHERE correo = %s AND contraseña = %s",
                (correo, contraseña)
            )
            usuario = cur.fetchone()
        except Exception as e:
            return HttpResponse(f"Error: {e}", status=500)
        finally:
            cur.close()
            conn.close()

        if usuario:
            # Guardar el ID y tipo de usuario en la sesión
            request.session['usuario_id'] = usuario[0]
            request.session['tipo_usuario'] = usuario[2]
            return redirect('dashboard')
        else:
            return HttpResponse("Correo o contraseña incorrectos", status=401)

    return render(request, 'usuarios/login.html')

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

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO solicitud (nombre_evento, fecha, espacio_id, usuario_id, estado) "
                "VALUES (%s, %s, %s, %s, 'pendiente')",
                (nombre_evento, fecha, espacio_id, usuario_id)
            )
            conn.commit()
        except Exception as e:
            return HttpResponse(f"Error: {e}", status=500)
        finally:
            cur.close()
            conn.close()

        return redirect('dashboard')

    # Si es GET, mostrar el formulario
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre FROM espacio")
    espacios = cur.fetchall()
    cur.close()
    conn.close()

    return render(request, 'usuarios/enviar_solicitud.html', {'espacios': espacios})
# Create your views here.
