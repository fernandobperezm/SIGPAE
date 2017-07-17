
@auth.requires(auth.is_logged_in() and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def index():
	"""
		Inicio en la vista de ayuda.
	"""

	message = "Ayuda"

	return dict(message=message)
