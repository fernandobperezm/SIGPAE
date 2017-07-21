from gluon.storage import Storage

settings = Storage()

settings.migrate = True
settings.title = 'SIGPAE'
settings.subtitle = 'Sistema de Gestión de Programas Analíticos de Estudio'
settings.author   = 'Leonardo Martínez, Jonnathan Ng, Nicolás Mañan.'
settings.author_email = ''
settings.keywords     = ''
settings.description  = ''
settings.layout_theme = ''
settings.database_uri = 'postgres://sigpae:LXHyCmFD9rQPCqC@localhost/newsigpae'
settings.login_method = 'local'
settings.email_server = 'smtp.gmail.com:587'
settings.email_sender = 'noreplysigpaeusb@gmail.com'
settings.email_login  = 'noreplysigpaeusb@gmail.com:LXHyCmFD9rQPCqC'
settings.login_config = ''
settings.plugins      = []

# CONFIGURACION DE URLS
# DESCOMENTAR LA URL DEPENDIENDO DE SI SE ESTA TRABAJANDO LOCALMENTE O ES
# LA VERSION USADA EN EL SERVIDOR.
# LOCAL:
settings.returnurl = "http%3A%2F%2Flocalhost%3A8000%2FSIGPAE%2Fdefault%2Flogin_cas"
# SERVIDOR:
#settings.returnurl =
