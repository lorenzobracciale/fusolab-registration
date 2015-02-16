from django.core.mail import send_mail, EmailMessage

email_file = '/root/script/emails.txt'

fp = open(email_file, 'rb')
email_data= fp.read()
fp.close()

message = EmailMessage(subject='Email soci fusolab', body='Caro Dario, ecco la lista fresca fresca. Cordialmente, Fusoci.', to=['dario.minghetti@gmail.com'], attachments=[('emails.txt', email_data, 'text/plain')])


message.send()
