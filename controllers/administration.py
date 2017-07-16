import StringIO

@auth.requires(auth.is_logged_in() and auth.has_permission('manage_users', 'auth_user') and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def log():
    """
        Inicio en la vista de la bitácora.
    """

    message = "Registro de Eventos"

    # Obtenemos los registros de la bitácora para la transcripcion
    registros = db(db.LOG_SIGPAE).select()

    formulario = form_download_registers()

    if formulario.process(formname="formulario_descargar_registros").accepted:
        periodo = request.vars.periodo
        redirect(URL(c='administration', f='download_registers', args=[periodo]))
    if formulario.errors:
        response.flash = "No se pudo descargar el Registro."

    return dict(message = message, registros = registros, formulario = formulario)

@auth.requires(auth.is_logged_in() and auth.has_permission('manage_users', 'auth_user') and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def download_registers():
    """
        Permite descargar los registros del sistema SIGPAE.
    """

    periodo = request.args[0]
    if not(periodo):
        redirect(URL(c='default', f='not_authorized'))

    date = ''

    if periodo == '0':
        query = "SELECT * FROM LOG_SIGPAE;"
    elif periodo == '1':
        date = datetime.date.today()
    elif periodo == '2':
        date = datetime.date.today() - datetime.timedelta(days=7)
    elif periodo == '3':
        date = datetime.date.today() - datetime.timedelta(days=31)
    elif periodo == '4':
        date = datetime.date.today() - datetime.timedelta(days=93)

    #Excecute query
    # rows = db.executesql(query, fields = db.LOG_SIGPAE)
    if date:
        rows=db(db.LOG_SIGPAE.fecha >= date).select(db.LOG_SIGPAE.fecha,
                                                    db.LOG_SIGPAE.usuario,
                                                    db.LOG_SIGPAE.rol_usuario,
                                                    db.LOG_SIGPAE.accion,
                                                    db.LOG_SIGPAE.descripcion)
    else:
        rows=db(db.LOG_SIGPAE).select(db.LOG_SIGPAE.fecha,
                                      db.LOG_SIGPAE.usuario,
                                      db.LOG_SIGPAE.rol_usuario,
                                      db.LOG_SIGPAE.accion,
                                      db.LOG_SIGPAE.descripcion)

    #convert query to csv
    tempfile = StringIO.StringIO()
    rows.export_to_csv_file(tempfile)
    response.headers['Content-Type'] = 'text/csv'
    attachment = 'attachment; filename="REGISTRO_SIGPAE.csv"'
    response.headers['Content-Disposition'] = attachment
    return tempfile.getvalue()

def form_download_registers():
    """
        Retorna el formulario para descargar el Registro.
    """

    periodos = [
        (0, 'Todo'),
        (1, 'Hoy'),
        (2, 'Semana pasada'),
        (3, 'Mes pasado'),
        (4, 'Hace 3 meses'),
    ]

    # Genero formulario para los campos
    formulario = SQLFORM.factory(
                    Field('periodo',
                           requires = [IS_IN_SET(periodos, zero='Seleccione...', error_message="Debe seleccionar un periodo para descargar el Registro.")],
                           widget = SQLFORM.widgets.options.widget),
                    labels = {'periodo' : 'Periodo'},
                    submit_button='Descargar'
                   )

    return formulario
