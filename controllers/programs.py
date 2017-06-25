
@auth.requires(auth.is_logged_in() and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def list():

    message = "Programas Analíticos de Estudio"

    return dict(message=message)
