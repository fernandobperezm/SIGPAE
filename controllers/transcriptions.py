import os

@auth.requires(auth.is_logged_in() and auth.has_permission('create_transcription'))
def upload_pdf():

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
        redirect(URL('edit_transcription', vars = dict(file = form.vars.file, file_type = form.vars.file_type, extract_type = form.vars.extract_type)))

    return dict(message = mensaje, form = form)


def edit_transcription():

    message = request.vars['file'] + '\n' +  request.vars['file_type'] + '\n' +  request.vars['extract_type'] + ' '
    text = ""
    if request.vars['extract_type'] == "Solo Texto":
        text = extract_text(os.path.join(request.folder,'static/transcriptions/originalpdf',request.vars['file']))

    pdfurl = URL('static','transcriptions/originalpdf/' + request.vars['file'])
    return dict(message=message, text=text, pdfurl=pdfurl)

def extract_text(path):
    os.system("pdftotext -layout " + path + " extraccion.txt")
    file = open("extraccion.txt", "r")
    text = file.read()
    file.close()
    os.system("rm extraccion.txt")
    return text
