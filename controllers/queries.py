import urllib2
import json
import re

@auth.requires(auth.is_logged_in() and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def departments():
    """
        Consulta a través de web services de los departamentos.
    """


    message = "Departamentos"

    try:
        page = urllib2.urlopen('http://127.0.0.1:8000/SIGPAE_WS/default/webservices/departamentos/').read()
        departments =  json.loads(page)
    except urllib2.URLError as e:
        response.flash = 'Error de conexión con el Web Service.'
        return dict(message=message, error = e.reason, departments = {})

    return dict(message=message, departments = departments)

@auth.requires(auth.is_logged_in() and auth.has_permission('manage_users', 'auth_user') and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def subjects():
    """
        Consulta a través de web services de las asignaturas.
    """
    message = "Asignaturas"

    try:
        page = urllib2.urlopen('http://127.0.0.1:8000/SIGPAE_WS/default/webservices/asignaturas/').read()
        subjects =  json.loads(page)
    except urllib2.URLError as e:
        response.flash = 'Error de conexión con el Web Service.'
        return dict(message=message, error = e.reason, subjects = {})

    return dict(message=message, subjects = subjects)

'''
    No requiere permiso especial, pues se trata de una vista que puede ser consultada publicamente.
'''
def subjectdetail():
    """
        Detalla caracteristicas de la asignatura, numero de creditos, horas asignadas
        y fecha de creación.
    """

    cod =  request.args(0)
    if not isinstance(cod, str):
        redirect(URL(c='default', f='not_authorized'))

    message =  "Asignatura %s"%(cod)

    try:
        page = urllib2.urlopen('http://127.0.0.1:8000/SIGPAE_WS/default/webservices/asignaturas/%s/'%(cod)).read()
        subject = json.loads(page)
        if len(subject) > 0:
            subject = subject[0]
    except urllib2.URLError as e:
        response.flash = 'Error de conexión con el Web Service.'
        return dict(message=message, error = e.reason, subject = [])

    programas = []
    # obtenemos los programas disponibles
    if subject:
        codigo = subject['cod_asignatura']
        programas = db(db.PROGRAMA.codigo == codigo).select(db.PROGRAMA.id,
                                                            db.PROGRAMA.periodo,
                                                            db.PROGRAMA.anio,
                                                            db.PROGRAMA.periodo_hasta,
                                                            db.PROGRAMA.anio_hasta)

    return dict(message=message, subject = subject, programas =programas)

@auth.requires(auth.is_logged_in() and auth.has_permission('manage_users', 'auth_user') and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def careers():
    """
        Consulta a través de web services de carreras.
    """

    message = "Carreras"

    try:
        page = urllib2.urlopen('http://127.0.0.1:8000/SIGPAE_WS/default/webservices/carreras/').read()
        careers =  json.loads(page)
    except urllib2.URLError as e:
        response.flash = 'Error de conexión con el Web Service.'
        return dict(message=message, error = e.reason, careers = {})

    return dict(message=message, careers = careers)

@auth.requires(auth.is_logged_in() and auth.has_permission('manage_users', 'auth_user') and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def students():
    """
        Consulta a través de web services de los estudiantes.
        La búsqueda es realizada por número de cédula o por carnet.
    """

    message = "Estudiantes"

    # formulario para buscar Estudiantes por cédula o carnet, validando a través de una expresión regular
    # si la cédula o carnet son válidos.
    form = SQLFORM.factory(Field('param', type="string",
                                  requires = IS_MATCH(r'\b([0-9]){2}-([0-9]){5}\b|\b([0-9]{6,10})\b',
                                  error_message = 'Formato de carnet o cédula no válido.')),
                           labels={'param':'Carnet o Cédula'},
                           col3  ={'param':'Ingrese un carnet de la forma XX-XXXXX o una cédula en forma numérica sin puntos, por ejemplo: 12345678.'})

    if form.process(formname="formulario_carnet").accepted:
        redirect(URL(c='queries', f='studentdetail',args = [form.vars.param]))
    elif form.errors:
        response.flash = 'Carnet o Cédula no válido.'

    return dict(form=form, message = message)

@auth.requires(auth.is_logged_in() and auth.has_permission('manage_users', 'auth_user') and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def studentdetail():
    """
        Consulta relacionada con las asignaturas aproubadas por un estudiante.
    """
    identificador =  request.args(0)
    if not isinstance(identificador, str):
        redirect(URL(c='default', f='not_authorized'))

    message =  "Datos del Estudiante"

    # en caso de haber pasado un carnet, verificamos que sea válido
    pattern_carnet = re.compile(r'\b([0-9]){2}-([0-9]){5}\b')

    if pattern_carnet.match(identificador):
        try:
            page = urllib2.urlopen('http://127.0.0.1:8000/SIGPAE_WS/default/webservices/estudiantes?carnet=%s'%(identificador)).read()
            student_data = json.loads(page)
            if len(student_data) > 0:
                student_data = student_data[0]
        except urllib2.URLError as e:
            response.flash = 'Error de conexión con el Web Service.'
            return dict(message=message, error = e.reason, student_data = [], aproved_subjects = [])

        try:
            page = urllib2.urlopen('http://127.0.0.1:8000/SIGPAE_WS/default/webservices/estudiantes/asig-aprobadas/?carnet=%s'%(identificador)).read()
            aproved_subjects = json.loads(page)
        except urllib2.URLError as e:
            response.flash = 'Error de conexión con el Web Service.'
            return dict(message=message, error = e.reason, student_data = [], aproved_subjects = [])

        return dict(message=message, student_data = student_data, aproved_subjects = aproved_subjects)

    # en caso contrario, se trata de una cedula
    else:
        try:
            page = urllib2.urlopen('http://127.0.0.1:8000/SIGPAE_WS/default/webservices/estudiantes?cedula=%s'%(identificador)).read()
            student_data = json.loads(page)
            if len(student_data) > 0:
                student_data = student_data[0]
        except urllib2.URLError as e:
            response.flash = 'Error de conexión con el Web Service.'
            return dict(message=message, error = e.reason, student_data = [], aproved_subjects = [])

        carnet = student_data['carnet']

        try:
            page = urllib2.urlopen('http://127.0.0.1:8000/SIGPAE_WS/default/webservices/estudiantes/asig-aprobadas/?carnet=%s'%(carnet)).read()
            aproved_subjects = json.loads(page)
        except urllib2.URLError as e:
            response.flash = 'Error de conexión con el Web Service.'
            return dict(message=message, error = e.reason, student_data = [], aproved_subjects = [])

        return dict(message=message, student_data = student_data, aproved_subjects = aproved_subjects)


@auth.requires(auth.is_logged_in() and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def departmentsubjects():
    """
        Consulta a través de web services de las asignaturas por departamento.
    """

    cod =  request.args(0)
    if not isinstance(cod, str):
        redirect(URL(c='default', f='not_authorized'))

    message =  "Asignaturas del Departamento %s"%(cod)

    try:
        page = urllib2.urlopen('http://127.0.0.1:8000/SIGPAE_WS/default/webservices/asignaturas?siglas_depto=%s'%(cod)).read()
        subjects = json.loads(page)
    except urllib2.URLError as e:
        response.flash = 'Error de conexión con el Web Service.'
        return dict(message=message, error = e.reason, subjects = [])

    return dict(message=message, subjects = subjects)

@auth.requires(auth.is_logged_in() and auth.has_permission('manage_users', 'auth_user') and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def careersubjects():
    """
        Consulta a través de web services de las asignaturas por carrera.
    """

    cod =  request.args(0)
    if not isinstance(cod, str):
        redirect(URL(c='default', f='not_authorized'))

    message =  "Asignaturas de la Carrera %s"%(cod)

    try:
        page = urllib2.urlopen('http://127.0.0.1:8000/SIGPAE_WS/default/webservices/asignaturas?cod_carrera=%s'%(cod)).read()
        subjects = json.loads(page)
    except urllib2.URLError as e:
        response.flash = 'Error de conexión con el Web Service.'
        return dict(message=message, error = e.reason, subjects = [])

    return dict(message=message, subjects = subjects)
