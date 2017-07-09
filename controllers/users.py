import re

def get_roles():
    """
        Obtiene una lista de los roles creados en la base de datos.
    """

    roles      = db(db.auth_group).select()
    roles_list = []
    for role in roles:
        roles_list.append(role.role)
    return roles_list


# Decorador solo para acceder a la vista si se ha iniciado sesion
@auth.requires(auth.is_logged_in() and auth.has_permission('update_profile', 'auth_user') and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def profile():
    """
      La función perfil permite editar la información recopilada del CAS asociada
      al usuario en sesión.
    """

    mensaje = 'Bienvenido ' + auth.user.first_name + ' ' + auth.user.last_name

    db.auth_user.ci.writable = False
    db.auth_user.username.writable = False
    db.auth_user.email.writable = False
    form = SQLFORM(db.auth_user,
                   fields = ['first_name', 'last_name', 'phone', 'phone2', 'ci', 'username' ,'email'],
                   record = auth.user.id,
                   showid = False,
                   formstyle = 'bootstrap',
                   labels = {'username':'USBID', 'ci':'Cédula', 'phone':'Teléfono', 'phone2' : 'Teléfono Secundario'})

    if form.process().accepted:
        response.flash = 'Datos actualizados correctamente.'
    elif form.errors:
        response.flash = 'Existen errores en el formulario.'

    return dict(message = mensaje, form = form)

@auth.requires(auth.is_logged_in() and auth.has_permission('manage_users', 'auth_user') and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def filter():
    '''
      Vista previa a la consulta de usuarios, de manera de poder elegir si se quiere
      buscar por roles, sin mostrarlos todos, o si se quiere buscar por usuario.
    '''
    message = "Gestión de Usuarios"

    # Recolectamos la lista de todos los roles

    roles_list = ['TODOS']
    roles_list = roles_list + get_roles()

    # Formulario para buscar usuarios por rol
    formulario_rol = SQLFORM.factory(Field('rol', type="string",
                                  requires = IS_IN_SET(roles_list,
                                  error_message = 'Seleccione un Rol de Usuario.',
                                  zero = "Seleccione...")),
                           labels={'rol':'Rol'},
                           col3  ={'rol':'Seleccione un Rol para listar los usuarios.'})

    # Formulario para buscar usuarios por cedula
    formulario_ci = SQLFORM.factory(Field('cedula', type="string",
                                  requires = IS_MATCH(r'\b([0-9]){6,10}\b',
                                  error_message = 'Formato de cédula no válido.')),
                           labels={'cedula':'Cédula'},
                           col3  ={'cedula':'Ingrese una cédula en forma numérica sin puntos, por ejemplo: 12345678.'})

    # Si la búsqueda fue procesada correctamente se desplegará la lista de usuarios con el rol
    # en la búsqueda, o el usuario que coincida con la cédula buscada.
    if formulario_rol.process(formname="formulario_filtro_rol").accepted:
        redirect(URL(c='users', f='manage',args = [formulario_rol.vars.rol]))
    elif formulario_rol.errors:
        response.flash = 'Error en la búsqueda de Usuarios.'

    if formulario_ci.process(formname="formulario_filtro_cedula").accepted:
        redirect(URL(c='users', f='manage',args = [formulario_ci.vars.cedula]))
        response.flash = formulario_ci.vars.cedula
    elif formulario_ci.errors:
        response.flash = 'Error en la búsqueda de Usuarios.'

    return dict(message=message, formulario_rol = formulario_rol, formulario_ci = formulario_ci)

@auth.requires(auth.is_logged_in() and auth.has_permission('manage_users', 'auth_user') and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def manage():
    """
      Muestra la vista de usuarios según lo procesado en el filtro de búsqueda

    """

    # param: puede ser un rol o una cédula
    param =  request.args(0)

    # verificamos que llegue un elemento correcto mediante la url
    if not isinstance(param, str):
        redirect(URL(c='default', f='not_authorized'))

    usuarios = []

    message = "Gestión de Usuarios: %s"%(param)

    # Expresion regular para comprobar las cedulas
    pattern = re.compile(r'\b([0-9]){6,10}\b',)

    # asociación del usuario con la cédula
    if pattern.match(param):
        usuarios = db(db.auth_user.ci == param).select(db.auth_user.id,
                                                       db.auth_user.ci,
                                                       db.auth_user.username,
                                                       db.auth_user.first_name,
                                                       db.auth_user.last_name,
                                                       db.auth_user.email)

    # asociación con los roles
    elif param == "TODOS":

        usuarios = db(db.auth_user).select(db.auth_user.id,
                                           db.auth_user.ci,
                                           db.auth_user.username,
                                           db.auth_user.first_name,
                                           db.auth_user.last_name,
                                           db.auth_user.email)
    else:
        roles_list = get_roles()
        if not (param in roles_list):
            redirect(URL(c='default', f='not_authorized'))

        # obtenemos el id del grupo (rol)
        group_id = auth.id_group(role=param)

        # obtenemos los id de todos los usuarios dentro del rol
        all_users_in_group = db(db.auth_membership.group_id == group_id)._select(db.auth_membership.user_id)

        # Obtenemos los usuarios
        usuarios = db(db.auth_user.id.belongs(all_users_in_group)).select(db.auth_user.id,
                                                                          db.auth_user.ci,
                                                                          db.auth_user.username,
                                                                          db.auth_user.first_name,
                                                                          db.auth_user.last_name,
                                                                          db.auth_user.email)
    lista_usuarios = []

    # Obtenemos los roles de cada usuario
    for usuario in usuarios:
        roles =  db(db.auth_membership.user_id == usuario.id).select()
        nombresroles = ""
        for role in roles:
            nombresroles += role.group_id.role + '\n'

        lista_usuarios.append({'id' : usuario.id,
                               'username': usuario.username,
                               'ci'   : usuario.ci,
                               'name' : usuario.first_name + ' ' + usuario.last_name,
                               'email': usuario.email,
                               'roles': nombresroles})

    return dict(message=message, usuarios = lista_usuarios)


@auth.requires(auth.is_logged_in() and auth.has_permission('manage_users', 'auth_user') and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def edit():
    """
      Funcion para editar usuarios, sus roles asignados o por asignar, y datos personales.
    """


    idusuario = request.args(0)
    message   = "Editar usuario"

    db.auth_user.username.writable = False
    db.auth_user.email.writable = False

    # obtenemos todos los roles del usuario
    roles      = db(db.auth_membership.user_id == idusuario).select()
    roles_list = []
    for role in roles:
        roles_list.append({'id' : role.group_id, 'role' : role.group_id.role, 'mid' : role.id })

    primary_role = []

    # encontramos el rol primario, para deshabilitar que se pueda cambiar en la vista.
    if len(roles_list) == 1:
        primary_role = roles_list[0]
        roles_list = []

    else:
    # se listan los roles adicionales asigandos al usuario, en su defecto un campo vacio.
        min_id = roles_list[0]['mid']
        for i in range(1, len(roles_list)):
            if min_id > roles_list[i]['mid']:
                min_id = roles_list[i]['mid']

        roles_list_aux = []
        for i in roles_list:
            if i['mid'] == min_id:
                primary_role = i
            else:
                roles_list_aux.append(i)
        roles_list = roles_list_aux

    # Datos personales del usuario
    formulario_datos = SQLFORM(db.auth_user,
                   fields = ['first_name', 'last_name', 'phone', 'phone2', 'ci', 'username' ,'email'],
                   record = idusuario,
                   showid = False,
                   formstyle = 'bootstrap',
                   labels = {'username':'USBID', 'ci':'Cédula', 'phone':'Teléfono', 'phone2' : 'Teléfono Secundario'})

    # Formulario para asignar nuevo rol
    formulario_nuevo_rol = SQLFORM.factory(Field('new_rol', requires=IS_IN_DB(db,db.auth_group.id,
                                                               '%(role)s',
                                                               zero='Seleccione...',
                                                               error_message="Seleccione un rol")),
                            labels={'new_rol':'Agregar Rol'})

    # Formulario para cambiar un rol
    formulario_cambiar_rol = SQLFORM.factory(Field('new_rol', requires=IS_IN_DB(db,db.auth_group.id,
                                                               '%(role)s',
                                                               zero='Seleccione...',
                                                               error_message="Seleccione un rol")),
                                             Field('old_rol', type="string"),
                            labels={'new_rol':'Cambiar Rol'})

    if formulario_datos.process(formname="formulario_datos").accepted:
        response.flash = 'Datos actualizados correctamente.'
    elif formulario_datos.errors:
        response.flash = 'Existen errores en el formulario.'

    if formulario_nuevo_rol.process(formname="formulario_nuevo_rol").accepted:

        new_rol = request.vars.new_rol
        agregar  = True

        # si el rol es el de transcriptor, verificamos que pueda ser asignado
        # hay ciertos roles que no pueden ser transcriptores (Dpto./Coord./Decanato)
        idrole_transcriptor = auth.id_group(role="TRANSCRIPTOR")
        if int(new_rol) == int(idrole_transcriptor):
            roles      = db(db.auth_membership.user_id == idusuario).select(db.auth_membership.group_id)

            no_permitidos = [int(auth.id_group(role="DECANATO")),
                             int(auth.id_group(role="COORDINACION")),
                             int(auth.id_group(role="DEPARTAMENTO"))]
            for i in roles:
                if i['group_id'] in no_permitidos:
                    agregar = False
                    session.flash = 'Usuarios con rol de DECANATO, COORDINACION o DEPARTAMENTO no pueden transcribir programas.'

        if agregar:
            auth.add_membership(request.vars.new_rol, idusuario)
            session.flash = 'Nuevo rol agregado.'

        redirect(URL(c='users',f='edit',args=[idusuario]))

    elif formulario_nuevo_rol.errors:
        response.flash = 'Por favor seleccione un nuevo rol.'

    # cambiando roles
    if formulario_cambiar_rol.process(formname="formulario_cambiar_rol").accepted:
        auth.del_membership(request.vars.old_rol, idusuario)
        auth.add_membership(request.vars.new_rol, idusuario)

        # si el rol era el de transcriptor, se elimina al usuario como transcriptor
        # de su supervisor correspondiente
        idrole_transcriptor = auth.id_group(role="TRANSCRIPTOR")
        if int(request.vars.old_rol) == int(idrole_transcriptor):
            usuario = db(db.auth_user.id == idusuario).select().first()
            registro = db(db.REGISTRO_TRANSCRIPTORES.transcriptor == usuario.username).delete()

        response.flash = 'Rol cambiado.'
        redirect(URL(c='users',f='edit',args=[idusuario]))
    elif formulario_cambiar_rol.errors:
        response.flash = 'Por favor seleccione un nuevo rol.'

    return dict(message = message,
                formulario_datos = formulario_datos,
                formulario_nuevo_rol = formulario_nuevo_rol,
                formulario_cambiar_rol = formulario_cambiar_rol,
                primary_role = primary_role,
                roles_list = roles_list,
                idusuario = idusuario)


@auth.requires(auth.is_logged_in() and auth.has_permission('manage_users', 'auth_user') and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def deleterole():
  """
    Eliminación de roles de un usuario
  """
    idusuario = request.args(0)
    idrole    = request.args(1)

    auth.del_membership(idrole, idusuario)

    # si el rol era el de transcriptor, lo eliminamos como transcriptor
    # para su supervisor correspondiente.
    idrole_transcriptor = auth.id_group(role="TRANSCRIPTOR")
    if int(idrole) == int(idrole_transcriptor):
        usuario = db(db.auth_user.id == idusuario).select().first()
        registro = db(db.REGISTRO_TRANSCRIPTORES.transcriptor == usuario.username).delete()

    redirect(URL(c='users',f='edit',args=[idusuario]))
