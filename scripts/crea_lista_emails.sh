#!/bin/bash

# loggare questi campi della table auth_user nel db fusoci
# prendere i campi first_name, last_name e email
# creare comma separated values

SQL="SELECT first_name, ',', last_name, ',', email FROM auth_user;"
USERNAME='fusoci'
#PASSWORD='EvdvS6AFZLqSU9xd'
PASSWORD='fdjofd09d'
#PASSWORD='bzzauz'

echo $SQL | mysql --user="$USERNAME" --password="$PASSWORD" fusoci | tr -d '[:blank:]'


