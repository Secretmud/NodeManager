#!/bin/bash
export FLASK_APP=flaskr/
export FLASK_ENV=development
db_check="$(pwd)/instance/flaskr.sqlite"
printf "%s\n" "$db_check"
if [ "$1" == "-db" ] || [ ! -f "$db_check" ];
then
  flask init-db
fi
flask run
