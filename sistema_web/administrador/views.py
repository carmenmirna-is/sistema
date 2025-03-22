from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db import connection

def dashboard_administrador(request):
    if not request.session.get('usuario_id') or request.session.get('tipo_usuario') != 'administrador':
        return redirect('login')

    return render(request, 'administrador/dashboard_administrador.html')

def registrar_espacio(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        encargado_id = request.POST.get('encargado_id')

        if not nombre or not descripcion or not encargado_id:
            return HttpResponse("Todos los campos son requeridos", status=400)

        try:
            with connection.cursor() as cur:
                cur.execute(
                    "INSERT INTO espacio (nombre, descripcion, encargado_id) VALUES (%s, %s, %s)",
                    (nombre, descripcion, encargado_id)
                )
                connection.commit()
        except Exception as e:
            return HttpResponse(f"Error: {e}", status=500)

        return redirect('listar_espacios')

    # Si es GET, mostrar el formulario
    try:
        with connection.cursor() as cur:
            cur.execute("SELECT id, nombre FROM encargado")
            encargados = cur.fetchall()
    except Exception as e:
        return HttpResponse(f"Error: {e}", status=500)

    return render(request, 'administrador/registrar_espacio.html', {'encargados': encargados})

def registrar_encargado(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        correo = request.POST.get('correo')
        contraseña = request.POST.get('contraseña')

        # Validación de campos requeridos
        if not nombre or not correo or not contraseña:
            return HttpResponse("Todos los campos son requeridos", status=400)

        try:
            with connection.cursor() as cur:
                # Registrar el encargado
                cur.execute(
                    "INSERT INTO encargado (nombre, correo, contraseña) VALUES (%s, %s, %s) RETURNING id",
                    (nombre, correo, contraseña)
                )
                connection.commit()  # Confirmar la transacción
        except Exception as e:
            return HttpResponse(f"Error: {e}", status=500)

        return redirect('listar_encargados')

    # Si es GET, mostrar el formulario
    return render(request, 'administrador/registrar_encargado.html')

def listar_espacios(request):
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

    return render(request, 'administrador/listar_espacios.html', {'espacios': espacios})

def editar_espacio(request, espacio_id):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        encargado_id = request.POST.get('encargado_id')

        if not nombre or not descripcion or not encargado_id:
            return HttpResponse("Todos los campos son requeridos", status=400)

        try:
            with connection.cursor() as cur:
                cur.execute(
                    "UPDATE espacio SET nombre = %s, descripcion = %s, encargado_id = %s WHERE id = %s",
                    (nombre, descripcion, encargado_id, espacio_id)
                )
                connection.commit()
        except Exception as e:
            return HttpResponse(f"Error: {e}", status=500)

        return redirect('listar_espacios')

    # Si es GET, mostrar el formulario con los datos actuales
    try:
        with connection.cursor() as cur:
            cur.execute("SELECT id, nombre, descripcion, encargado_id FROM espacio WHERE id = %s", (espacio_id,))
            espacio = cur.fetchone()
            cur.execute("SELECT id, nombre FROM encargado")
            encargados = cur.fetchall()
    except Exception as e:
        return HttpResponse(f"Error: {e}", status=500)

    return render(request, 'administrador/editar_espacio.html', {'espacio': espacio, 'encargados': encargados})

def eliminar_espacio(request, espacio_id):
    try:
        with connection.cursor() as cur:
            cur.execute("DELETE FROM espacio WHERE id = %s", (espacio_id,))
            connection.commit()
    except Exception as e:
        return HttpResponse(f"Error: {e}", status=500)

    return redirect('listar_espacios')

def listar_encargados(request):
    if not request.session.get('usuario_id') or request.session.get('tipo_usuario') != 'administrador':
        return redirect('login')
    
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, nombre, correo, contraseña FROM encargado ORDER BY nombre"
            )
            # Convertir el resultado en una lista de diccionarios
            columns = [col[0] for col in cursor.description]
            encargados = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        return render(request, 'administrador/listar_encargados.html', {
            'encargados': encargados
        })
    except Exception as e:
        print(f"Error en listar_encargados: {e}")
        return HttpResponse(f"Error: {e}", status=500)

def editar_encargado(request, encargado_id):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        correo = request.POST.get('correo')
        contraseña = request.POST.get('contraseña')
        espacio_id = request.POST.get('espacio_id')

        if not nombre or not correo or not contraseña:
            return HttpResponse("Todos los campos son requeridos", status=400)

        try:
            with connection.cursor() as cur:
                cur.execute(
                    "UPDATE encargado SET nombre = %s, correo = %s, contraseña = %s WHERE id = %s",
                    (nombre, correo, contraseña, encargado_id)
                )
                if espacio_id:
                    cur.execute(
                        "UPDATE espacio SET encargado_id = %s WHERE id = %s",
                        (encargado_id, espacio_id)
                    )
                connection.commit()
        except Exception as e:
            return HttpResponse(f"Error: {e}", status=500)

        return redirect('listar_encargados')

    # Si es GET, mostrar el formulario con los datos actuales
    try:
        with connection.cursor() as cur:
            cur.execute("SELECT id, nombre, correo, contraseña FROM encargado WHERE id = %s", (encargado_id,))
            encargado = cur.fetchone()
            cur.execute("SELECT id, nombre FROM espacio")
            espacios = cur.fetchall()
    except Exception as e:
        return HttpResponse(f"Error: {e}", status=500)

    return render(request, 'administrador/editar_encargado.html', {'encargado': encargado, 'espacios': espacios})

def eliminar_encargado(request, encargado_id):
    try:
        with connection.cursor() as cur:
            cur.execute("DELETE FROM encargado WHERE id = %s", (encargado_id,))
            connection.commit()
    except Exception as e:
        return HttpResponse(f"Error: {e}", status=500)

    return redirect('listar_encargados')