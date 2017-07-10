from wand.image         import Image
from PIL                import Image as Pi
from webservice_queries import *
from notifications      import *
import os
import sys
import io
import re
import pyocr
import pyocr.builders

@auth.requires(auth.is_logged_in() and auth.has_permission('manage_transcriptors', 'auth_user') and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def transcriptors():
    """
      Vista para un usuario que tiene el rol de transcriptor.
    """

    message = "Transcriptores"

    group_id = auth.id_group(role="TRANSCRIPTOR")

    all_transcriptors_for_user = db(db.REGISTRO_TRANSCRIPTORES.supervisor == auth.user.username)._select(db.REGISTRO_TRANSCRIPTORES.transcriptor)

    transcriptors = db(db.auth_user.username.belongs(all_transcriptors_for_user)).select(db.auth_user.id,
                                                                                         db.auth_user.username,
                                                                                         db.auth_user.first_name,
                                                                                         db.auth_user.last_name,
                                                                                         db.auth_user.email)
    lista_transcriptores = []
    # Obtenemos los roles de cada usuario
    for transcriptor in transcriptors:
        lista_transcriptores.append({'id' : transcriptor.id,
                                     'username': transcriptor.username,
                                     'name' : transcriptor.first_name + ' ' + transcriptor.last_name,
                                     'email': transcriptor.email})

    # formulario para nuevos transcriptores
    # se buscan por correo institucional, y se comprueba por medio de una expresion regular
    form = SQLFORM.factory(Field('correo', type="string",
                                  requires = IS_MATCH(r'\b([a-zA-Z0-9-]+@usb\.ve)\b',
                                  error_message = 'Correo no corresponde a un Correo Institucional.')),
                           labels={'correo':'Correo'})

    if form.process(formname="formulario_agregar_transcriptor").accepted:
        email = form.vars.correo
        usuario = db(db.auth_user.email == email).select().first()
        if usuario:

            # chequeo sobre si el usuario puede transcribir.
            # primero revisamos que el usuario pertenece a un grupo que puede ser transcriptor
            puede_transcribir = True
            roles      = db(db.auth_membership.user_id == usuario.id).select(db.auth_membership.group_id)

            no_permitidos = [int(auth.id_group(role="DECANATO")),
                             int(auth.id_group(role="COORDINACION")),
                             int(auth.id_group(role="DEPARTAMENTO"))]

            # Revisamos que el usuario no tenga rol de decanato, Dpto, o Coord. para transcribir.
            for i in roles:
                if i['group_id'] in no_permitidos:
                    puede_transcribir = False
                    session.flash = 'Usuarios con rol de DECANATO, COORDINACION o DEPARTAMENTO no pueden transcribir programas.'

            # luego, revisamos si ya se encuentra transcribiendo para algun supervisor
            existente = db(db.REGISTRO_TRANSCRIPTORES.transcriptor == usuario.username).select()
            if existente:
                puede_transcribir = False
                session.flash = 'El Usuario ya es Transcriptor de otro DECANATO, COORDINACION o DEPARTAMENTO.'

            # finalmente, puede transcribir y se agrega a la lista de usuarios transcriptores
            if puede_transcribir:
                auth.add_membership(group_id, usuario.id)

                new_id = db.REGISTRO_TRANSCRIPTORES.insert(transcriptor = usuario.username,
                                                           supervisor   = auth.user.username)
                session.flash = 'Usuario agregado como Transcriptor.'

        else:
            session.flash = 'Usuario no encontrado.'

        redirect(URL(c='transcriptions',f='transcriptors'))
    elif form.errors:
        response.flash = 'No se pudo agregar al usuario.'

    return dict(message = message, transcriptores = lista_transcriptores, group_id = group_id, form=form)

@auth.requires(auth.is_logged_in() and auth.has_permission('manage_transcriptors', 'auth_user') and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def deletetranscriptor():
    """
      Funcion encargada de la eliminacion de transcriptores.
    """

    idusuario = request.args(0)
    idrole    = request.args(1)

    # eliminamos el usuario como transcriptor para el solicitante
    usuario  = db(db.auth_user.id == idusuario).select().first()
    registro = db((db.REGISTRO_TRANSCRIPTORES.transcriptor == usuario.username ) &
                  (db.REGISTRO_TRANSCRIPTORES.supervisor == auth.user.username )).delete()

    # Reasignamos las transcriptiones pendientes al usuario que realizo la eliminacion
    transcripciones = db(db.TRANSCRIPCION.transcriptor == usuario.username).select()

    for transcripcion in transcripciones:
      db.TRANSCRIPCION[transcripcion['id']] = dict(transcriptor = auth.user.username)

    # revisamos si es transcriptor de otro usuario. En caso contrario, quitamos el rol
    # de transcriptor.
    registro = db(db.REGISTRO_TRANSCRIPTORES.transcriptor == usuario.username).select()
    if len(registro) == 0:
        auth.del_membership(idrole, idusuario)
    else:
        session.flash = 'Usuario eliminado como Transcriptor.'
        redirect(URL(c='transcriptions',f='transcriptors'))

    session.flash = 'Usuario eliminado como Transcriptor.'
    redirect(URL(c='transcriptions',f='transcriptors'))

@auth.requires(auth.is_logged_in() and auth.has_permission('manage_transcriptors', 'auth_user') and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def following():
    """
        Vista para listar las transcripciones a evaluar por un supervisor en proceso.
    """
    message = "Seguimiento de Transcripciones"

    # obtenemos los transcriptores asociadas al supervisor
    all_transcriptors_for_user = db(db.REGISTRO_TRANSCRIPTORES.supervisor == auth.user.username)._select(db.REGISTRO_TRANSCRIPTORES.transcriptor)

    # Obtenemos las transcripciones
    transcripciones = db((db.TRANSCRIPCION.transcriptor.belongs(all_transcriptors_for_user)) & (db.TRANSCRIPCION.estado == 'pendiente')|
                         (db.TRANSCRIPCION.transcriptor == auth.user.username) & (db.TRANSCRIPCION.estado == 'pendiente')).select(db.TRANSCRIPCION.id,
                                                                                                                                  db.TRANSCRIPCION.codigo,
                                                                                                                                  db.TRANSCRIPCION.transcriptor,
                                                                                                                                  db.TRANSCRIPCION.fecha_elaboracion,
                                                                                                                                  db.TRANSCRIPCION.fecha_modificacion)

    transcriptores =  db(db.auth_user.username.belongs(all_transcriptors_for_user)).select(db.auth_user.username,
                                                                                           db.auth_user.first_name,
                                                                                           db.auth_user.last_name)
    lista_transcripciones = []
    # Obtenemos los roles de cada usuario
    for transcripcion in transcripciones:
        lista_transcripciones.append({'id' : transcripcion.id,
                                      'transcriptor' : transcripcion.transcriptor,
                                      'codigo': transcripcion.codigo,
                                      'fecha_elaboracion' : transcripcion.fecha_elaboracion,
                                      'fecha_modificacion': transcripcion.fecha_modificacion})

    lista_transcriptores = []
    for transcriptor in transcriptores:
        lista_transcriptores.append((transcriptor.username, transcriptor.first_name + ' ' + transcriptor.last_name))

    # formulario para reasignar transcripcion a otro transcriptor
    formulario_reasignar = SQLFORM.factory(Field('transcriptor', type="string",
                                                  requires = IS_IN_SET(lista_transcriptores,
                                                  error_message = 'Seleccione un Transcriptor.',
                                                  zero = "Seleccione...")),
                                           Field('transcription_id', type='string'),
                                           Field('comentario', type='text'),
                                                  labels={'transcriptor':'Nuevo Transcriptor',
                                                          'comentario': 'Comentario'})

    if formulario_reasignar.process(formname="formulario_reasignar").accepted:

        transcription_id = formulario_reasignar.vars.transcription_id
        transcriptor = formulario_reasignar.vars.transcriptor

        comentario = formulario_reasignar.vars.comentario
        print(comentario)

        # buscamos la transcripcion a reasignar y la actualizamos
        db.TRANSCRIPCION[transcription_id] = dict(transcriptor = transcriptor)
        session.flash = "Reasignación exitosa."
        redirect(URL(c='transcriptions', f='following'))

    elif formulario_reasignar.errors:
        response.flash = 'Error en la reasignación, intente nuevamente.'

    return dict(message=message, transcripciones = lista_transcripciones, formulario_reasignar = formulario_reasignar)


@auth.requires(auth.is_logged_in() and auth.has_permission('create_transcription') and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def add():
    """
      Función para empezar una nueva transcripción.
      En la vista se selecciona un archivo .pdf o imagen de un .pdf de una transcripcion
      para poder iniciar el proceso.
    """

    mensaje = 'Nueva Transcripción'

    # Se selecciona en el formulario el tipo de archivo a cargar.
    form = SQLFORM.factory(
                Field('file', 'upload', label = 'Archivo PDF',
                                        uploadfolder=os.path.join(request.folder,'static/transcriptions/originalpdf/'),
                                        requires = IS_NOT_EMPTY(error_message='Seleccione un archivo.')),
                Field('file_type', 'select' , label = 'Tipo de Archivo',
                                              requires = IS_IN_SET(['Texto', 'Imagen'],
                                                         zero='Seleccione una opción...',
                                                         error_message='Seleccione un tipo de archivo.'),
                                              default='Texto'),
                Field('extract_type', 'select' , label = 'Extraer',
                                                 requires = IS_IN_SET(['Solo Texto', 'Código y Departamento'],
                                                            zero='Seleccione una opción...',
                                                            error_message='Seleccione el tipo de extracción.'),
                                                 default='Solo Texto'),
                formstyle = 'bootstrap3_stacked',
                col3 = {'file_type':'Seleccione "Texto" si el programa a transcribir proviene de un pdf de texto. Si es un programa escaneado, seleccione "Imagen".',
                        'extract_type': 'Si desea detectar automáticamente el Código y  Departamento seleccione "Código y Departamento", sino seleccione "Solo Texto".' })

    if form.process().accepted:
        id = db.TRANSCRIPCION.insert(original_pdf = form.vars.file, transcriptor = auth.user.username)['id']
        redirect(URL('edit', vars = dict(id = id, file = form.vars.file, file_type = form.vars.file_type, extract_type = form.vars.extract_type)))

    return dict(message = mensaje, form = form)

def check_valid_aditional_field_name(name):

    """
      Función para chequear que el campo adicional no contenga los mismos
      nombres que los campos obligatorios.

    """
    campos_definidos= [
          "Codigo", "Código",
          "Denominacion", "Denominación",
          "Fecha Elaboracion", "Fecha Elaboración",
          "Periodo", "Año",
          "Periodo De Vigencia",
          "Horas De Teoria", "Horas De Teoría",
          "Horas De Practica", "Horas De Práctica",
          "Horas De Laboratorio",
          "Creditos", "Créditos",
          "Objetivos Generales",
          "Objetivos Específicos", "Objetivos Especificos",
          "Contenidos Sinópticos", "Contenidos Sinopticos",
          "Requisitos",
          "Estrategias Metodológicas", "Estrategias Metodologicas",
          "Estrategias de Evaluación", "Estrategias de Evaluacion",
          "Justificación", "Justificacion",
          "Fuentes de Información Recomendadas", "Fuentes de Informacion Recomendadas",
          "Observaciones",
          "Campos Adicionales"]

    # revisa si no existe otro campo adicional definido con el mismo nombre
    nombre = db(db.NOMBRES_CAMPOS_ADICIONALES_TRANSCRIPCION.nombre == name).select()

    if nombre:
        return False

    return not(name in campos_definidos)

@auth.requires(auth.is_logged_in() and auth.has_permission('create_transcription') and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def delete_aditional_field():
    """
        Borra el campo adicional agregado.
    """

    transid  = request.args(0)
    id_campo = request.args(1)
    db(db.CAMPOS_ADICIONALES_TRANSCRIPCION.id == id_campo).delete()

    session.flash = "Campo Adicional eliminado exitosamente."
    redirect(URL(c='transcriptions',f='edit', vars=dict(id=transid)))


@auth.requires(auth.is_logged_in() and auth.has_permission('create_transcription') and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def edit():
    """
      Función para editar la planilla de transcripción.
    """

    id =  request.vars['id']
    if not isinstance(id, str):
        id = id[0]

    transcription = db(db.TRANSCRIPCION.id == id).select().first()

    pdfurl = transcription.original_pdf
    code   = transcription.codigo
    text   = transcription.texto

    # Extrae el texto según el tipo de archivo cargado para transcribir
    if 'file_type' in request.vars:
        if request.vars['file_type'] == "Texto":

            text = extract_text(os.path.join(request.folder,'static/transcriptions/originalpdf',request.vars['file']))
        elif request.vars['file_type'] == "Imagen":
            text = extract_text_from_image(os.path.join(request.folder,'static/transcriptions/originalpdf',request.vars['file']))

        db.TRANSCRIPCION[id] = dict(texto = text)

    # Se extrae en código y departamento del texto para llenar automáticamente en la forma.
    if 'extract_type' in request.vars:
        if request.vars['extract_type'] == "Código y Departamento":
            code = match_codigo_asig(text)
            db.TRANSCRIPCION[id] = dict(codigo = code)

            # hacemos la busqueda de la asignatura, si es posible
            details = subject_details(code)
            if details:
                db.TRANSCRIPCION[id] = dict(denominacion = details['nombre'])

    pdfurl = URL('static','transcriptions/originalpdf/' + pdfurl)

    # Campos por defecto en la forma de transcripción.
    transcription_form = SQLFORM(db.TRANSCRIPCION,
                   record = id,
                   fields = ['codigo', 'denominacion', 'fecha_elaboracion',
                             'periodo', 'horas_teoria', 'horas_practica',
                             'horas_laboratorio' , 'creditos', 'anio',
                             'periodo_hasta', 'anio_hasta',
                             'sinopticos','ftes_info_recomendadas','requisitos',
                             'estrategias_met','estrategias_eval','justificacion',
                             'observaciones','objetivos_generales','objetivos_especificos'],
                   submit_button=T('Guardar')
                   )

    # obtenemos los campos adicionales, si existen
    campos_adicionales = db(db.CAMPOS_ADICIONALES_TRANSCRIPCION.transcripcion == transcription).select()

    # formulario para el nuevo campo adicional
    new_field_form = SQLFORM.factory(
            Field('nombre', type="string",
                   requires = IS_EMPTY_OR(
                                IS_IN_DB(db, db.NOMBRES_CAMPOS_ADICIONALES_TRANSCRIPCION.nombre, zero='Seleccione...'))),
            Field('otro_nombre', type='string'),
            labels = {
                'nombre' : 'Campos Adicionales',
                'otro_nombre' : 'Otro Campo'
            },
            submit_button=T('Agregar Campo')
            )

    # formulario para editar campos adicionales
    edit_field_form = SQLFORM.factory(
            Field('id_campo', type='string'),
            Field('contenido', type='text'),
            labels = {
                'contenido' : 'Contenido'},
            submit_button=T('Guardar')
            )

    # Procesamiento del formulario de la transcripcion
    if transcription_form.accepts(request, session, hideerror=True, keepvalues = True, formname = "transcription_form"):
        session.flash = 'Transcripción guardada satisfactoriamente.'
    elif transcription_form.errors:
        response.flash = 'Hay errores en el formulario'

    # procesamiento del formulario para una nuevo campo adicional
    if new_field_form.process(formname = "new_field_form").accepted:
        nombre_campo = ''

        if new_field_form.vars.nombre:
            nombre_campo = new_field_form.vars.nombre.capitalize()

            campo_existe = campos_adicionales = db((db.CAMPOS_ADICIONALES_TRANSCRIPCION.transcripcion == transcription) &
                                                   (db.CAMPOS_ADICIONALES_TRANSCRIPCION.nombre == nombre_campo)).select()
            if campo_existe:
                session.flash = 'Campo %s ya fue agregado previamente.'%(nombre_campo)
            else:
                db.CAMPOS_ADICIONALES_TRANSCRIPCION.insert(
                        transcripcion = transcription,
                        nombre = nombre_campo
                    )
                session.flash = 'Nuevo campo %s agregado.'%(nombre_campo)
        elif new_field_form.vars.otro_nombre:
            nombre_campo = new_field_form.vars.otro_nombre.capitalize()

            # se verifica si es un campo adicional no antes definido
            if check_valid_aditional_field_name(nombre_campo):
                # en caso afirmativo, lo registramos y lo asociamos a la transcripcion
                field_id = db.NOMBRES_CAMPOS_ADICIONALES_TRANSCRIPCION.insert(nombre=nombre_campo)
                db.CAMPOS_ADICIONALES_TRANSCRIPCION.insert(
                        transcripcion = transcription,
                        nombre = field_id['nombre']
                    )
                session.flash = 'Nuevo campo %s agregado.'%(nombre_campo)
            else:
                session.flash = 'Campo %s ya existe.'%(nombre_campo)


        redirect(URL(c='transcriptions',f='edit',vars={'id' : id}), client_side = True)

    elif new_field_form.errors:
        response.flash = 'No se pudo agregar un nuevo campo.'

    # procesamiento para editar campos adicionales
    if edit_field_form.process(formname = "edit_field_form").accepted:
        id_campo = edit_field_form.vars.id_campo
        db.CAMPOS_ADICIONALES_TRANSCRIPCION[id_campo] = dict (contenido = edit_field_form.vars.contenido)
        session.flash = 'Campo adicional actualizado.'
        redirect(URL(c='transcriptions',f='edit',vars={'id' : id}), client_side = True)
    elif edit_field_form.errors:
        response.flash = 'No se pudo agregar un nuevo campo.'

    return dict(text=text,
                pdfurl=pdfurl,
                code=code,
                id = id,
                campos_adicionales = campos_adicionales,
                transcription_form = transcription_form,
                new_field_form = new_field_form,
                edit_field_form = edit_field_form)

@auth.requires(auth.is_logged_in()
               and (auth.has_permission('manage_transcriptors', 'auth_user') or auth.has_permission('create_transcription'))
               and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def view():
    """
      Vista para ver la transcripción realizada ya enviada a aprobación.
    """

    id =  request.vars['id']
    if not isinstance(id, str):
        id = id[0]

    transcription = db(db.TRANSCRIPCION.id == id).select()
    if transcription:
        transcription = transcription.first()
    else:
        redirect(URL(c='default', f='not_authorized'))

    pdfurl = transcription.original_pdf
    code   = transcription.codigo
    text   = transcription.texto

    pdfurl = URL('static','transcriptions/originalpdf/' + pdfurl)

    transcription_form = SQLFORM(db.TRANSCRIPCION,
                   record   = id,
                   writable = False,
                   fields = ['codigo', 'denominacion', 'fecha_elaboracion',
                             'periodo', 'horas_teoria', 'horas_practica',
                             'horas_laboratorio' , 'creditos', 'anio',
                             'periodo_hasta', 'anio_hasta',
                             'sinopticos','ftes_info_recomendadas','requisitos',
                             'estrategias_met','estrategias_eval','justificacion',
                             'observaciones','objetivos_generales','objetivos_especificos'],
                   submit_button=T('Guardar')
                   )

    # obtenemos los campos adicionales, si existen
    campos_adicionales = db(db.CAMPOS_ADICIONALES_TRANSCRIPCION.transcripcion == transcription).select()

    return dict(text=text,
                pdfurl=pdfurl,
                code=code,
                id = id,
                transcription_form = transcription_form,
                campos_adicionales = campos_adicionales)

@auth.requires(auth.is_logged_in() and auth.has_permission('manage_transcriptors', 'auth_user')
               and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def approval_view():
    """
      Vista para los supervisores de transcripción, en esta pueden modificar las transcripciones
      a ser aprobadas o rechazadas.
    """

    id =  request.vars['id']
    if not isinstance(id, str):
        id = id[0]

    transcription = db(db.TRANSCRIPCION.id == id).select()
    if transcription:
        transcription = transcription.first()
    else:
        redirect(URL(c='default', f='not_authorized'))

    pdfurl = transcription.original_pdf
    code   = transcription.codigo
    text   = transcription.texto

    pdfurl = URL('static','transcriptions/originalpdf/' + pdfurl)

    # Se obtienen los campos por defecto

    transcription_form = SQLFORM(db.TRANSCRIPCION,
                   record   = id,
                   writable = False,
                   fields = ['codigo', 'denominacion', 'fecha_elaboracion',
                             'periodo', 'horas_teoria', 'horas_practica',
                             'horas_laboratorio' , 'creditos', 'anio',
                             'periodo_hasta', 'anio_hasta',
                             'sinopticos','ftes_info_recomendadas','requisitos',
                             'estrategias_met','estrategias_eval','justificacion',
                             'observaciones','objetivos_generales','objetivos_especificos'],
                   submit_button=T('Guardar')
                   )

    # obtenemos los campos adicionales, si existen
    campos_adicionales = db(db.CAMPOS_ADICIONALES_TRANSCRIPCION.transcripcion == transcription).select()

    # formulario del nuevo campo adicional
    new_field_form = SQLFORM.factory(
            Field('nombre', type="string",
                   requires = IS_EMPTY_OR(
                                IS_IN_DB(db, db.NOMBRES_CAMPOS_ADICIONALES_TRANSCRIPCION.nombre, zero='Seleccione...'))),
            Field('otro_nombre', type='string'),
            labels = {
                'nombre' : 'Campos Adicionales',
                'otro_nombre' : 'Otro Campo'
            },
            submit_button=T('Agregar Campo')
            )

    # formulario para editar campos adicionales
    edit_field_form = SQLFORM.factory(
            Field('id_campo', type='string'),
            Field('contenido', type='text'),
            labels = {
                'contenido' : 'Contenido'},
            submit_button=T('Guardar'))

    # formulario para rechazar la transcripcion
    reject_transcription_form = SQLFORM.factory(
                                    Field('comentario', type='text'),
                                    labels = {
                                        'comentario' : 'Comentario'},
                                    submit_button=T('Rechazar'))

    # Procesamiento del formulario de la transcripcion
    if transcription_form.accepts(request, session, hideerror=True, keepvalues = True, formname = "transcription_form"):
        session.flash = 'Transcripción guardada satisfactoriamente.'
    elif transcription_form.errors:
        response.flash = 'Hay errores en el formulario'

    # procesamiento del formulario para una nuevo campo adicional
    if new_field_form.process(formname = "new_field_form").accepted:
        nombre_campo = ''

        if new_field_form.vars.nombre:
            nombre_campo = new_field_form.vars.nombre.capitalize()

            campo_existe = campos_adicionales = db((db.CAMPOS_ADICIONALES_TRANSCRIPCION.transcripcion == transcription) &
                                                   (db.CAMPOS_ADICIONALES_TRANSCRIPCION.nombre == nombre_campo)).select()
            if campo_existe:
                session.flash = 'Campo %s ya fue agregado previamente.'%(nombre_campo)
            else:
                db.CAMPOS_ADICIONALES_TRANSCRIPCION.insert(
                        transcripcion = transcription,
                        nombre = nombre_campo
                    )
                session.flash = 'Nuevo campo %s agregado.'%(nombre_campo)
        elif new_field_form.vars.otro_nombre:
            nombre_campo = new_field_form.vars.otro_nombre.capitalize()

            # se verifica si es un campo adicional no antes definido
            if check_valid_aditional_field_name(nombre_campo):
                # en caso afirmativo, lo registramos y lo asociamos a la transcripcion
                field_id = db.NOMBRES_CAMPOS_ADICIONALES_TRANSCRIPCION.insert(nombre=nombre_campo)
                db.CAMPOS_ADICIONALES_TRANSCRIPCION.insert(
                        transcripcion = transcription,
                        nombre = field_id['nombre']
                    )
                session.flash = 'Nuevo campo %s agregado.'%(nombre_campo)
            else:
                session.flash = 'Campo %s ya existe.'%(nombre_campo)


        redirect(URL(c='transcriptions',f='approval_view',vars={'id' : id}), client_side = True)

    elif new_field_form.errors:
        response.flash = 'No se pudo agregar un nuevo campo.'

    # procesamiento para editar campos adicionales
    if edit_field_form.process(formname = "edit_field_form").accepted:
        id_campo = edit_field_form.vars.id_campo
        db.CAMPOS_ADICIONALES_TRANSCRIPCION[id_campo] = dict (contenido = edit_field_form.vars.contenido)
        session.flash = 'Campo adicional actualizado.'
        redirect(URL(c='transcriptions',f='approval_view',vars={'id' : id}), client_side = True)
    elif edit_field_form.errors:
        response.flash = 'No se pudo agregar un nuevo campo.'

    # procesamiento para rechazar una transcripcion
    if reject_transcription_form.process(formname = "reject_transcription_form").accepted:

        db.TRANSCRIPCION[id] = dict(estado = 'pendiente')
        session.flash = "Transcripción rechazada exitosamente."
        # comentarios
        comentario = reject_transcription_form.vars.comentario
        print(comentario)

        # obtenemos el usuario para enviar la notificaciones
        usuario = db(db.auth_user.username == transcription.transcriptor).select().first()
        enviar_correo_rechazo_transcripcion(mail, usuario, transcription.codigo + ' ' + transcription.denominacion, comentario)

        redirect(URL(c='transcriptions',f='list_pending'))

    elif reject_transcription_form.errors:
        response.flash = 'No se pudo agregar rechazar la Transcripción.'

    return dict(text=text,
                pdfurl=pdfurl,
                code=code,
                id = id,
                campos_adicionales = campos_adicionales,
                transcription_form = transcription_form,
                new_field_form = new_field_form,
                edit_field_form = edit_field_form,
                reject_transcription_form = reject_transcription_form)

@auth.requires(auth.is_logged_in() and auth.has_permission('create_transcription') and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def list():
    """
      Lista las transcripciones pendientes.
    """

    message = "Transcripciones"

    # Obtenemos las transcripciones
    transcripciones = db((db.TRANSCRIPCION.transcriptor == auth.user.username) & (db.TRANSCRIPCION.estado == 'pendiente')).select(db.TRANSCRIPCION.id,
                                                                                                                                  db.TRANSCRIPCION.codigo,
                                                                                                                                  db.TRANSCRIPCION.fecha_elaboracion,
                                                                                                                                  db.TRANSCRIPCION.fecha_modificacion)

    lista_transcripciones = []
    # Obtenemos los roles de cada usuario
    for transcripcion in transcripciones:
        lista_transcripciones.append({'id' : transcripcion.id,
                                      'codigo': transcripcion.codigo,
                                      'fecha_elaboracion' : transcripcion.fecha_elaboracion,
                                      'fecha_modificacion': transcripcion.fecha_modificacion})

    return dict(message=message, transcripciones = lista_transcripciones)

@auth.requires(auth.is_logged_in() and auth.has_permission('create_transcription') and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def list_sent():
    """
        Lista las transcripciones enviadas por el usuario que esperan aprobacion
        del supervisor.
    """
    message = "Transcripciones en Revisión"

    # Obtenemos las transcripciones
    transcripciones = db((db.TRANSCRIPCION.transcriptor == auth.user.username) &
                         (db.TRANSCRIPCION.estado == 'propuesta')).select(db.TRANSCRIPCION.id,
                                                                          db.TRANSCRIPCION.codigo,
                                                                          db.TRANSCRIPCION.fecha_elaboracion,
                                                                          db.TRANSCRIPCION.fecha_modificacion)

    lista_transcripciones = []
    # Obtenemos los roles de cada usuario
    for transcripcion in transcripciones:
        lista_transcripciones.append({'id' : transcripcion.id,
                                      'codigo': transcripcion.codigo,
                                      'fecha_elaboracion' : transcripcion.fecha_elaboracion,
                                      'fecha_modificacion': transcripcion.fecha_modificacion})

    return dict(message=message, transcripciones = lista_transcripciones)

@auth.requires(auth.is_logged_in() and auth.has_permission('manage_transcriptors', 'auth_user') and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def list_pending():
    """
        Lista las transcripciones pendientes por aprobar desde el punto de vista
        del supervisor.
    """

    message = "Transcripciones por Revisión"

    # obtenemos los transcriptores asociados
    all_transcriptors_for_user = db(db.REGISTRO_TRANSCRIPTORES.supervisor == auth.user.username)._select(db.REGISTRO_TRANSCRIPTORES.transcriptor)

    # Obtenemos las transcripciones
    transcripciones = db((db.TRANSCRIPCION.transcriptor.belongs(all_transcriptors_for_user)) &
                         (db.TRANSCRIPCION.estado == 'propuesta')).select(db.TRANSCRIPCION.id,
                                                                          db.TRANSCRIPCION.codigo,
                                                                          db.TRANSCRIPCION.transcriptor,
                                                                          db.TRANSCRIPCION.fecha_elaboracion,
                                                                          db.TRANSCRIPCION.fecha_modificacion)
    lista_transcripciones = []
    # Obtenemos los roles de cada usuario
    for transcripcion in transcripciones:
        lista_transcripciones.append({'id' : transcripcion.id,
                                      'transcriptor' : transcripcion.transcriptor,
                                      'codigo': transcripcion.codigo,
                                      'fecha_elaboracion' : transcripcion.fecha_elaboracion,
                                      'fecha_modificacion': transcripcion.fecha_modificacion})

    return dict(message=message, transcripciones = lista_transcripciones)

@auth.requires(auth.is_logged_in() and auth.has_permission('manage_transcriptors', 'auth_user') and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def list_approved():
    """
        List las transcripciones aprbadas por el supervisor.
    """

    message = "Transcripciones Aprobadas"

    # obtenemos los transcriptores asociados
    all_transcriptors_for_user = db(db.REGISTRO_TRANSCRIPTORES.supervisor == auth.user.username)._select(db.REGISTRO_TRANSCRIPTORES.transcriptor)

    # Obtenemos las transcripciones
    transcripciones = db((db.TRANSCRIPCION.transcriptor == auth.user.username) &
                         (db.TRANSCRIPCION.estado == 'aprobada')).select(db.TRANSCRIPCION.id,
                                                                         db.TRANSCRIPCION.codigo,
                                                                         db.TRANSCRIPCION.transcriptor,
                                                                         db.TRANSCRIPCION.fecha_elaboracion,
                                                                         db.TRANSCRIPCION.fecha_modificacion)
    lista_transcripciones = []
    # Obtenemos los roles de cada usuario
    for transcripcion in transcripciones:
        lista_transcripciones.append({'id' : transcripcion.id,
                                      'codigo': transcripcion.codigo,
                                      'fecha_modificacion': transcripcion.fecha_modificacion})

    return dict(message=message, transcripciones = lista_transcripciones)

def match_codigo_asig(text):
    """
      Del texto extraido se busca y se asocia el codigo de la asignatura
      a traves de una expresion regular.
    """
    expresion = '([A-Z]{2,3} *(-|\s|[^a-z|^A-Z|^0-9]|) *[0-9]{3,4})'
    patron = re.compile(expresion)
    matcher = patron.search(text)
    if matcher is not None:
        code = re.sub(' *(-|\s|[^a-z|^A-Z|^0-9]|) *', '', matcher.group(0))
        return code
    else:
        return None

def extract_text(path):
    """
      Se extraen el texto del programa en pdf para comparar al momento de
      realizar la transcripción.
    """
    os.system("pdftotext -layout " + path + " extraccion.txt")
    file = open("extraccion.txt", "r")
    text = file.read()
    file.close()
    os.system("rm extraccion.txt")
    return text

def extract_text_from_image(path):
    """
      Función para extraer el texto de la imagen para comparar
      al momento de hacer la transcripción.
    """
    tool = pyocr.get_available_tools()[0]
    lang = tool.get_available_languages()[2]

    req_image = []
    final_text = []

    image_pdf  = Image(filename=path, resolution=200)
    image_jpeg = image_pdf.convert('jpeg')

    for img in image_jpeg.sequence:
        img_page = Image(image=img)
        req_image.append(img_page.make_blob('jpeg'))

    for img in req_image:
        txt = tool.image_to_string(Pi.open(io.BytesIO(img)),
                                   lang=lang,
                                   builder=pyocr.builders.TextBuilder()
                                   )
        final_text.append(txt)

    trancription = ''
    for i in final_text:
        trancription += i

    return trancription

def check_required_fields(trasid):
    """
      Se chequea que los campos obligatorios estén llenos en el formulario.
    """

    transcripcion = db(db.TRANSCRIPCION.id == trasid).select().first()

    campos_obligatorios = [ 'codigo', 'denominacion',
                            'fecha_elaboracion', 'periodo',
                            'anio', 'horas_teoria',
                            'horas_practica', 'horas_laboratorio',
                            'creditos']

    check = True

    for campo in campos_obligatorios:
        if not(transcripcion[campo]):
            check = False

    return check

@auth.requires(auth.is_logged_in() and auth.has_permission('create_transcription') and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def delete_transcription():
    """
      Permite a un supervisor eliminar una transcripción
    """

    transid = request.args(0)
    transcripcion = db(db.TRANSCRIPCION.id == transid).select().first()
    os.remove(os.path.join(request.folder,'static/transcriptions/originalpdf',transcripcion.original_pdf))
    db(db.TRANSCRIPCION.id == transid).delete()

    session.flash = "Transcripción eliminada exitosamente."
    redirect(URL(c='transcriptions',f='list'))

@auth.requires(auth.is_logged_in() and auth.has_permission('create_transcription') and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def send_transcription():
    """
      Permite al usuario enviar una transcripcion al supervisor.
    """

    transid = request.args(0)

    if check_required_fields(transid):
        db.TRANSCRIPCION[transid] = dict(estado = 'propuesta')
        session.flash = "Transcripción enviada exitosamente a revisión."
    else:
        session.flash = "Faltan campos obligatorios para esta Transcripción. Complételos antes de enviarla a revisión."

    redirect(URL(c='transcriptions',f='list'))

@auth.requires(auth.is_logged_in() and auth.has_permission('manage_transcriptors', 'auth_user') and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def approve_transcription():
    """
      Permite al supervisor aprobar una transcripción.
    """

    transid = request.args(0)
    db.TRANSCRIPCION[transid] = dict(estado = 'aprobada', transcriptor = auth.user.username)

    session.flash = "Transcripción aprobada exitosamente."
    redirect(URL(c='transcriptions',f='list_pending'))

@auth.requires(auth.is_logged_in() and auth.has_permission('manage_transcriptors', 'auth_user') and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def delete_transcription_as_supervizer():
    """
    Permite al supervisor rechazar trsncripcionespendientes,
    """

    transid = request.args(0)
    transcripcion = db(db.TRANSCRIPCION.id == transid).select().first()
    os.remove(os.path.join(request.folder,'static/transcriptions/originalpdf',transcripcion.original_pdf))
    db(db.TRANSCRIPCION.id == transid).delete()

    session.flash = "Transcripción eliminada exitosamente."
    redirect(URL(c='transcriptions',f='following'))
