# SIGPAE
## Resumen

Este repositorio contiene el código fuente necesario para SIGPAE. En este README se encuentra la información necesaria para la instalación en ambiente de desarrollo y producción.

Para **SIGPAE WS** leer el README correspondiente al repositorio. Se recomienda primero seguir las instrucciones de SIGPAE.

## Estructura del repositorio

La rama ```master``` contiene el código fuente para el ambiente de Desarrollo (local). La rama ```deploy``` es la versión más actualizada en el ambiente de producción. Existen diferencias entre las configuraciones de ambas ramas. Por favor tener esto en cuenta al momento de hacer merge con la rama ```deploy```

## Dirección del Servidor

El servidor se encuentra disponible en la siguiente dirección https://159.90.61.100.

El usuario y la clave de acceso para la conexión SSH con el servidor serán entregados en un documento aparte.

## Instalación

### Web2Py

Primero, se debe descargar Web2Py [desde el sitio web oficial](http://www.web2py.com/init/default/download) y descomprimir el archivo .zip en el directorio de su preferencia.

Una vez hecho esto, dirigirse a ```web2py/applications/``` y clonar este repositorio. Tambien se debe clonar dentro de este directorio **SIGPAE WS**.

### Librerias Requeridas

Luego de la instalación de Web2Py, se recomienda correr los siguientes comandos para instalar las librerias necesarias del sistema.

- Necesarias para la conexión con el CAS
```bash
$ sudo apt-get update
$ sudo apt-get install libsasl2-dev python-dev libldap2-dev libssl-dev ldap-utils
```
- Necesarias para la lectura de PDF (texto e imágenes)
```bash
$ sudo apt-get install xpdf
$ sudo apt-get install libmagickwand-dev
$ sudo apt-get install tesseract-ocr libtesseract-dev libleptonica-dev
$ sudo apt-get install tesseract-ocr-eng tesseract-ocr-spa
```
- Necesarias para el funcionamiento de algunos módulos de SIGPAE
```bash
$ cd web2py/applications/SIGPAE/
$ pip install -R requirements.txt
```

### Base de Datos

Realizar la instalación de PostgreSQL de manera habitual. Luego, crear la base de datos.

Ingresar a PostgreSQL
```bash
$ sudo -su postgres
$ psql
```

Crear el usuario y la base de datos si no existen en la consola de postgres.

```bash
$ create user sigpae with password '123123';
$ create database newsigpae with owner sigpae;
```  

**SIGPAE** y **SIGPAE WS** usan el mismo usuario y password. En la version de desarrollo (rama ```master```) y la versión de producción (rama ```deploy```) los passwords difieren.

## Ejecución

### Local
Desde el direcorio raiz de Web2Py ejecutar:
```bash
$ python web2py.py
```  

Por lo general, se solicita un password que será necesario para acceder a la interfaz de administración de Web2Py. Luego de esto el sistema SIGPAE será accesible localmente.

### En Servidor

Subir los cambios al repositorio de git y ejecutar en el servidor via SSH.
```bash
$ cd /home/www-data/web2py/applications/SIGPAE_WS
$ sudo git pull
```  

Los cambios generalmente estarán disponibles de inmediato. Algunos cambios pudiesen requerir reiniciar el servicio de Apache del servidor de manera habitual.


```bash
$ sudo /etc/init.d/apache2 restart
```  

 Uno de los cambios mas comunes que requiere de esto son los realizados a los scripts en el directorio ```modules```.

## Desarrolladores

### Abril - Julio 2017
- [Leonardo Martínez](https://github.com/leotms)
- [Jonnathan Chiu Ng](https://github.com/Stahet)
- [Nicolás Mañán](https://github.com/nmanan)    

## Última Actualización
- 27 de Julio, 2017.
