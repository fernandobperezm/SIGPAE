# -*- coding: utf-8 -*-

from usbutils import get_ldap_data, random_key

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

    return dict(message=T('Sistema de Gestión de Planes Académicos de Estudio'))

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

    if not request.vars.getfirst('ticket'):
        print 'pass!'
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
        print e
        redirect(URL('error'))

    if the_page[0:2] == "no":
        redirect(URL('index'))
    else:

        # session.casticket = request.vars.getfirst('ticket')
        data  = the_page.split()
        usbid = data[1]

        print "usbid ", usbid

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
    url = 'http://secure.dst.usb.ve/logout'
    auth.logout(next = url)

def registrar(usuario, auth):

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

        #Agregando roles por defecto
        if tipo == 'Pregrado':
            auth.add_membership(auth.id_group(role="ESTUDIANTE"), auth_user_id)
        if tipo == 'Docente':
            auth.add_membership(auth.id_group(role="PROFESOR"), auth_user_id)

    	return auth_user_id

    except Exception as e:
    	print 'ERROR: ',
    	print e

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
