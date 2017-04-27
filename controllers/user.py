
# Decorador solo para acceder a la vista si se ha iniciado sesion
@auth.requires_login()
def profile():
    # aqui va la logica para ver/actualizar el perfil

    mensaje = 'Bienvenido ' + auth.user.first_name + ' ' + auth.user.last_name
    usuario = auth.user
    
    return dict(message = mensaje, usuario = usuario)
