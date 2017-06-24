import os
import sys
import io
import re
from wand.image import Image
from PIL import Image as Pi
import pyocr
import pyocr.builders

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
        id = db.TRANSCRIPCION.insert(original_pdf = form.vars.file)['id']
        redirect(URL('edit', vars = dict(id = id, file = form.vars.file, file_type = form.vars.file_type, extract_type = form.vars.extract_type)))

    return dict(message = mensaje, form = form)

@auth.requires(auth.is_logged_in() and auth.has_permission('create_transcription') and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def edit():

    id =  request.vars['id']
    print type(id)
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
                             'sinopticos','ftes_info_recomendadas','requisitos',
                             'estrategias_met','estrategias_eval','justificacion',
                             'observaciones','objetivos_generales','objetivos_especificos'],
                   submit_button=T('save')
                   )

    if form.accepts(request, session, hideerror=True, formname = "transcription_form"):
        form.process()
        redirect(URL('list'))
    elif form.errors:
        print(form.errors)
        response.flash = SPAN('Hay errores en el formulario', _class='whatever')

    return dict(text=text, pdfurl=pdfurl, code=code, id = id, form = form)

@auth.requires(auth.is_logged_in() and auth.has_permission('create_transcription') and not(auth.has_membership(auth.id_group(role="INACTIVO"))))
def list():
    message = "Transcripciones"

    # Obtenemos las transcripciones
    transcripciones = db(db.TRANSCRIPCION).select(db.TRANSCRIPCION.id,
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

    print("Will use tool '%s'" % (tool.get_name()))
    print(tool.get_available_languages())

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
    db(db.TRANSCRIPCION.id == transid).delete()

    session.flash = "Transcripción eliminada exitosamente."
    redirect(URL(c='transcriptions',f='list'))
