from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db import connection
from reportlab.pdfgen import canvas
from openpyxl import Workbook
from docx import Document

def generar_reporte_pdf(request):
    if not request.session.get('usuario_id'):
        return redirect('login')

    try:
        with connection.cursor() as cur:
            cur.execute(
                "SELECT s.nombre_evento, s.fecha, u.nombre AS usuario_nombre, e.nombre AS espacio_nombre "
                "FROM solicitud s "
                "JOIN usuario u ON s.usuario_id = u.id "
                "JOIN espacio e ON s.espacio_id = e.id "
                "WHERE s.estado = 'aceptada'"
            )
            solicitudes = cur.fetchall()
    except Exception as e:
        return HttpResponse(f"Error: {e}", status=500)

    # Crear el PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte.pdf"'

    p = canvas.Canvas(response)
    y = 800
    for solicitud in solicitudes:
        p.drawString(100, y, f"Evento: {solicitud[0]}")
        p.drawString(100, y - 20, f"Fecha: {solicitud[1]}")
        p.drawString(100, y - 40, f"Solicitante: {solicitud[2]}")
        p.drawString(100, y - 60, f"Espacio: {solicitud[3]}")
        y -= 80
        if y < 100:
            p.showPage()
            y = 800
    p.save()

    return response

def generar_reporte_excel(request):
    if not request.session.get('usuario_id'):
        return redirect('login')

    try:
        with connection.cursor() as cur:
            cur.execute(
                "SELECT s.nombre_evento, s.fecha, u.nombre AS usuario_nombre, e.nombre AS espacio_nombre "
                "FROM solicitud s "
                "JOIN usuario u ON s.usuario_id = u.id "
                "JOIN espacio e ON s.espacio_id = e.id "
                "WHERE s.estado = 'aceptada'"
            )
            solicitudes = cur.fetchall()
    except Exception as e:
        return HttpResponse(f"Error: {e}", status=500)

    # Crear el archivo Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Solicitudes Aceptadas"

    # Encabezados
    ws.append(["Evento", "Fecha", "Solicitante", "Espacio"])

    # Datos
    for solicitud in solicitudes:
        ws.append([solicitud[0], solicitud[1], solicitud[2], solicitud[3]])

    # Guardar el archivo
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="reporte.xlsx"'
    wb.save(response)

    return response

def generar_reporte_word(request):
    if not request.session.get('usuario_id'):
        return redirect('login')

    try:
        with connection.cursor() as cur:
            cur.execute(
                "SELECT s.nombre_evento, s.fecha, u.nombre AS usuario_nombre, e.nombre AS espacio_nombre "
                "FROM solicitud s "
                "JOIN usuario u ON s.usuario_id = u.id "
                "JOIN espacio e ON s.espacio_id = e.id "
                "WHERE s.estado = 'aceptada'"
            )
            solicitudes = cur.fetchall()
    except Exception as e:
        return HttpResponse(f"Error: {e}", status=500)

    # Crear el documento Word
    doc = Document()
    doc.add_heading('Reporte de Solicitudes Aceptadas', 0)

    for solicitud in solicitudes:
        doc.add_paragraph(f"Evento: {solicitud[0]}")
        doc.add_paragraph(f"Fecha: {solicitud[1]}")
        doc.add_paragraph(f"Solicitante: {solicitud[2]}")
        doc.add_paragraph(f"Espacio: {solicitud[3]}")
        doc.add_paragraph("")

    # Guardar el archivo
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response['Content-Disposition'] = 'attachment; filename="reporte.docx"'
    doc.save(response)

    return response