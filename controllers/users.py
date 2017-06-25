
# Decorador solo para acceder a la vista si se ha iniciado sesion
@auth.requires(auth.is_logged_in() and auth.has_permission('update_profile', 'auth_user') and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def profile():
    # aqui va la logica para ver/actualizar el perfil

    mensaje = 'Bienvenido ' + auth.user.first_name + ' ' + auth.user.last_name

    db.auth_user.ci.writable = False
    db.auth_user.username.writable = False
    db.auth_user.email.writable = False
    form = SQLFORM(db.auth_user,
                   fields = ['first_name', 'last_name', 'phone','ci', 'username' ,'email'],
                   record = auth.user.id,
                   showid = False,
                   formstyle = 'bootstrap',
                   labels = {'username':'USBID', 'ci':'Cédula', 'phone':'Teléfono'})

    if form.process().accepted:
        response.flash = 'Datos actualizados correctamente.'
    elif form.errors:
        response.flash = 'Existen errores en el formulario.'

    return dict(message = mensaje, form = form)

@auth.requires(auth.is_logged_in() and auth.has_permission('manage_users', 'auth_user') and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def manage():

    message = "Gestión de Usuarios"

    # Obtenemos los usuarios
    usuarios = db(db.auth_user).select(db.auth_user.id,
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
                               'name' : usuario.first_name + ' ' + usuario.last_name,
                               'email': usuario.email,
                               'roles': nombresroles})

    return dict(message=message, usuarios = lista_usuarios)


@auth.requires(auth.is_logged_in() and auth.has_permission('manage_users', 'auth_user') and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def edit():
    idusuario = request.args(0)
    message   = "Editar usuario"

    db.auth_user.username.writable = False
    db.auth_user.email.writable = False

    #we get the roles for the user
    roles      = db(db.auth_membership.user_id == idusuario).select()
    roles_list = []
    for role in roles:
        roles_list.append({'id' : role.group_id, 'role' : role.group_id.role })

    # Datos personales del usuario
    formulario_datos = SQLFORM(db.auth_user,
                   fields = ['first_name', 'last_name', 'phone','ci', 'username' ,'email'],
                   record = idusuario,
                   showid = False,
                   formstyle = 'bootstrap',
                   labels = {'username':'USBID', 'ci':'Cédula', 'phone':'Teléfono'})

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
        auth.add_membership(request.vars.new_rol, idusuario)
        response.flash = 'Nuevo rol agregado.'
        redirect(URL(c='users',f='edit',args=[idusuario]))
    elif formulario_nuevo_rol.errors:
        response.flash = 'Por favor seleccione un nuevo rol.'

    if formulario_cambiar_rol.process(formname="formulario_cambiar_rol").accepted:
        auth.del_membership(request.vars.old_rol, idusuario)
        auth.add_membership(request.vars.new_rol, idusuario)
        response.flash = 'Nuevo rol agregado.'
        redirect(URL(c='users',f='edit',args=[idusuario]))
    elif formulario_cambiar_rol.errors:
        response.flash = 'Por favor seleccione un nuevo rol.'

    return dict(message = message,
                formulario_datos = formulario_datos,
                formulario_nuevo_rol = formulario_nuevo_rol,
                formulario_cambiar_rol = formulario_cambiar_rol,
                roles_list = roles_list,
                idusuario = idusuario)


@auth.requires(auth.is_logged_in() and auth.has_permission('manage_users', 'auth_user') and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def deleterole():
    idusuario = request.args(0)
    idrole    = request.args(1)

    auth.del_membership(idrole, idusuario)

    redirect(URL(c='users',f='edit',args=[idusuario]))
