from   pdf_generator import generatePDF
import urllib2
import json
import re
import cStringIO
import os


@auth.requires(auth.is_logged_in() and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def list():
    """
        Inicio en la vista consulta de programas.
    """

    message = "Programas Analíticos de Estudio por Departamento"

    try:
        page = urllib2.urlopen('http://127.0.0.1:8000/SIGPAE_WS/default/webservices/departamentos/').read()
        departments =  json.loads(page)
    except urllib2.URLError as e:
        response.flash = 'Error de conexión con el Web Service.'
        return dict(message=message, error = e.reason, departments = {})

    return dict(message=message, departments = departments)

'''
    No requiere permiso especial, pues se trata de una vista que puede ser consultada publicamente.
'''
def view():
    """
        Permite visualisar un programa en una vista HTML con todos sus elementos.
    """

    message = "Detalles del Programa"

    id =  request.vars['id']
    if not isinstance(id, str):
        id = id[0]

    programa = db(db.PROGRAMA.id == id).select()
    if programa:
        programa = programa.first()
    else:
        redirect(URL(c='default', f='not_authorized'))

    # obtenemos los campos adicionales, si existen
    campos_adicionales = db(db.CAMPOS_ADICIONALES_PROGRAMA.programa == programa).select()

    return dict(message=message, programa=programa, campos_adicionales=campos_adicionales)


def generate():
    """
        Genera un PDF con los contenidos del programa registrados en el sistema.
    """
    cod = request.args(0)
    if not cod:
        redirect(URL(c='default', f='not_authorized'))

    # Obtener el programa
    programa = db(db.PROGRAMA.id == cod).select().first()

    if not programa:
        redirect(URL(c='default', f='not_authorized'))

    # Obtener extras
    extras = {}
    for e in db(db.CAMPOS_ADICIONALES_PROGRAMA.programa == programa).select():
        extras[e.nombre] = e.contenido

    #WebService para Obtener nombre departamento segun el codigo
    try:
        page = urllib2.urlopen(
            'http://127.0.0.1:8000/SIGPAE_WS/default/webservices/departamentos').read()
        department_data = json.loads(page)
    except urllib2.URLError as e:
        response.flash = 'Error de conexión con el Web Service.'
        return dict(error=e.reason)
    cod_depto = programa.codigo[:2] # Dos primeros digitos codigo del departamento
    for depto in department_data:
        if depto.get("siglas_depto") == cod_depto:
            nombre_depto = depto.get("nombre")



    buffer = cStringIO.StringIO()
    generatePDF(buffer=buffer,
                request=request,
                cod=programa.codigo,
                division="", #Falta obtener el codigo de división
                depto=nombre_depto,
                nombre=programa.denominacion,
                anio_vig=programa.anio,
                periodo_vig=programa.periodo,
                h_teoria=programa.horas_teoria,
                h_practica=programa.horas_practica,
                h_laboratorio=programa.horas_laboratorio,
                creditos=programa.creditos,
                sinopticos=programa.sinopticos,
                fuentes=programa.ftes_info_recomendadas,
                requisitos=programa.requisitos,
                estrategias_met=programa.estrategias_met,
                estrategias_eval=programa.estrategias_eval,
                justificacion=programa.justificacion,
                obj_general=programa.objetivos_generales,
                obj_especificos=programa.objetivos_especificos,
                observaciones=programa.observaciones,
                extras=extras
    )
    pdf = buffer.getvalue()
    buffer.close()

    header = {'Content-Type':'application/pdf'}
    response.headers.update(header)
    return pdf

def originalpdf():
    """
        Permite descargar le PDF original de programa. Habilitado solo para los programas que tienen un PDF historico.
        (Vienen de una Transcripcion.)
    """

    program_id = request.args(0)
    if not program_id:
        redirect(URL(c='default', f='not_authorized'))

    # Obtener el programa
    programa = db(db.PROGRAMA.id == program_id).select().first()

    if not programa:
        redirect(URL(c='default', f='not_authorized'))

    if programa.original_pdf:
        fullpath = os.path.join(request.folder,'static/transcriptions/originalpdf', programa.original_pdf)
        response.stream(os.path.join(request.folder, fullpath), headers  ={'Content-Disposition': 'filename= HISTORICO_%s.pdf'%(programa.codigo)})

    redirect(URL(c='default', f='not_authorized'))
