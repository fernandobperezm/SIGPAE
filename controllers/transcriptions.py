import os
import sys
import io
import re
from wand.image import Image
from PIL import Image as Pi
import pyocr
import pyocr.builders

@auth.requires(auth.is_logged_in() and auth.has_permission('manage_transcriptors', 'auth_user') and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def transcriptors():
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

            for i in roles:
                if i['group_id'] in no_permitidos:
                    puede_transcribir = False
                    session.flash = 'Usuarios con rol de DECANATO, COORDINACION o DEPARTAMENTO no pueden transcribir programas.'

            # luego, revisamos si ya se encuentra transcribiendo para alguno supervisor
            existente = db(db.REGISTRO_TRANSCRIPTORES.transcriptor == usuario.username).select()
            if existente:
                puede_transcribir = False
                session.flash = 'El Usuario ya es Transcriptor de otro DECANATO, COORDINACION o DEPARTAMENTO.'

            # finalmente, si puede transcribir
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
    message = "Seguimiento de Transcripciones"

    # obtenemos los transcriptores asociados
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
                                                  labels={'transcriptor':'Nuevo Transcriptor'})

    if formulario_reasignar.process(formname="formulario_reasignar").accepted:

        transcription_id = formulario_reasignar.vars.transcription_id
        transcriptor = formulario_reasignar.vars.transcriptor

        # buscamos la transcripcion a reasignar y la actualizamos
        db.TRANSCRIPCION[transcription_id] = dict(transcriptor = transcriptor)
        session.flash = "Reasignación exitosa."
        redirect(URL(c='transcriptions', f='following'))

    elif formulario_reasignar.errors:
        response.flash = 'Error en la reasignación, intente nuevamente.'

    return dict(message=message, transcripciones = lista_transcripciones, formulario_reasignar = formulario_reasignar)


@auth.requires(auth.is_logged_in() and auth.has_permission('create_transcription') and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def add():

    mensaje = 'Nueva Transcripción'

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

@auth.requires(auth.is_logged_in() and auth.has_permission('create_transcription') and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def edit():

    id =  request.vars['id']
    if not isinstance(id, str):
        id = id[0]

    transcription = db(db.TRANSCRIPCION.id == id).select().first()

    pdfurl = transcription.original_pdf
    code   = transcription.codigo
    text   = transcription.texto

    if 'file_type' in request.vars:
        if request.vars['file_type'] == "Texto":

            text = extract_text(os.path.join(request.folder,'static/transcriptions/originalpdf',request.vars['file']))
        elif request.vars['file_type'] == "Imagen":
            text = extract_text_from_image(os.path.join(request.folder,'static/transcriptions/originalpdf',request.vars['file']))

        db.TRANSCRIPCION[id] = dict(texto = text)
    if 'extract_type' in request.vars:
        if request.vars['extract_type'] == "Código y Departamento":
            code = match_codigo_asig(text)
            db.TRANSCRIPCION[id] = dict(codigo = code)

    pdfurl = URL('static','transcriptions/originalpdf/' + pdfurl)

    form = SQLFORM(db.TRANSCRIPCION,
                   record = id,
                   fields = ['codigo', 'denominacion', 'fecha_elaboracion',
                             'periodo', 'horas_teoria', 'horas_practica',
                             'horas_laboratorio' , 'creditos', 'anio',
                             'periodo_hasta', 'anio_hasta',
                             'sinopticos','ftes_info_recomendadas','requisitos',
                             'estrategias_met','estrategias_eval','justificacion',
                             'observaciones','objetivos_generales','objetivos_especificos',
                             'campo_1', 'campo_1_cont',
                             'campo_2', 'campo_2_cont',
                             'campo_3', 'campo_3_cont'],
                   submit_button=T('Guardar')
                   )

    form.append(INPUT(_type='button', _value='Cancel', _onclick='window.location=\'%s\';;return false' % URL(c='transcriptions', f='list')))

    if form.accepts(request, session, hideerror=True, formname = "transcription_form"):
        session.flash = 'Transcripción guardada satisfactoriamente.'

        if form.vars.campo_1 != '':
            exists = db(db.CAMPOS_ADICIONALES_TRANSCRIPCION.nombre == form.vars.campo_1).select()
            if len(exists) == 0:
                db.CAMPOS_ADICIONALES_TRANSCRIPCION.insert(nombre=form.vars.campo_1.capitalize())
        if form.vars.campo_2 != '':
            exists = db(db.CAMPOS_ADICIONALES_TRANSCRIPCION.nombre == form.vars.campo_2).select()
            if len(exists) == 0:
                db.CAMPOS_ADICIONALES_TRANSCRIPCION.insert(nombre=form.vars.campo_2.capitalize())
        if form.vars.campo_3 != '':
            exists = db(db.CAMPOS_ADICIONALES_TRANSCRIPCION.nombre == form.vars.campo_3).select()
            if len(exists) == 0:
                db.CAMPOS_ADICIONALES_TRANSCRIPCION.insert(nombre=form.vars.campo_3.capitalize())

        redirect(URL(c='transcriptions', f='list'))

    elif form.errors:
        print(form.errors)
        response.flash = 'Hay errores en el formulario'

    return dict(text=text, pdfurl=pdfurl, code=code, id = id, form = form)

@auth.requires(auth.is_logged_in() and auth.has_permission('manage_transcriptors', 'auth_user')
               and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def view():

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

    form = SQLFORM(db.TRANSCRIPCION,
                   record   = id,
                   writable = False,
                   fields = ['codigo', 'denominacion', 'fecha_elaboracion',
                             'periodo', 'horas_teoria', 'horas_practica',
                             'horas_laboratorio' , 'creditos', 'anio',
                             'periodo_hasta', 'anio_hasta',
                             'sinopticos','ftes_info_recomendadas','requisitos',
                             'estrategias_met','estrategias_eval','justificacion',
                             'observaciones','objetivos_generales','objetivos_especificos',
                             'campo_1', 'campo_1_cont',
                             'campo_2', 'campo_2_cont',
                             'campo_3', 'campo_3_cont'],
                   submit_button=T('Guardar')
                   )

    return dict(text=text, pdfurl=pdfurl, code=code, id = id, form = form)

@auth.requires(auth.is_logged_in() and auth.has_permission('manage_transcriptors', 'auth_user')
               and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def approval_view():

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

    form = SQLFORM(db.TRANSCRIPCION,
                   record   = id,
                   writable = False,
                   fields = ['codigo', 'denominacion', 'fecha_elaboracion',
                             'periodo', 'horas_teoria', 'horas_practica',
                             'horas_laboratorio' , 'creditos', 'anio',
                             'periodo_hasta', 'anio_hasta',
                             'sinopticos','ftes_info_recomendadas','requisitos',
                             'estrategias_met','estrategias_eval','justificacion',
                             'observaciones','objetivos_generales','objetivos_especificos',
                             'campo_1', 'campo_1_cont',
                             'campo_2', 'campo_2_cont',
                             'campo_3', 'campo_3_cont'],
                   submit_button=T('Guardar')
                   )

    return dict(text=text, pdfurl=pdfurl, code=code, id = id, form = form)

@auth.requires(auth.is_logged_in() and auth.has_permission('create_transcription')
               and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def transcriptor_view():

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

    form = SQLFORM(db.TRANSCRIPCION,
                   record   = id,
                   writable = False,
                   fields = ['codigo', 'denominacion', 'fecha_elaboracion',
                             'periodo', 'horas_teoria', 'horas_practica',
                             'horas_laboratorio' , 'creditos', 'anio',
                             'periodo_hasta', 'anio_hasta',
                             'sinopticos','ftes_info_recomendadas','requisitos',
                             'estrategias_met','estrategias_eval','justificacion',
                             'observaciones','objetivos_generales','objetivos_especificos',
                             'campo_1', 'campo_1_cont',
                             'campo_2', 'campo_2_cont',
                             'campo_3', 'campo_3_cont'],
                   submit_button=T('Guardar')
                   )

    return dict(text=text, pdfurl=pdfurl, code=code, id = id, form = form)

@auth.requires(auth.is_logged_in() and auth.has_permission('create_transcription') and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def aditional_field_selector():

    string = ''
    if len(request.vars) == 0:
        return ''
    else:
        if request.vars.campo_1:
            string = request.vars.campo_1
        if request.vars.campo_2:
            string = request.vars.campo_2
        if request.vars.campo_3:
            string = request.vars.campo_3

    pattern = '%' + string.capitalize() + '%'
    selected = [row.nombre for row in db(db.CAMPOS_ADICIONALES_TRANSCRIPCION.nombre.like(pattern)).select()]

    return_string = ''.join([OPTION(k).xml() for k in selected])
    return return_string

@auth.requires(auth.is_logged_in() and auth.has_permission('create_transcription') and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def list():
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
    expresion = '([A-Z]{2,3} *(-|\s|[^a-z|^A-Z|^0-9]|) *[0-9]{3,4})'
    patron = re.compile(expresion)
    matcher = patron.search(text)
    if matcher is not None:
        code = re.sub(' *(-|\s|[^a-z|^A-Z|^0-9]|) *', '', matcher.group(0))
        return code
    else:
        return None

def extract_text(path):
    os.system("pdftotext -layout " + path + " extraccion.txt")
    file = open("extraccion.txt", "r")
    text = file.read()
    file.close()
    os.system("rm extraccion.txt")
    return text

def extract_text_from_image(path):
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

@auth.requires(auth.is_logged_in() and auth.has_permission('create_transcription') and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def delete_transcription():

    transid = request.args(0)
    transcripcion = db(db.TRANSCRIPCION.id == transid).select().first()
    os.remove(os.path.join(request.folder,'static/transcriptions/originalpdf',transcripcion.original_pdf))
    db(db.TRANSCRIPCION.id == transid).delete()

    session.flash = "Transcripción eliminada exitosamente."
    redirect(URL(c='transcriptions',f='list'))

@auth.requires(auth.is_logged_in() and auth.has_permission('create_transcription') and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def send_transcription():

    transid = request.args(0)
    db.TRANSCRIPCION[transid] = dict(estado = 'propuesta')

    session.flash = "Transcripción enviada exitosamente a revisión."
    redirect(URL(c='transcriptions',f='list'))

@auth.requires(auth.is_logged_in() and auth.has_permission('manage_transcriptors', 'auth_user') and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def approve_transcription():

    transid = request.args(0)
    db.TRANSCRIPCION[transid] = dict(estado = 'aprobada', transcriptor = auth.user.username)

    session.flash = "Transcripción aprobada exitosamente."
    redirect(URL(c='transcriptions',f='list_pending'))

@auth.requires(auth.is_logged_in() and auth.has_permission('manage_transcriptors', 'auth_user') and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def reject_transcription():

    transid = request.args(0)
    db.TRANSCRIPCION[transid] = dict(estado = 'pendiente')

    session.flash = "Transcripción rechazada exitosamente."
    redirect(URL(c='transcriptions',f='list_pending'))

@auth.requires(auth.is_logged_in() and auth.has_permission('manage_transcriptors', 'auth_user') and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def delete_transcription_as_supervizer():

    transid = request.args(0)
    transcripcion = db(db.TRANSCRIPCION.id == transid).select().first()
    os.remove(os.path.join(request.folder,'static/transcriptions/originalpdf',transcripcion.original_pdf))
    db(db.TRANSCRIPCION.id == transid).delete()

    session.flash = "Transcripción eliminada exitosamente."
    redirect(URL(c='transcriptions',f='following'))
