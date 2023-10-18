# Fastapi Base(HEAPDUMP in Python)

## Indice
  - [Descripción](#descripción)
  - [Path/Funciones](#pathfunciones)
  - [Estructura](#estructura)
    - [Directorios](#directorios)
    - [Ficheros](#ficheros)
  - [Local](#local)
  
<a name=descripcion></a>
## Descripción:
Micro para sacar HeapDump/ThreadDump de pods. 

<a name=funciones></a>
## Path/Funciones:
Esquema de los Path publicados
Funciones que realiza en mas detalle

<a name=funciones></a>
## Estructura:
<a name=directorios></a>
### Directorios:
Descripcion de las carpetas que se usan y que se almacena en ellas 
<a name=ficheros></a>
### Ficheros:
Descripcion de los ficheros con las funciones mas importantes

<a name=local></a>
## Local:
Explicacion de como poder probarlo en local y desarrollar (docker):

Ejemplo:
```bash
    docker build -t name-imge .
    docker run -d -p 8000:8000 --env-file local.env --name alma-status shuttle-alma:latest
```

Tener en cuenta que la aplicación no se puede ejecutar si no es contenida dentro de un Docker
ya que hay librerías que no están disponibles para Windows (ej. uvloop).