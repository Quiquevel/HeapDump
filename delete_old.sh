#!/bin/bash

# Directorio donde se encuentran los archivos
directorio="/app/downloads"

# Número de días, ajusta según sea necesario
dias=1

# Encuentra y borra los archivos más antiguos de n días
find $directorio -type f -mtime +$dias -exec rm {} \;