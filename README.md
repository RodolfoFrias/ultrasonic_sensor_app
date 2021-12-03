# Proyecto IOT
### Descripción del proyecto

Este proyecto consiste en un sensor ultrásonico que realiza mediciones de distacia y envia notificaciones a través de Telegram.

### Requerimientos
* NodeJS version 12 o superior
* Micropython
* Algún IDE que permite cargar código a la NodeMCU

### Intalación
Lo primero es correr el servidor que será el encargado de recibir la petición y enviar la notificación a Telegram.

`npm run start:dev`

El archivo de python se encuntra en la siguiente ruta:

```
project
└───src
|   └───scripts
|       └───main.py
```


