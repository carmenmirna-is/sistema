from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db import connection
from datetime import datetime, timedelta

def home(request):
    return render(request, 'usuarios/home.html')

def dashboard_usuario(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    # Manejo seguro de parámetros de fecha
    hoy = datetime.now()
    
    try:
        mes_actual = int(request.GET.get('mes', hoy.month))
        año_actual = int(request.GET.get('anio', hoy.year))
    except (ValueError, TypeError):
        mes_actual = hoy.month
        año_actual = hoy.year

    # Validación de rangos
    mes_actual = max(1, min(12, mes_actual))  # Asegura mes entre 1-12
    año_actual = max(2000, min(2100, año_actual))  # Ajusta según necesites

    # Navegación entre meses
    if mes_actual == 1:
        mes_anterior, anio_anterior = 12, año_actual - 1
        mes_siguiente, anio_siguiente = 2, año_actual
    elif mes_actual == 12:
        mes_anterior, anio_anterior = 11, año_actual
        mes_siguiente, anio_siguiente = 1, año_actual + 1
    else:
        mes_anterior, anio_anterior = mes_actual - 1, año_actual
        mes_siguiente, anio_siguiente = mes_actual + 1, año_actual

    # Nombres de meses en español
    nombres_meses = [
        "", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]
    nombre_mes = nombres_meses[mes_actual]  # Usamos el mes solicitado

    # Consulta SQL simplificada (sin horas)
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT s.id, s.nombre_evento, s.fecha, e.color, e.nombre as espacio
            FROM solicitud s
            JOIN espacio e ON s.espacio_id = e.id
            WHERE s.estado = 'aceptada' 
              AND s.usuario_id = %s
              AND EXTRACT(MONTH FROM s.fecha) = %s
              AND EXTRACT(YEAR FROM s.fecha) = %s
            ORDER BY s.fecha
        """, [usuario_id, mes_actual, año_actual])
        eventos_db = cursor.fetchall()

    # Procesamiento de eventos
    eventos_por_dia = {}
    for evento in eventos_db:
        dia = evento[2].day  # Extrae el día de la fecha
        if dia not in eventos_por_dia:
            eventos_por_dia[dia] = []
        eventos_por_dia[dia].append({
            'nombre': evento[1],
            'color': evento[3],
            'espacio': evento[4]
        })

    # Generación del calendario
    semanas = []
    primer_dia_mes = datetime(año_actual, mes_actual, 1)
    ultimo_dia_mes = (primer_dia_mes + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    
    # Ajuste para semana comenzando en domingo
    dia_actual = primer_dia_mes - timedelta(days=(primer_dia_mes.weekday() + 1) % 7)
    
    while dia_actual <= ultimo_dia_mes + timedelta(days=6):
        semana = []
        for _ in range(7):
            if dia_actual.month == mes_actual:
                semana.append({
                    'dia': dia_actual.day,
                    'eventos': eventos_por_dia.get(dia_actual.day, []),
                    'es_hoy': dia_actual.date() == hoy.date()
                })
            else:
                semana.append({'dia': 0, 'eventos': []})
            dia_actual += timedelta(days=1)
        semanas.append(semana)

    return render(request, 'usuarios/dashboard_usuario.html', {
        'usuario': {'nombre': request.session.get('nombre')},
        'semanas': semanas,
        'mes_actual': mes_actual,
        'año_actual': año_actual,
        'nombre_mes': nombre_mes,  # Usamos la variable calculada
        'mes_anterior': mes_anterior,
        'anio_anterior': anio_anterior,
        'mes_siguiente': mes_siguiente,
        'anio_siguiente': anio_siguiente
    })

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

def espacios_disponibles(request):
    try:
        with connection.cursor() as cur:
            cur.execute(
                "SELECT e.id, e.nombre, e.descripcion, c.nombre AS encargado_nombre "
                "FROM espacio e "
                "JOIN encargado c ON e.encargado_id = c.id"
            )
            espacios = cur.fetchall()
    except Exception as e:
        return HttpResponse(f"Error: {e}", status=500)
    return render(request, 'usuarios/espacios_disponibles.html', {'espacios': espacios})
# Create your views here.
