# -*- coding: utf-8 -*-
from gluon import current
import os

'''
	Este modulo define funciones principales para enviar notificaciones via correo electronico
	en el sistema.

	Cuenta donde seran enviadas las notificaciones2:
				email: noreplysigpaeusb@gmail.com
				pass:  LXHyCmFD9rQPCqC
'''

def enviar_correo_rechazo_transcripcion(mail, usuario, transcripcion, comentario):
	asunto = '[SIGPAE] Transcripción Rechazada'

	# Mensaje del Correo

	mensaje  = '''<h1>Estimado/a %(nombres)s:</h1>
								<p>Cumplimos con comunicarle que su Transcripción para
											<b> %(nombreTranscripcion)s</b>
											no fue aprobada.
								</p>''' % {'nombres': usuario['first_name'], 'nombreTranscripcion' : transcripcion}

	if comentario != "":
			mensaje += '''<p> Las razones por las cuales no fue aprobada son las siguientes: </p>
										<center>%(comentario)s</center>
										<br>
								''' % {'comentario':comentario}
	mensaje +=  '''
								<p> Usted puede ingresar al nuevamente SIGPAE para editar esta Transcripción y enviarla nuevamente para su aprobación.
								</p>
								<p>
									 Recuerde que siempre puede ver el estado de esta y sus otras transcripciones en el SIGPAE.</a>
								</p>
								<p> Saludos cordiales.</p>
							'''

	body   =  get_plantilla_html(mensaje)
	mail.send(usuario['email'], asunto, body)

def enviar_correo_reasignacion_transcripcion(mail, usuario, transcripcion, comentario):
	asunto = '[SIGPAE] Transcripción Asignada'

	# Mensaje del Correo

	mensaje  = '''<h1>Estimado/a %(nombres)s:</h1>
								<p>Cumplimos con comunicarle que le ha sido asignada una nueva Transcripción:
											<b> %(nombreTranscripcion)s.</b>
								</p>''' % {'nombres': usuario['first_name'], 'nombreTranscripcion' : transcripcion}

	if comentario != "":
			mensaje += '''<p> La reasignación viene acompañada del siguiente comentario: </p>
										<center>%(comentario)s</center>
										<br>
								''' % {'comentario':comentario}
	mensaje +=  ''' <p> Usted puede ingresar desde ya al SIGPAE para editar esta Transcripción y enviarla para su aprobación.
					</p>
					<p>
					 Recuerde que siempre puede ver el estado de esta y sus otras transcripciones en el SIGPAE.</a>
					</p>
					<p> Saludos cordiales.</p>
			     '''

	body   =  get_plantilla_html(mensaje)
	mail.send(usuario['email'], asunto, body)

def enviar_correo_contacto(mail, usuario, asunto, mensaje):
		email  = usuario['email']
		asunto = '[SIRADEx] ' + asunto

		# Mensaje del Correo
		mensaje  = '''<h1>Estimado/a %(nombres)s:</h1>
									<p>%(mensaje)s
									</p>''' % {'nombres': usuario['nombres'], 'mensaje' : mensaje}

		body   =  get_plantilla_html(mensaje)

		mail.send(email, asunto, body)


def get_plantilla_html(mensaje):
	"""
		Define la plantilla general para los correos electronicos enviados por
		el sistema.
	"""
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
						<h2>Sistema de Gestión de Programas Analíticos de Estudio SIGPAE</h2>
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
