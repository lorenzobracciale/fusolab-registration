from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.core.servers.basehttp import FileWrapper
import os, mimetypes, urllib
from ingresso.models import Card
from models import Greeting

def salutatore(request, cardid=None, manual_speech=None):
    to_say, name = "", ""
    last_greeting, first_time, current_greeting = None, None, None
    c = None
    try:
        c = Card.objects.get(sn = cardid)
        name = c.user.user.first_name
        current_greeting = Greeting(user = c.user)
        current_greeting.save()
        last_greeting = Greeting.objects.filter(user = c.user).order_by('-date')[1]
    except Card.DoesNotExist:
        name = "signor nessuno"
    except Greeting.DoesNotExist:
        last_greeting = None
    except IndexError:
        last_greeting = None
        first_time = ", benvenuto al fusolab. Oggi ci siamo conosciuti, me lo ricordero' per sempre"

    to_say = "ciao %s tessera numero %s" % (name, cardid)

    if last_greeting and current_greeting:
        to_say += ", sono %d secondi che non ci vediamo, mi sei mancato tanto" % (current_greeting.date - last_greeting.date).seconds
    elif first_time:
        to_say += first_time

    if manual_speech:
        to_say = manual_speech

    os.system("cd /var/www/fusolab/media/salutatore; echo \"" + to_say + "\"|/usr/bin/text2wave -eval \"(voice_pc_diphone)\" -o saluto.wav -; lame -b 80 saluto.wav saluto.mp3")
    wrapper = FileWrapper(file( '/var/www/fusolab/media/salutatore/saluto.mp3' ))
    response = HttpResponse(wrapper, content_type='audio/mpeg')
    response['Content-Length'] = os.path.getsize( '/var/www/fusolab/media/salutatore/saluto.mp3' )
    return response

def say(request, sentence):
    if sentence == "criticalmass":
        sentence = "Benvenuta critical mass al fusolab, la sai questa e' fortissima: due ciclisti si incontrano a trastevere quando uno dei due dice all'altro: sai come si chiama questo fiume? e l'altro: no. Aaaarhrhrhrhhahahahahahharrrhhh ahh ahhhh ahhhhrrrrr"
    return salutatore(request, manual_speech=sentence)

