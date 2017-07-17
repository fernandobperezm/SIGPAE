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

def generatePDF(buffer, request):

    var = {
        "departamento": "Computación y Tecnología de la Información",
        "division": "División de Ciencias Físicas y Matemáticas",
        "cod" : "CI2125",
        "nombre": "Computación I",
        "vigencia": "Ene-Mar 2011",
        "creditos": "3",
        "h_teoria" : "4",
        "h_practica" : "2",
        "h_laboratorio" : "1",
        "obj_general": "Descripcion de objetivo",
        "obj_especificos":"1) Objetivo 1\n2) Objetivo 2\n 3) Objetivo 3",
        "sinopticos": "Contenidos sinopticos",
        "observaciones": "Observaciones"
    }

    extras = {}
    extras = {
        "Materiales" : "Cemento y piedra",
        "Software": "Windows 10 Original"
    }

    title = "Programa analítico %s.pdf" % var["cod"]
    doc = SimpleDocTemplate(buffer, title=title, pagesize=letter,
                            rightMargin=3*cm,leftMargin=4*cm,
                            topMargin=3*cm, bottomMargin=3*cm)

    var["departamento"] = "Computación y Tecnología de la Información"
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
                              borderPadding = (4, 6, 5, 6),
                              spaceAfter=18,
                              spaceShrinkage=3,
                              leading=15))

    # Header
    filepath = os.path.join(request.folder, 'static', 'images/home/usblogo.png')
    im = Image(filepath, width=100, height=66)
    text = "<b>UNIVERSIDAD SIMÓN BOLÍVAR</b><br/><b>Vicerrectorado Académico</b><br/>%s" % var["division"]
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
    text = "<b>Departamento: </b>" + var["departamento"]
    Story.append(Paragraph(text, styles["Programa"]))

    #Nombre Asignatura
    text = "<b>Asignatura: </b>%s - %s" % (var["cod"], var["nombre"])
    Story.append(Paragraph(text, styles["Programa"]))

    # Unidades credito
    text = "<b>N° unidades de crédito:</b> %s<br/>" % var["creditos"]
    text +="<b>N° de horas semanales:</b>  Teoría %s, Práctica %s, Laboratorio %s" % (var["h_teoria"],var["h_practica"],var["h_laboratorio"])
    Story.append(Paragraph(text, styles["Programa"]))

    #Entrada Vigencia
    text = "<b>Fecha de entrada en vigencia: </b>" + var["vigencia"]
    Story.append(Paragraph(text, styles["Programa"]))

    #Objetivos
    if(var.get("obj_general")):
        text = "<b>Objetivo General:</b><br/>" + replaceBreak(var["obj_general"])
        Story.append(Paragraph(text, styles["Programa"]))

    if(var.get("obj_especificos")):
        text = "<b>Objetivos Específicos:</b><br/>" + replaceBreak(var["obj_especificos"])
        Story.append(Paragraph(text, styles["Programa"]))

    if(var.get("objetivos")):
        text = "<b>Objetivos:</b><br/>" + replaceBreak(var["objetivos"])
        Story.append(Paragraph(text, styles["Programa"]))

    #Contenidos sinopticos
    if(var.get("sinopticos")):
        text = "<b>Contenidos sinópticos:</b><br/>" + replaceBreak(var["sinopticos"])
        Story.append(Paragraph(text, styles["Programa"]))

    #Estrategias
    if(var.get("e_metodologicas")):
        text = "<b>Estrategias metodológicas:</b><br/>" + replaceBreak(var["e_metodologicas"])
        Story.append(Paragraph(text, styles["Programa"]))

    if(var.get("e_evaluacion")):
        text = "<b>Estrategias de evaluación:</b><br/>" + replaceBreak(var["e_evaluacion"])
        Story.append(Paragraph(text, styles["Programa"]))

    #Fuentes
    if(var.get("fuentes")):
        text = "<b>Fuentes recomendadas de información:</b><br/>" + replaceBreak(var["fuentes"])
        Story.append(Paragraph(text, styles["Programa"]))

    #Extras
    for key in extras:
        text = "<b>%s:</b><br/>%s" % (key,replaceBreak(extras[key]))
        Story.append(Paragraph(text, styles["Programa"]))

    #Observaciones
    if(var.get("observaciones")):
        text = "<b>Observaciones:</b><br/>" + replaceBreak(var["observaciones"])
        Story.append(Paragraph(text, styles["Programa"]))

    ## Documento sin validez
    doc.build(Story, onFirstPage=setWaterMark, onLaterPages=setWaterMark)