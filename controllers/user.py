
# Decorador solo para acceder a la vista si se ha iniciado sesion
@auth.requires_login()
def profile():
    # aqui va la logica para ver/actualizar el perfil

    mensaje = 'Bienvenido ' + auth.user.first_name + ' ' + auth.user.last_name
    usuario = auth.user

    db.auth_user.ci.writable = False
    db.auth_user.username.writable = False
    db.auth_user.email.writable = False
    form = SQLFORM(db.auth_user, fields = ['first_name', 'last_name', 'phone',
                                           'ci', 'username' ,'email'],
                   record = auth.user.id, showid = False, formstyle = 'bootstrap',
                   labels = {'username':'USBID', 'ci':'Cédula', 'phone':'Teléfono'})

    if form.process().accepted:
        response.flash = 'form accepted'
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill out the form'

    return dict(message = mensaje, form = form)
