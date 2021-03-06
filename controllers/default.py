# -*- coding: utf-8 -*-

from   usbutils import get_ldap_data, random_key
from   logs     import *
import urllib2
import json

def reroute():
    """
    Funcion utilizada para que nos lleve al index aunque estemos en la pagina
    por defecto de web2py
    """
    redirect(URL('index'))

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html
    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """

    if auth.has_membership(auth.id_group(role="INACTIVO")):
        redirect(URL(c='default', f='inactive'))

    response.flash = T("¡Bienvenido al SIGPAE!")

    message = 'Sistema de Gestión de Planes Académicos de Estudio'

    # formulario de busqueda publica
    departamentos = []

    try:
        page = urllib2.urlopen('http://127.0.0.1:8000/SIGPAE_WS/default/webservices/departamentos/').read()
        departments =  json.loads(page, "ascii")
        for department in departments:
            departamentos.append(('%s (%s)'%(department['nombre'], department['siglas_depto'])).encode('ascii','ignore'))

    except urllib2.URLError as e:
        return dict(message=T('Sistema de Gestión de Planes Académicos de Estudio'))

    form_busqueda = SQLFORM.factory(Field('departamento', type="string",
                                          requires = IS_EMPTY_OR(IS_IN_SET(departamentos,
                                          error_message = 'Seleccione un Rol de Usuario.',
                                          zero = "Seleccione..."))),
                                    Field('codigo', type="string"),
                                    Field('denominacion', type="string"),
                                    labels={'departamento':'Departamento',
                                            'codigo' : 'Código',
                                            'denominacion' : 'Denominación'},
                                    col3 = {'denominacion' : 'Nombre de la Asignatura.'})

    if form_busqueda.process(formname='form_busqueda').accepted:
        response.flash = "Accepted!"
        redirect(URL(c='default', f='search_results', vars=form_busqueda.vars))

    if form_busqueda.errors:
        pass

    return dict(message=message, form_busqueda =  form_busqueda)

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """

    # Redireccionamos las entradas para la parte superior, pues estamos usando una autenticacion distinta (CAS).

    if request.args(0)=='login':
        redirect('https://secure.dst.usb.ve/login?service=' + settings.returnurl)
    if request.args(0)=='logout':
        redirect(URL(c='default',f='logout'))
    if request.args(0)=='profile':
        redirect(URL(c='users',f='profile'))
    if request.args(0)=='not_authorized':
        redirect(URL(c='default', f='not_authorized'))
    if request.args(0) in ['register','retrieve_password','change_password', 'bulk_register']:
        redirect(URL(c='default',f='index'))

    return dict(form=auth())

def login_cas():
    """
        Establece el loggeo de los usuarios a traves del sistema CAS. Si el usuario
        no existe en la base de datos, se registra.
    """

    if not request.vars.getfirst('ticket'):
        pass
    try:
        import urllib2, ssl
        ssl._create_default_https_context = ssl._create_unverified_context


        # url para iniciar sesion
        url = "https://secure.dst.usb.ve/validate?ticket=" +\
              request.vars.getfirst('ticket') + "&service=" + settings.returnurl

        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        the_page = response.read()

    except Exception, e:
        redirect(URL('error'))

    if the_page[0:2] == "no":
        redirect(URL('index'))
    else:

        # session.casticket = request.vars.getfirst('ticket')
        data  = the_page.split()
        usbid = data[1]

        usuario = get_ldap_data(usbid) #Se leen los datos del CAS

        tabla_usuario  = db.auth_user

        #Esto nos indica si el usuario ha ingresado alguna vez al sistema
        #buscandolo en la tabla de usuario.
        primeravez = db(tabla_usuario.username == usbid)

        if primeravez.isempty():

            # registrar al usuario
            authUserId  = registrar(usuario, auth)

            # obtenemos los datos para iniciar sesion
            datos_usuario = db(tabla_usuario.username == usbid).select()[0]
            clave         = datos_usuario.access_key

            # inicio de sesion y redireccion
            auth.login_bare(usbid, clave)

            # registro en el log
            regiter_in_log(db, auth, 'REGISTRO', 'Registro como nuevo usuario.')

            redirect(URL(c='default',f='index'))


        else:

            #Como el usuario ya esta registrado, buscamos sus datos y lo logueamos.
            datos_usuario = db(tabla_usuario.username == usbid).select()[0]
            clave         = datos_usuario.access_key

            auth.login_bare(usbid, clave)

            # respuesta = Usuario.getByRole(auth.user.id)

            redirect(URL(c='default',f='index'))

    return None

def logout():
    """
        Redirecciona al usuario al finalizar sesión en el sistema.
    """

    url = 'http://secure.dst.usb.ve/logout'
    auth.logout(next = url)

def registrar(usuario, auth):
    """
        Una vez el usuario inicia sesión, extrae la información asociada a su id,
        provista por el CAS, para llenar los campos de perfil del usuario.
    """

    nombre = usuario['first_name']
    apellido = usuario['last_name']
    tipo  = usuario['tipo']
    email = usuario['email']
    cedula  = usuario['cedula']
    phone = usuario['phone']
    usbid = usuario['email'].split('@')[0]
    clave = random_key()

    try:
    	auth_user_id = db.auth_user.insert(
                                 first_name = nombre,
    							 last_name  = apellido,
    							 username = usbid,
                                 email = email,
                                 access_key = clave,
                                 ci = cedula,
                                 phone = phone,
    							 password = db.auth_user.password.validate(clave)[0])

        # Agregando roles por defecto.
        if tipo == 'Pregrado':
            auth.add_membership(auth.id_group(role="ESTUDIANTE"), auth_user_id)
        if tipo == 'Docente':
            auth.add_membership(auth.id_group(role="PROFESOR"), auth_user_id)

    	return auth_user_id

    except Exception as e:
        pass

    return dict( message = usuario)

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()

@auth.requires_login()
def not_authorized():
    """
        Expose a custom page for not authorization areas.
    """
    message = "Área no autorizada"
    return dict(message=message)

@auth.requires_login()
def inactive():
    """
        Expose a custom page for inactive users.
    """
    message = "Usuario Inactivo"
    return dict(message=message)

def search_results():
    '''
        Muestra los resultados de la busqueda publica o general
    '''

    message = 'Resultados de Búsqueda'

    subjects = []

    if request.vars.departamento:
        #Extraemos las siglas del departamento
        siglas  = request.vars.departamento[-3:-1]

        if not(request.vars.codigo) and not(request.vars.denominacion):
            subjects = db(db.PROGRAMA.codigo.startswith(siglas)).select()
        else:
            if request.vars.codigo and not(request.vars.denominacion):
                subjects = db((db.PROGRAMA.codigo.startswith(siglas)) &
                              (db.PROGRAMA.codigo.contains(request.vars.codigo, case_sensitive=False))).select()
            if request.vars.denominacion and not(request.vars.codigo):
                subjects = db((db.PROGRAMA.codigo.startswith(siglas)) &
                              (db.PROGRAMA.denominacion.contains(request.vars.denominacion, case_sensitive=False))).select()
            if request.vars.codigo and request.vars.denominacion:
                subjects = db((db.PROGRAMA.codigo.startswith(siglas)) &
                              (db.PROGRAMA.codigo.contains(request.vars.codigo, case_sensitive=False)) &
                              (db.PROGRAMA.denominacion.contains(request.vars.denominacion, case_sensitive=False))).select()
    else:
        if request.vars.codigo and not(request.vars.denominacion):
            subjects = db(db.PROGRAMA.codigo.contains(request.vars.codigo, case_sensitive=False)).select()
        if request.vars.denominacion and not(request.vars.codigo):
            subjects = db(db.PROGRAMA.denominacion.contains(request.vars.denominacion, case_sensitive=False)).select()
        if request.vars.codigo and request.vars.denominacion:
            subjects = db((db.PROGRAMA.codigo.contains(request.vars.codigo, case_sensitive=False)) &
                          (db.PROGRAMA.denominacion.contains(request.vars.denominacion, case_sensitive=False))).select()

    return dict(message = message, subjects =  subjects)
