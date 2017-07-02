# -*- coding: utf-8 -*-
import datetime

# -------------------------------------------------------------------------
# This scaffolding model makes your app work on Google App Engine too
# File is released under public domain and you can use without limitations
# -------------------------------------------------------------------------

if request.global_settings.web2py_version < "2.14.1":
    raise HTTP(500, "Requires web2py 2.13.3 or newer")

# -------------------------------------------------------------------------
# if SSL/HTTPS is properly configured and you want all HTTP requests to
# be redirected to HTTPS, uncomment the line below:
# -------------------------------------------------------------------------
# request.requires_https()

# -------------------------------------------------------------------------
# app configuration made easy. Look inside private/appconfig.ini
# -------------------------------------------------------------------------
from gluon.contrib.appconfig import AppConfig

# -------------------------------------------------------------------------
# once in production, remove reload=True to gain full speed
# -------------------------------------------------------------------------
myconf = AppConfig(reload=True)

if not request.env.web2py_runtime_gae:
    # ---------------------------------------------------------------------
    # if NOT running on Google App Engine use SQLite or other DB
    # ---------------------------------------------------------------------
    db = DAL(settings.database_uri,
             pool_size=myconf.get('db.pool_size'),
             migrate_enabled = True,
             check_reserved = ['all'])
else:
    # ---------------------------------------------------------------------
    # connect to Google BigTable (optional 'google:datastore://namespace')
    # ---------------------------------------------------------------------
    db = DAL('google:datastore+ndb')
    # ---------------------------------------------------------------------
    # store sessions and tickets there
    # ---------------------------------------------------------------------
    session.connect(request, response, db=db)
    # ---------------------------------------------------------------------
    # or store session in Memcache, Redis, etc.
    # from gluon.contrib.memdb import MEMDB
    # from google.appengine.api.memcache import Client
    # session.connect(request, response, db = MEMDB(Client()))
    # ---------------------------------------------------------------------

# -------------------------------------------------------------------------
# by default give a view/generic.extension to all actions from localhost
# none otherwise. a pattern can be 'controller/function.extension'
# -------------------------------------------------------------------------
response.generic_patterns = ['*'] if request.is_local else []
# -------------------------------------------------------------------------
# choose a style for forms
# -------------------------------------------------------------------------
response.formstyle = myconf.get('forms.formstyle')  # or 'bootstrap3_stacked' or 'bootstrap2' or other
response.form_label_separator = myconf.get('forms.separator') or ''

# -------------------------------------------------------------------------
# (optional) optimize handling of static files
# -------------------------------------------------------------------------
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

# -------------------------------------------------------------------------
# (optional) static assets folder versioning
# -------------------------------------------------------------------------
# response.static_version = '0.0.0'

# -------------------------------------------------------------------------
# Here is sample code if you need for
# - email capabilities
# - authentication (registration, login, logout, ... )
# - authorization (role based authorization)
# - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
# - old style crud actions
# (more options discussed in gluon/tools.py)
# -------------------------------------------------------------------------

from gluon.tools import Auth, Service, PluginManager

# host names must be a list of allowed host names (glob syntax allowed)
auth = Auth(db)

service = Service()
plugins = PluginManager()

# -------------------------------------------------------------------------
# create all tables needed by auth if not custom tables
# -------------------------------------------------------------------------

# Definimos campos adicionales en la tabla auth_user
auth.settings.extra_fields['auth_user']= [
  Field('ci', type='string', notnull=False, required=False, default=''),
  Field('phone', type='string', notnull=False, required=False, default=''),
  Field('phone2', type='string', notnull=False, required=False, default=''),
  Field('access_key', type='string', notnull=False, required=True, default='')
]

auth.define_tables(username=True, signature=False)

# -------------------------------------------------------------------------
# configure email
# -------------------------------------------------------------------------
mail = auth.settings.mailer
mail.settings.server = 'logging' if request.is_local else myconf.get('smtp.server')
mail.settings.sender = myconf.get('smtp.sender')
mail.settings.login = myconf.get('smtp.login')
mail.settings.tls = myconf.get('smtp.tls') or False
mail.settings.ssl = myconf.get('smtp.ssl') or False

# -------------------------------------------------------------------------
# configure auth policy
# -------------------------------------------------------------------------
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = False

#Insertando los roles en la base de datos
ROLES = [
    ('DACE-ADMINISTRADOR','Miembro de DACE que tiene permisos de administrador del sistema.'),
    ('DACE-OPERADOR','Miembro de DACE que tiene permisos de consulta del sistema.'),
    ('DECANATO','Decanato de la USB.'),
    ('DEPARTAMENTO','Jefe de Departamento de la USB.'),
    ('COORDINACION','Coordinador de Carrera de la USB.'),
    ('LABORATORIO','Jefe de la Unidad de Laboratorios de la USB.'),
    ('BIBLIOTECA','Director de la Biblioteca de la USB.'),
    ('TRANSCRIPTOR','Miembro de la USB con permiso de transcripción de Programas Académicos'),
    ('PROFESOR','Profesor de la USB.'),
    ('ESTUDIANTE','Estudiante de la USB.'),
    ('INACTIVO','Usuario que ha sido marcado como Inactivo en el sistema SIGPAE.'),
]

for rol in ROLES:
    if db(db.auth_group).count() < len(ROLES):
        db.auth_group.insert(role = rol[0], description = rol[1])

#Asignando los permisos a los roles respectivos.

# Actulizar Perfil Propio
auth.add_permission(auth.id_group(role="DACE-ADMINISTRADOR"), 'update_profile', 'auth_user')
auth.add_permission(auth.id_group(role="DACE-OPERADOR"),      'update_profile', 'auth_user')
auth.add_permission(auth.id_group(role="DECANATO"),      'update_profile', 'auth_user')
auth.add_permission(auth.id_group(role="DEPARTAMENTO"),      'update_profile', 'auth_user')
auth.add_permission(auth.id_group(role="COORDINACION"),      'update_profile', 'auth_user')
auth.add_permission(auth.id_group(role="LABORATORIO"),      'update_profile', 'auth_user')
auth.add_permission(auth.id_group(role="BIBLIOTECA"),      'update_profile', 'auth_user')
auth.add_permission(auth.id_group(role="TRANSCRIPTOR"),      'update_profile', 'auth_user')
auth.add_permission(auth.id_group(role="PROFESOR"),      'update_profile', 'auth_user')
auth.add_permission(auth.id_group(role="ESTUDIANTE"),      'update_profile', 'auth_user')

# Manejar Usuario
auth.add_permission(auth.id_group(role="DACE-ADMINISTRADOR"), 'manage_users', 'auth_user')
# Manejar Transcriptores
auth.add_permission(auth.id_group(role="DEPARTAMENTO"), 'manage_transcriptors', 'auth_user')
auth.add_permission(auth.id_group(role="COORDINACION"), 'manage_transcriptors', 'auth_user')
auth.add_permission(auth.id_group(role="DECANATO"), 'manage_transcriptors', 'auth_user')

# Crear Nueva Transcripcion
auth.add_permission(auth.id_group(role="TRANSCRIPTOR"), 'create_transcription')

# Aceptar y Rechazar Transcripciones
auth.add_permission(auth.id_group(role="DEPARTAMENTO"), 'manage_transcription')
auth.add_permission(auth.id_group(role="COORDINACION"), 'manage_transcription')
auth.add_permission(auth.id_group(role="DECANATO"), 'manage_transcription')

# Solicitar Programa Academico
auth.add_permission(auth.id_group(role="COORDINACION"), 'request_ap')
auth.add_permission(auth.id_group(role="DEPARTAMENTO"), 'request_ap')
auth.add_permission(auth.id_group(role="DECANATO"),     'request_ap')
auth.add_permission(auth.id_group(role="PROFESOR"),     'request_ap')

# Llenar Programa Academico
auth.add_permission(auth.id_group(role="PROFESOR"), 'fill_ap')

# Asignar Profesores
auth.add_permission(auth.id_group(role="DEPARTAMENTO"), 'assign_profesor')

# Aceptar y Rechazar Asignacion de Programa Academico
auth.add_permission(auth.id_group(role="PROFESOR"), 'manage_assignment')

# Aceptar y Rechazar Solicitud Programa Academico
auth.add_permission(auth.id_group(role="DACE-ADMINISTRADOR"), 'manage_ap_request')
auth.add_permission(auth.id_group(role="DACE-OPERADOR"), 'manage_ap_request')
auth.add_permission(auth.id_group(role="DECANATO"), 'manage_ap_request')
auth.add_permission(auth.id_group(role="DEPARTAMENTO"), 'manage_ap_request')
auth.add_permission(auth.id_group(role="COORDINACION"), 'manage_ap_request')

# Incorporar y Desincorporar Programa Academico
auth.add_permission(auth.id_group(role="DACE-ADMINISTRADOR"), 'manage_ap')
auth.add_permission(auth.id_group(role="DACE-OPERADOR"), 'manage_ap')

# Consultar Referencias Bibliograficas
auth.add_permission(auth.id_group(role="BIBLIOTECA"), 'consult_references')

# Ver Programas Academicos de Materias Aprobadas
auth.add_permission(auth.id_group(role="ESTUDIANTE"), 'consult_ap')

# ASEGURA QUE EL PRIMER USUARIO EN INCIAR SESION EL EL SISTEMA (ID=1) SEA EL ADMIN.
auth.add_membership(auth.id_group(role="DACE-ADMINISTRADOR"), 1)


# TRANSCRIPCIONES
# Definición del dominio del periodo de vigencia del programa que se transcribe
SEP_DIC = 'SEP-DIC'
ENE_MAR = 'ENE-MAR'
ABR_JUL = 'ABR-JUL'

# Periodos para programas de Pasantias
ENE_MAY = 'ENE-MAY'
ABR_SEP = 'ABR-SEP'
JUL_DIC = 'JUL-DIC'
OCT_FEB = 'OCT_FEB'


PERIODOS = (
    (SEP_DIC, SEP_DIC),
    (ENE_MAR, ENE_MAR),
    (ABR_JUL, ABR_JUL),
    (ENE_MAY, ENE_MAY),
    (ABR_SEP, ABR_SEP),
    (JUL_DIC, JUL_DIC),
    (OCT_FEB, OCT_FEB)
)

# Definición del dominio de las horas de dedicación al curso del programa
HORAS = tuple([(i, i) for i in range(41)])

# Definición del dominio de los creditos de un programa
CREDITOS = tuple([(i, i) for i in range(17)])


db.define_table('TRANSCRIPCION',
    Field('original_pdf', type='string', notnull = True, required = True),
    Field('texto', type='text',   notnull = False),
    Field('codigo',type='string', length = 8, requires = IS_MATCH('([A-Z]{2,2}[0-9]{4,4})|([A-Z]{3,3}[0-9]{3,3})',
                                                                 error_message = 'Codigo de asignatura no válido.')),
    Field('denominacion', type = 'string',length = 100),
    Field('fecha_elaboracion', type = 'date', requires = IS_DATE_IN_RANGE(format=T('%d/%m/%Y'),
                                                                          minimum=datetime.date(1967,1,1),
                                                                          maximum=datetime.date.today(),
                                                                          error_message='Debe seleccionar una fecha en formato DD/MM/AAAA no mayor a la fecha actual.')),
    Field('periodo', type ='string', length = 9, requires =  IS_IN_SET(PERIODOS, zero='Seleccione', error_message = 'Seleccione un periodo.')),
    Field('anio', type = 'integer',  length = 4,  requires = [IS_INT_IN_RANGE(1967, 1e100,
                                                                            error_message='El año debe ser un numero positivo de la forma YYYY a partir de 1967.'),
                                                              IS_LENGTH(4,  error_message ='El año debe ser de la forma YYYY.')]),
    Field('periodo_hasta', type ='string', length = 9, requires =  IS_IN_SET(PERIODOS, zero='Seleccione', error_message = 'Seleccione un periodo.')),
    Field('anio_hasta', type = 'integer',  length = 4,  requires = [IS_INT_IN_RANGE(1967, 1e100,
                                                                            error_message='El año debe ser un numero positivo de la forma YYYY a partir de 1967.'),
                                                              IS_LENGTH(4,  error_message ='El año debe ser de la forma YYYY.')]),
    Field('horas_teoria', type ='integer', requires =  IS_IN_SET(HORAS, zero='Seleccione', error_message = 'Seleccione un número de horas.')),
    Field('horas_practica', type ='integer', requires =  IS_IN_SET(HORAS, zero='Seleccione', error_message = 'Seleccione un número de horas.')),
    Field('horas_laboratorio', type ='integer', requires =  IS_IN_SET(HORAS, zero='Seleccione', error_message = 'Seleccione un número de horas.')),
    Field('creditos', type ='integer', requires =  IS_IN_SET(CREDITOS, zero='Seleccione', error_message = 'Seleccione un número de creditos.')),
    Field('sinopticos', type="text"),
    Field('ftes_info_recomendadas', type="text"),
    Field('requisitos', type="text"),
    Field('estrategias_met', type="text"),
    Field('estrategias_eval', type="text"),
    Field('justificacion', type="text"),
    Field('observaciones', type="text"),
    Field('objetivos_generales', type="text"),
    Field('objetivos_especificos', type="text"),
    Field('fecha_modificacion', type="date", notnull = True, default = datetime.date.today()),
    Field('transcriptor', type="string", notnull = True),
    # encargado = models.CharField('Encargado', max_length=100, null=True)
    # pasa = models.BooleanField(default= False)
    # propuesto = models.BooleanField(default= False)
    )

db.define_table('REGISTRO_TRANSCRIPTORES',
    Field('transcriptor', type="string", notnull = True),
    Field('supervisor', type="string", notnull = True)
    )
# -------------------------------------------------------------------------
# after defining tables, uncomment below to enable auditing
# -------------------------------------------------------------------------
auth.enable_record_versioning(db)
