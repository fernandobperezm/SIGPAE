@auth.requires(auth.is_logged_in() and auth.has_permission('manage_users', 'auth_user') and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def log():
    """
        Inicio en la vista de la bitácora.
    """

    message = "Registro de Eventos"

    # Obtenemos los registros de la bitácora para la transcripcion
    registros = db(db.LOG_SIGPAE).select()

    return dict(message = message, registros = registros)
