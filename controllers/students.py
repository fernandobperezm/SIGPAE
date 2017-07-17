import urllib2
import json
import re

@auth.requires(auth.is_logged_in() and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def list():
    """
        Inicio en la vista consulta de programas analiticos aprobados por el estudiante.
    """

    message = "Programas Analíticos de Estudio de Asignaturas Aprobadas"

    try:
        page = urllib2.urlopen('http://127.0.0.1:8000/SIGPAE_WS/default/webservices/estudiantes/asig-aprobadas/?carnet=%s'%(auth.user.username)).read()
        aproved_subjects = json.loads(page)
    except urllib2.URLError as e:
        response.flash = 'Error de conexión con el Web Service.'
        return dict(message=message, error = e.reason, aproved_subjects = [])

    return dict(message=message, aproved_subjects = aproved_subjects)
