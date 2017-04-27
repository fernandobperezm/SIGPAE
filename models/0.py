from gluon.storage import Storage

settings = Storage()

settings.migrate = True
settings.title = ''
settings.subtitle = ''
settings.author = ''
settings.author_email = ''
settings.keywords = ''
settings.description = ''
settings.layout_theme = ''
settings.database_uri = 'postgres://sigpae:123123@localhost/newsigpae'
settings.security_key = ''
settings.email_server = ''
settings.email_sender = ''
settings.email_login = ''
settings.login_method = 'local'
settings.login_config = ''
settings.plugins = []

# CONFIGURACION DE URLS
# DESCOMENTAR LA URL DEPENDIENDO DE SI SE ESTA TRABAJANDO LOCALMENTE O ES
# LA VERSION USADA EN EL SERVIDOR.
# LOCAL:
settings.returnurl = "http%3A%2F%2Flocalhost%3A8000%2FSIGPAE%2Fdefault%2Flogin_cas"
# SERVIDOR:
#settings.returnurl =

# Custom requires_login decorator for login with CAS
def requires_login(function):

    def wrapper():
        if auth.is_logged_in():
            return function()
        else:
            redirect('https://secure.dst.usb.ve/login?service=' + settings.returnurl)

    return wrapper
