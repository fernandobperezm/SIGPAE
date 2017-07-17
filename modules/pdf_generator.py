# -*- coding: utf-8 -*-
import cStringIO
import os
import re
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def replaceBreak(text):
    return str(text).replace('\n','<br/>')

def setWaterMark(canvas, doc):
    canvas.saveState()
    canvas.setFont("Times-Roman", 32)
    canvas.setFillGray(0.85)
    canvas.drawCentredString(11*cm, 6*cm, "Documento sin validez")
    canvas.drawCentredString(11*cm, 13*cm, "Documento sin validez")
    canvas.drawCentredString(11*cm, 20*cm, "Documento sin validez")
    canvas.restoreState()

def generatePDF(buffer, request,
                cod,
                nombre,
                depto,
                division,
                anio_vig,
                periodo_vig,
                h_teoria,
                h_practica,
                h_laboratorio,
                creditos,
                sinopticos,
                fuentes,
                requisitos,
                estrategias_met,
                estrategias_eval,
                justificacion,
                obj_general,
                obj_especificos,
                observaciones,
                extras=None):

    extras = {}
    extras = {
        "Materiales" : "Cemento y piedra",
        "Software": "Windows 10 Original"
    }

    title = "Programa analítico %s.pdf" % cod
    doc = SimpleDocTemplate(buffer, title=title, pagesize=letter,
                            rightMargin=3*cm,leftMargin=4*cm,
                            topMargin=3*cm, bottomMargin=3*cm)

    Story = []
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Top',
                              fontName="Times",
                              leading=16,
                              fontSize=12,
                              alignment=TA_CENTER))
    styles.add(ParagraphStyle(name='Programa',
                              alignment=TA_JUSTIFY,
                              fontName="Times",
                              fontSize=12,
                              borderWidth=0.5,
                              borderColor='#000000',
                              borderPadding=(4, 6, 5, 6),
                              spaceAfter=18,
                              leading=14))

    # Header
    filepath = os.path.join(request.folder, 'static', 'images/home/usblogo.png')
    im = Image(filepath, width=100, height=66)
    text = "<b>UNIVERSIDAD SIMÓN BOLÍVAR</b><br/><b>Vicerrectorado Académico</b><br/>%s" % division
    text = Paragraph(text, styles["Top"])
    data = [[im, text, '','','','','','','']]
    t = Table(data)
    t.setStyle(TableStyle([
        ('VALIGN', (1,0), (1,0), 'CENTER'),
        ('SPAN',(1,0),(6,0)),
        ('BOTTOMPADDING', (0,0),(-1,-1),20)
    ]))
    Story.append(t)

    #Departamento
    text = "<b>Departamento: </b>" + depto
    Story.append(Paragraph(text, styles["Programa"]))

    #Nombre Asignatura
    text = "<b>Asignatura: </b>%s - %s" % (cod, nombre)
    Story.append(Paragraph(text, styles["Programa"]))

    # Unidades credito
    text = "<b>N° unidades de crédito:</b> %s<br/>" % creditos
    text +="<b>N° de horas semanales:</b>  Teoría %s, Práctica %s, Laboratorio %s" % (h_teoria,h_practica,h_laboratorio)
    Story.append(Paragraph(text, styles["Programa"]))

    #Requisitos
    if(requisitos):
        text = "<b>Requisitos: </b>" + replaceBreak(requisitos)
        Story.append(Paragraph(text, styles["Programa"]))

    #Entrada Vigencia
    if(periodo_vig and anio_vig):
        text = "<b>Fecha de entrada en vigencia: </b> %s %s" % (periodo_vig,anio_vig)
        Story.append(Paragraph(text, styles["Programa"]))

    #Objetivos
    if(obj_general):
        text = "<b>Objetivo General:</b><br/>" + replaceBreak(obj_general)
        Story.append(Paragraph(text, styles["Programa"]))

    if(obj_especificos):
        text = "<b>Objetivos Específicos:</b><br/>" + replaceBreak(obj_especificos)
        Story.append(Paragraph(text, styles["Programa"]))

    #Justificacion
    if(justificacion):
        text = "<b>Justificacion:</b><br/>" + replaceBreak(justificacion)
        Story.append(Paragraph(text, styles["Programa"]))

    #Contenidos sinopticos
    if(sinopticos):
        text = "<b>Contenidos sinópticos:</b><br/>" + replaceBreak(sinopticos)
        Story.append(Paragraph(text, styles["Programa"]))

    #Estrategias
    if(estrategias_met):
        text = "<b>Estrategias metodológicas:</b><br/>" + replaceBreak(estrategias_met)
        Story.append(Paragraph(text, styles["Programa"]))

    if(estrategias_eval):
        text = "<b>Estrategias de evaluación:</b><br/>" + replaceBreak(estrategias_eval)
        Story.append(Paragraph(text, styles["Programa"]))

    #Fuentes
    if(fuentes):
        text = "<b>Fuentes recomendadas de información:</b><br/>" + replaceBreak(fuentes)
        Story.append(Paragraph(text, styles["Programa"]))

    #Extras
    for key in extras:
        text = "<b>%s:</b><br/>%s" % (key,replaceBreak(extras[key]))
        Story.append(Paragraph(text, styles["Programa"]))

    #Observaciones
    if(observaciones):
        text = "<b>Observaciones:</b><br/>" + replaceBreak(observaciones)
        Story.append(Paragraph(text, styles["Programa"]))

    doc.build(Story, onFirstPage=setWaterMark, onLaterPages=setWaterMark)