
## Requerimientos

Primero installar las siguientes librerias:

```bash
$ sudo apt-get update
$ sudo apt-get install libsasl2-dev python-dev libldap2-dev libssl-dev ldap-utils
```

Crear la base de datos en PostgreSQL

Ingresar a PostgreSQL
```bash
$ sudo -su postgres
$ psql
```
Crear el usuario y la base de datos si no existen en la consola de postgres. (El usuario y el pass es el
mismo de SIGPAE_HISTORICO de PowerSoft)

```bash
$ create user sigpae with password '123123';
$ create database newsigpae with owner sigpae;
```  
