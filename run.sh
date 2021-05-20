#!/bin/bash
export FLASK_APP=flaskr/
export FLASK_ENV=development
if [ "$1" == "-db" ];
then
  flask init-db
fi
flask run
