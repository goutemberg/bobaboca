#!/usr/bin/env sh

# O shell irá encerrar a execução do script quando um comando falhar
set -e



collectstatic.sh
#makemigrations.sh
runserver.sh
migrate.sh
#gunicorn.sh
wait_psql.sh