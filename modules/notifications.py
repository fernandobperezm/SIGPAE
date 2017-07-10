# -*- coding: utf-8 -*-
from gluon import current
import os

'''
	Define funciones principales para enviar notificaciones via correo electronico
	en el sistema.

	Cuenta donde seran enviadas las notificaciones2:
				email: noreplysigpaeusb@gmail.com
				pass:  LXHyCmFD9rQPCqC
'''

def enviar_correo_rechazo_transcripcion(mail, usuario, transcripcion, comentario):
		asunto = '[SIGPAE] Transcripción Rechazada'

		# Mensaje del Correo

		mensaje  = '''<h1>Estimado/a %(nombres)s:</h1>
									<p>Cumplimos con comunicarle que su Transcripcion para
												<b> %(nombreTranscripcion)s</b>
												no fue aprobada.
									</p>''' % {'nombres': usuario['first_name'], 'nombreTranscripcion' : transcripcion}

		if comentario != "":
				mensaje += '''<p> Las razones por las cuales no fue aprobada son las siguientes: </p>
											<center>%(comentario)s</center>
											<br>
									''' % {'comentario':comentario}
		mensaje +=  '''
									<p> Usted puede ingresar al nuevamente al SIGPAE.
									    para editar este Transcripcion y enviarla nuevamente su para su aprobación.
									</p>
									<p>
										 Recuerde que siempre puede ver el estado de esta y sus tras transcripciones en el SIGPAE.</a>
									</p>
									<p> Saludos cordiales.</p>
								'''

		body   =  get_plantilla_html(mensaje)
		mail.send(usuario['email'], asunto, body)


def enviar_correo_validacion_coautor(mail, coautor, creador, producto):
		asunto = '[SIRADEx] Producto Validado'

		# Mensaje del Correo

		mensaje  = '''<h1>Estimado/a %(nombres)s:</h1>
									<p>Nos complace comunicarle que su Producto de Extensión
												<b> %(nombreProducto)s</b>
												cargado en el sistema SIRADEx por <b>%(usuarioCreador)s</b>
												fue validado satisfactoriamente por el Comité de Evaluación del Decanato de Extensión.
									</p>
									<p>
										 Recuerde que siempre puede ver el estado de este y sus otros productos
										 iniciando sesión en el <a href="https://siradex.dex.usb.ve/SiraDex">SIRADEx.</a>
									</p>
									<p> Saludos cordiales.</p>
							 '''  % {'nombres': coautor['nombres'], 'nombreProducto' : producto['nombre'], 'usuarioCreador' : creador['nombres'] }

		body   =  get_plantilla_html(mensaje)
		if coautor['correo_alter'] :
			mail.send(coautor['correo_alter'], asunto, body)
		mail.send(coautor['correo_inst'], asunto, body)

'''
		Envia un correo que indica si una producto fue rechazado.
		Parametros:
				Usuario  = [email, nombre]
				Producto = [nombre]
				Razon    = ''
'''
def enviar_correo_rechazo(mail, usuario, producto, razon):
		asunto = '[SIRADEx] Producto no Validado'

		# Mensaje del Correo

		mensaje  = '''<h1>Estimado/a %(nombres)s:</h1>
									<p>Cumplimos con comunicarle que su Producto de Extensión
												<b> %(nombreProducto)s</b>
												no fue validado por el Comité de Evaluación del Decanato de Extensión.
									</p>''' % {'nombres': usuario['nombres'], 'nombreProducto' : producto['nombre']}

		if razon != "":
				mensaje += '''<p> Las razones por las cuales no fue validado son las siguientes: </p>
											<center>%(razon)s</center>
											<br>
									''' % {'razon':razon}
		mensaje +=  '''
									<p> Usted puede ingresar al <a href="https://siradex.dex.usb.ve/SiraDex">SIRADEx.</a>
											para editar este producto y solicitar nuevamente su evaluación.
									</p>
									<p>
										 Recuerde que siempre puede ver el estado de este y sus otros productos
										 iniciando sesión en el Sistema SIRADEx.</a>
									</p>
									<p> Saludos cordiales.</p>
								'''

		body   =  get_plantilla_html(mensaje)
		if usuario['correo_alter'] :
			mail.send(usuario['correo_alter'], asunto, body)
		mail.send(usuario['correo_inst'], asunto, body)


def enviar_correo_contacto(mail, usuario, asunto, mensaje):
		email  = usuario['email']
		asunto = '[SIRADEx] ' + asunto

		# Mensaje del Correo
		mensaje  = '''<h1>Estimado/a %(nombres)s:</h1>
									<p>%(mensaje)s
									</p>''' % {'nombres': usuario['nombres'], 'mensaje' : mensaje}

		body   =  get_plantilla_html(mensaje)

		mail.send(email, asunto, body)

'''
		Envia un correo de Bienvenida a SiraDex.
		Parametros:
				Usuario  = {email, nombre}
				Razon    = ''
'''

def enviar_correo_bienvenida(mail, usuario):
	email  = usuario['email']
	asunto = '[SIRADEx] Bienvenida'

	# Mensaje del Correo

	mensaje  = '''<h1>Bienvendo al SIRADEx</h1>
								<p> Estimado/a %(nombres)s:
								</p>''' % {'nombres': usuario['nombres']}

	mensaje +=  '''
								<p>
									Ahora podrá subir sus productos y esperar la validación por parte del Comité de Evaluación del Decanato de Extensión.
								</p>
								<p>
									Lo primero que debe realizar es ingresar al <a href="https://siradex.dex.usb.ve/EditarPerfil">SIRADEx</a>
									para actualizar su número de teléfono y correo electrónico.
								</p>
								<p> Saludos cordiales.</p>
							'''

	body   =  get_plantilla_html(mensaje)

	mail.send(email, asunto, body)


# Define la plantilla html del correo electronico.
# con el campo mensaje dependiendo del tipo sdel correo que se quiere.
def get_plantilla_html(mensaje):

		usb_logo_url = 'https://docs.google.com/uc?id=0B7O8rYGssxZkTnFJWGRjMGo0Zzg'

		plantilla = '''
				<html>
					<head>
						<meta charset = "UTF-8">
						<style>

							header, body, footer {
								display: block;
								font-family: "Helvetica";
							}

							header, body {
								color: black;
							}

							hr {
								color: #333333;
								margin-top: 15px;
							}

							img {
									float: none;
									width: 135px;
							 }
							 h1 {
								 font-size: 20px;
								 margin: 2px;
							 }
							 h2 {
								 font-size: 15px;
								 margin: 2px;
							 }

							 .bottom-msg {
										margin-top: 20px;
										font: 10px verdana, arial, helvetica, sans-serif;
										color: black;
							 }

							 footer{
								 background-color: #333333;
								 padding-top: 3px;
								 padding-bottom: 3px;
								 font: 10px verdana, arial, helvetica, sans-serif;
								 color: #FFFFFF;
							 }
						</style>
					</head>

					<header>
						<center>
							<img src='%(urlimg)s' alt="Logo" title="Logo" style="display:block" width="135px" height="90px">
							<h1>Universidad Simón Bolívar</h1>
							<h2>Dirección de Admisión y Control de Estudios</h2>
							<h2>Sistema de Gestión de Programas Académicos de Estudio SIGPAE</h2>
						</center>
						<hr>
					</header>

					<body>
						%(mensaje)s
						<div class='bottom-msg'>
								<center>
										<p> Este mensaje fue enviado de manera automatica por el Sistema SIGPAE</p>
										<p> Por favor no responda a este correo. En caso de duda o comentarios póngase en contacto con
										la Dirección de Admisión y Control de Estudios (DACE).</p>
								</center>
						</div>
					</body>

					<footer>
						<center>
							<p>Sartenejas, Baruta, Edo. Miranda - Apartado 89000 Cable Unibolivar Caracas Venezuela. Teléfono +58 0212-9063111</p>
							<p>Litoral. Camurí Grande, Edo. Vargas Parroquia Naiguatá. Teléfono +58 0212-9069000</p>
						</center>
					</footer>
				</html>
		''' % {'urlimg' : usb_logo_url, 'mensaje': mensaje}

		return plantilla
