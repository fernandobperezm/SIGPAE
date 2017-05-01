# -*- coding: utf-8 -*-

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
             migrate_enabled=myconf.get('db.migrate'),
             check_reserved=['all'])
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
    ('DECANATO','Decano de la USB.'),
    ('DEPARTAMENTO','Jefe de Departamento de la USB.'),
    ('COORDINACION','Coordinador de Carrera de la USB.'),
    ('LABORATORIO','Jefe de la Unidad de Laboratorios de la USB.'),
    ('BIBLIOTECA','Director de la Biblioteca de la USB.'),
    ('TRANSCRIPTOR','Miembro de la USB con permiso de transcripción de Programas Académicos'),
    ('PROFESOR','Profesor de la USB.'),
    ('ESTUDIANTE','Estudiante de la USB.'),
    ('BLOQUEADO','Usuario que ha sido bloqueado del sistema SIGPAE.'),
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
auth.add_permission(auth.id_group(role="DACE-OPERADOR"),      'manage_users', 'auth_user')

# Manejar Transcriptores
auth.add_permission(auth.id_group(role="DEPARTAMENTO"), 'manage_transcriptors', 'auth_user')
auth.add_permission(auth.id_group(role="COORDINACION"), 'manage_transcriptors', 'auth_user')

# Crear Nueva Transcripcion
auth.add_permission(auth.id_group(role="TRANSCRIPTOR"), 'create_transcription')

# Aceptar y Rechazar Transcripciones
auth.add_permission(auth.id_group(role="DEPARTAMENTO"), 'manage_transcription')
auth.add_permission(auth.id_group(role="COORDINACION"), 'manage_transcription')

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
auth.add_permission(auth.id_group(role="PROFESOR"), 'accept_assignment')
auth.add_permission(auth.id_group(role="PROFESOR"), 'reject_assignment')

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

# TEST ROLES
auth.add_membership(auth.id_group(role="DACE-ADMINISTRADOR"), 1)
auth.add_membership(auth.id_group(role="TRANSCRIPTOR"), 1)


# -------------------------------------------------------------------------
# after defining tables, uncomment below to enable auditing
# -------------------------------------------------------------------------
auth.enable_record_versioning(db)
