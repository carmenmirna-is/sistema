from django.shortcuts import render, redirect
from django.http import HttpResponse
from sistema_web.db import get_db_connection

def registrar_espacio(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        encargado_id = request.POST.get('encargado_id')

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO espacio (nombre, descripcion, encargado_id) VALUES (%s, %s, %s)",
                (nombre, descripcion, encargado_id)
            )
            conn.commit()
        except Exception as e:
            return HttpResponse(f"Error: {e}", status=500)
        finally:
            cur.close()
            conn.close()

        return redirect('lista_espacios')

    # Si es GET, mostrar el formulario
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre FROM encargado")
    encargados = cur.fetchall()
    cur.close()
    conn.close()

    return render(request, 'administrador/registrar_espacio.html', {'encargados': encargados})

# Create your views here.
