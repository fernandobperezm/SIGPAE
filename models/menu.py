response.title       = settings.title
response.subtitle    = settings.subtitle
response.meta.author = '%(author)s <%(author_email)s>' % settings
response.meta.keywords    = settings.keywords
response.meta.description = settings.description

DEVELOPMENT_MENU = True

# Menu de autenticacion

if auth.is_logged_in():
    texto_principal = "Bienvenido, " + auth.user.first_name
else:
    texto_principal = "Bienvenido"

opciones = [
    ((SPAN(_class='fa fa-user'), '  Ver Perfil'), False, URL('users', 'profile')),
    ((SPAN(_class='fa fa-question-circle'), '  Ayuda'), False, URL('help', 'index')),
    ((SPAN(_class='fa fa-sign-out'), '  Cerrar Sesión'), False, URL('default', 'logout'))
]

opciones_inactivo = [
    ((SPAN(_class='fa fa-sign-out'), '  Cerrar Sesión'), False, URL('default', 'logout'))
]

manejo_administrador = [
    ((SPAN(_class='fa fa-archive'), '  Registro de Eventos'), False, URL('administration', 'log')),
]

manejo_usuarios = [
    ((SPAN(_class='fa fa-user'), '  Gestionar Usuarios'), False, URL('users', 'filter')),
]

crear_transcripciones = [
    ((SPAN(_class='fa fa-file-text-o'), ' Nueva Transcripción'), False, URL('transcriptions', 'add')),
    ((SPAN(_class='fa fa-files-o'), '  Transcripciones en Curso'), False, URL('transcriptions', 'list')),
    ((SPAN(_class='fa fa-clock-o '), '  Transcripciones en Revisión'), False, URL('transcriptions', 'list_sent')),
]

manejar_transcripciones = [
    ((SPAN(_class='fa fa-user'), '  Transcriptores'), False, URL('transcriptions', 'transcriptors')),
    ((SPAN(_class='fa fa-eye'), '  Seguimiento de Transcripciones'), False, URL('transcriptions', 'following')),
    ((SPAN(_class='fa fa-clock-o'), '  Transcripciones por Revisión'), False, URL('transcriptions', 'list_pending')),
    ((SPAN(_class='fa fa-check'), '  Transcripciones Aprobadas'), False, URL('transcriptions', 'list_approved')),
]

consultar_programas = [
    ((SPAN(_class='fa fa-file-powerpoint-o'), '  Listar Programas'), False, URL('programs', 'list')),
]

queries = [
    ((SPAN(_class='fa fa-chevron-down'), '  Departamentos'), False, URL('queries', 'departments')),
    ((SPAN(_class='fa fa-chevron-down'), '  Asignaturas'),   False, URL('queries', 'subjects')),
    ((SPAN(_class='fa fa-chevron-down'), '  Carreras'),   False, URL('queries', 'careers')),
    ((SPAN(_class='fa fa-chevron-down'), '  Estudiantes'),   False, URL('queries', 'students')),
]

# Tomado de SPE. Adecuar en futuro de acuerdo a los roles y permisologia definida
# opciones_estudiante = [
#     ((SPAN(_class='fa fa-user'), '  Ver Perfil'), False, '/SPE/mi_perfil/ver'),
#     ((SPAN(_class='fa fa-list'), '  Mis Pasantias'), False, '/SPE/mis_pasantias/listar'),
#     ((SPAN(_class='fa fa-cog'), '  Configuración '), False, '/SPE/mi_perfil/configuracion'),
#     ((SPAN(_class='fa fa-sign-out'), '  Cerrar Sesión'), False, URL('default', 'logout'))
# ]
#
# opciones_coordinadorCCT = [
#     ((SPAN(_class='fa fa-user'), '  Ver Perfil'), False, '/SPE/mi_perfil/ver'),
#     ((SPAN(_class='fa fa-list'), '  Administracion'), False, '/SPE/pasantias/listar'),
#     ((SPAN(_class='fa fa-cog'), '  Configuración'), False, '/SPE/mi_perfil/configuracion'),
#     ((SPAN(_class='fa fa-sign-out'), '  Cerrar Sesión'), False, URL('default', 'logout'))
# ]
#
# opciones_coordinador = [
#     ((SPAN(_class='fa fa-user'), '  Ver Perfil'), False, '/SPE/mi_perfil/ver'),
#     ((SPAN(_class='fa fa-list'), '  Mis Pasantias'), False, '/SPE/Coordinador/consultarPasantias'),
#     ((SPAN(_class='fa fa-cog'), '  Configuración'), False, '/SPE/mi_perfil/configuracion'),
#     ((SPAN(_class='fa fa-sign-out'), '  Cerrar Sesión'), False, URL('default', 'logout'))
# ]
#
# opciones_profesor = [
#     ((SPAN(_class='fa fa-user'), '  Ver Perfil'), False, '/SPE/mi_perfil/ver'),
#     ((SPAN(_class='fa fa-list'), '  Mis Pasantias'), False, '/SPE/mis_pasantias_tutor/listar'),
#     ((SPAN(_class='fa fa-cog'), '  Configuración'), False, '/SPE/mi_perfil/configuracion'),
#     ((SPAN(_class='fa fa-sign-out'), '  Cerrar Sesión'), False, URL('default', 'logout'))
# ]
#
# if auth.has_membership(role='CoordinadorCCT'):
#     opciones = opciones_coordinadorCCT
# elif auth.has_membership(role='Estudiante'):
#     opciones = opciones_estudiante
# elif auth.has_membership(role='Profesor'):
#     opciones = opciones_profesor
# elif auth.has_membership(role='Coordinador'):
#     opciones = opciones_coordinador

menu_autenticado = [
    (texto_principal, False, '#', opciones)
]

menu_opciones_rol = []

if auth.has_permission('manage_users', 'auth_user'):
    menu_opciones_rol.append(('Administración', False, '#', manejo_administrador ))
    menu_opciones_rol.append(('Usuarios', False, '#', manejo_usuarios ))
    menu_opciones_rol.append(('Consultas', False, '#', queries ))


# agrega consulta de programas para todos los usuarios
if not(auth.has_membership(auth.id_group(role="INACTIVO"))):
    menu_opciones_rol.append(('Programas', False, '#', consultar_programas))

if auth.has_permission('create_transcription'):
    menu_opciones_rol.append(('Transcripciones', False, '#', crear_transcripciones))

if auth.has_permission('manage_transcription'):
    menu_opciones_rol.append(('Transcripciones', False, '#', manejar_transcripciones))



response.menu = [
    (T('Iniciar Sesión'), False , 'https://secure.dst.usb.ve/login?service=' + settings.returnurl, []),
]

if auth.has_membership(auth.id_group(role="INACTIVO")):

    menu_autenticado = [
        (texto_principal, False, '#', opciones_inactivo)
    ]

    menu_opciones_rol = []
