# -*- coding: utf-8 -*-
'''
    Insersión de registros en el LOG y Bitácoras del sistema.
'''
from gluon import current

def regiter_in_log(db, auth, accion, descripcion):
    '''
        Registra un evento en la bitacora de la transcripcion.
    '''

    # Obtenemos el rol del usuario

    # obtenemos todos los roles del usuario
    roles_list      = db(db.auth_membership.user_id == auth.user.id).select()
    roles           = ""
    for role in roles_list:
        roles += role.group_id.role + " "

    db.LOG_SIGPAE.insert(
        usuario = auth.user.username,
        rol_usuario = roles,
        accion = accion,
        descripcion = descripcion
    )

def regiter_in_transcriptions_journal(db, auth, id, accion, descripcion):
    '''
        Registra un evento en la bitacora de la transcripcion.
    '''

    # Obtenemos el rol del usuario

    rol  = ''
    if auth.has_membership(auth.id_group(role="TRANSCRIPTOR")):
        rol = 'TRANSCRIPTOR'
    elif auth.has_membership(auth.id_group(role="DECANATO")):
        rol = 'DECANATO'
    elif auth.has_membership(auth.id_group(role="DEPARTAMENTO")):
        rol = 'DEPARTAMENTO'
    elif auth.has_membership(auth.id_group(role="COORDINACION")):
        rol = 'COORDINACION'

    db.BITACORA_TRANSCRIPCION.insert(
        transcripcion = id,
        usuario = auth.user.username,
        rol_usuario = rol,
        accion = accion,
        descripcion = descripcion
    )

def regiter_in_programs_journal(db, auth, id, accion, descripcion):
    '''
        Registra un evento en la bitacora de los programas.
    '''

    # Obtenemos el rol del usuario

    rol  = ''
    if auth.has_membership(auth.id_group(role="TRANSCRIPTOR")):
        rol = 'TRANSCRIPTOR'
    elif auth.has_membership(auth.id_group(role="DECANATO")):
        rol = 'DECANATO'
    elif auth.has_membership(auth.id_group(role="DEPARTAMENTO")):
        rol = 'DEPARTAMENTO'
    elif auth.has_membership(auth.id_group(role="COORDINACION")):
        rol = 'COORDINACION'

    db.BITACORA_PROGRAMA.insert(
        programa = id,
        usuario = auth.user.username,
        rol_usuario = rol,
        accion = accion,
        descripcion = descripcion
    )
