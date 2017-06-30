# webservices test
import urllib2
import json

@auth.requires(auth.is_logged_in() and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def departments():
    message = "Departamentos"

    try:
        page = urllib2.urlopen('http://127.0.0.1:8080/webservices/departamentos/').read()
        departments =  json.loads(page)
    except urllib2.URLError as e:
        response.flash = 'Error de conexión con el Web Service.'
        return dict(message=message, error = e.reason, departments = {})

    return dict(message=message, departments = departments)

@auth.requires(auth.is_logged_in() and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def subjects():
    message = "Asignaturas"

    try:
        page = urllib2.urlopen('http://127.0.0.1:8080/webservices/asignaturas/').read()
        subjects =  json.loads(page)
    except urllib2.URLError as e:
        response.flash = 'Error de conexión con el Web Service.'
        return dict(message=message, error = e.reason, subjects = {})

    return dict(message=message, subjects = subjects)

@auth.requires(auth.is_logged_in() and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def subjectdetail():
    cod =  request.args(0)
    if not isinstance(cod, str):
        redirect(URL(c='default', f='not_authorized'))

    message =  "Asignatura %s"%(cod)

    try:
        page = urllib2.urlopen('http://127.0.0.1:8080/webservices/asignaturas/%s/'%(cod)).read()
        subject = json.loads(page)
        if len(subject) > 0:
            subject = subject[0]
    except urllib2.URLError as e:
        response.flash = 'Error de conexión con el Web Service.'
        return dict(message=message, error = e.reason, subject = [])

    return dict(message=message, subject = subject)

@auth.requires(auth.is_logged_in() and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def careers():
    message = "Carreras"

    try:
        page = urllib2.urlopen('http://127.0.0.1:8080/webservices/carreras/').read()
        careers =  json.loads(page)
    except urllib2.URLError as e:
        response.flash = 'Error de conexión con el Web Service.'
        return dict(message=message, error = e.reason, careers = {})

    return dict(message=message, careers = careers)

@auth.requires(auth.is_logged_in() and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def students():
    message = "Estudiantes"

    # formulario para nuevos transcriptores
    form = SQLFORM.factory(Field('carnet', type="string",
                                  requires = IS_MATCH(r'\b([0-9]){2}-([0-9]){5}\b',
                                  error_message = 'Formato de carnet no válido.')),
                           labels={'carnet':'Carnet'},
                           col3  ={'carnet':'Ingrese un carnet de la forma XX-XXXXX'})

    if form.process(formname="formulario_carnet").accepted:
        redirect(URL(c='webservices', f='studentdetail',args = [form.vars.carnet]))
    elif form.errors:
        response.flash = 'Carnet no válido.'

    return dict(form=form, message = message)

@auth.requires(auth.is_logged_in() and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def studentdetail():
    carnet =  request.args(0)
    if not isinstance(carnet, str):
        redirect(URL(c='default', f='not_authorized'))

    message =  "Estudiante #%s"%(carnet)

    try:
        page = urllib2.urlopen('http://127.0.0.1:8080/webservices/estudiantes/%s/'%(carnet)).read()
        student_data = json.loads(page)
        if len(student_data) > 0:
            student_data = student_data[0]
    except urllib2.URLError as e:
        response.flash = 'Error de conexión con el Web Service.'
        return dict(message=message, error = e.reason, student_data = [], aproved_subjects = [])

    try:
        page = urllib2.urlopen('http://127.0.0.1:8080/webservices/estudiantes/%s/asig-aprobadas/'%(carnet)).read()
        aproved_subjects = json.loads(page)
    except urllib2.URLError as e:
        response.flash = 'Error de conexión con el Web Service.'
        return dict(message=message, error = e.reason, student_data = [], aproved_subjects = [])

    return dict(message=message, student_data = student_data, aproved_subjects = aproved_subjects)

@auth.requires(auth.is_logged_in() and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def departmentsubjects():
    cod =  request.args(0)
    if not isinstance(cod, str):
        redirect(URL(c='default', f='not_authorized'))

    message =  "Asignaturas del Departamento %s"%(cod)

    try:
        page = urllib2.urlopen('http://127.0.0.1:8080/webservices/asignaturas?siglas_depto=%s'%(cod)).read()
        subjects = json.loads(page)
    except urllib2.URLError as e:
        response.flash = 'Error de conexión con el Web Service.'
        return dict(message=message, error = e.reason, subjects = [])

    return dict(message=message, subjects = subjects)

@auth.requires(auth.is_logged_in() and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def careersubjects():
    cod =  request.args(0)
    if not isinstance(cod, str):
        redirect(URL(c='default', f='not_authorized'))

    message =  "Asignaturas de la Carrera %s"%(cod)

    try:
        page = urllib2.urlopen('http://127.0.0.1:8080/webservices/asignaturas?cod_carrera=%s'%(cod)).read()
        subjects = json.loads(page)
    except urllib2.URLError as e:
        response.flash = 'Error de conexión con el Web Service.'
        return dict(message=message, error = e.reason, subjects = [])

    return dict(message=message, subjects = subjects)
