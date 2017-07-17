import urllib2
import json
import re
import cStringIO
from pdf_generator import generatePDF


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


@auth.requires(auth.is_logged_in() and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def view():

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
    cod = request.args(0)
    if not cod:
        redirect(URL(c='default', f='not_authorized'))

    programa = db(db.PROGRAMA.id == cod).select().first()
    print programa.anio

    buffer = cStringIO.StringIO()
    generatePDF(buffer=buffer,
                request=request,
                cod=programa.codigo,
                division="Falta obtener esto",
                depto="Falta obtener esto",
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
                observaciones=programa.observaciones
    )
    pdf = buffer.getvalue()
    buffer.close()
    print(programa.objetivos_especificos)

    header = {'Content-Type':'application/pdf'}
    response.headers.update(header)
    return pdf