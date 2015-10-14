#!/bin/bash
/root/script/crea_lista_emails.sh | tee /root/script/emails.txt
sendemail -f fusoci@fusolab.net -t xxxx@gmail.com -m "messaggio" -u "email fusolab" -a /root/script/emails.txt
