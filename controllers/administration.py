
@auth.requires(auth.is_logged_in() and auth.has_permission('manage_users', 'auth_user') and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def log():

    message = "Registro de Eventos"

    return dict(message=message)
