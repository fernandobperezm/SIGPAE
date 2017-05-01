
# Decorador solo para acceder a la vista si se ha iniciado sesion
@auth.requires_login()
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
    else:
        response.flash = 'Por favor llene el formulario.'

    return dict(message = mensaje, form = form)

@auth.requires(auth.is_logged_in() and auth.has_permission('manage_users', 'auth_user'))
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
