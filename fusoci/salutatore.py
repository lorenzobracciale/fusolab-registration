from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.core.servers.basehttp import FileWrapper
import os, mimetypes, urllib
from models import *
import random

jokes = ["Bill Gates sta' facendo l'amore quando la compagna gli dice: Caro non godo per niente! E lui: Annullo, Riprovo, Ignoro o Tralascio? ",
        "Quanti programmatori ci vogliono per cambiare una lampadina?  Nessuno. E' un problema aaarduer. ",
        "Un IBM Pentium sta facendo la corte ad un Motorola Macintosh. Che programma hai per stasera?. Mi dispiace, devo uscire con un' Amiga. ",
        "Due topi si incontrano dopo tanto tempo, uno chiede all'altro. Come sta tuo figlio? Sta bene grazie, si e' laureato in America e ora lavora nel campo dell'informatica. E di che cosa si occupa precisamente? Fa il maaauuuuuss. ",
        "Un bambino chiede al padre cosa fossero le icone, il padre risponde. Sono immagini sacre. E il figlio. E perche' windows ne ha tante? Il padre. Perche' per farlo funzionare ci vuole un miracolo. ",
        "Fonzie con un pugno riusciva a far partire il giu box. Fusolab due punto zero con un pugno fa partire i concerti a San Siro. ",
        "Maradona palleggia con le arance, Fusolab Due Punto Zero palleggia con Maradona che palleggia con le arance. ",
        ]

def custom_greeting(cardid):
    to_say = None
    if cardid == "1d74a629": #lorena
        to_say = "In informatica, il kernel costituisce il nucleo di un sistema operativo. Si tratta di un software avente il compito di fornire ai processi in esecuzione sull'elaboratore un accesso sicuro e controllato all'hardware. Dato che possono esserne eseguiti simultaneamente piu' di uno, il kernel ha anche la responsabilia' di assegnare una porzione di tempo-macchina (scheduling) e di accesso all'hardware a ciascun programma (multitasking)."
    elif cardid == "faf70430": #fish
        to_say = "Ciao Fish, hai fatto lo sburratone?"
    elif cardid == "7aa23d30": #silvio
        to_say = "Ciao Silvio, grazie di essere tornato, sei l'unico che prende le doppio malto, lo sai? Vuole mica un caffettini? Arrivederci, Arrivederci, Arrivederci"
    elif cardid == "0a2d3d30": #michele
        to_say == "E' arrivato il sindaco mics. Alleluaiiaaaaaaaaaa suonate campane vicine e lontane"
    elif cardid == "ba6f4630": #matteo
        to_say == "Ciao Matteo, lo sai che ho imparato a dire le cose con i rutti. UUUUAAAAAAAAIIIIIIIIOOOOOOOOMMMMMMMIIIINNNNNNGGGGGGGG . Bravo vero? "
    return to_say


def salutatore(request, cardid=None):
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
        td = (current_greeting.date - last_greeting.date)
        seconds = td.seconds + td.days * (3600*24) 
        to_say += ", sono %d secondi che non ci vediamo, mi sei mancato tanto" % seconds
    elif first_time:
        to_say += first_time

    if random.randrange(0,1) == 0: #0.5 prob
        to_say += ", senti questa, e' fortissima. "
        to_say += random.choice(jokes)
        #to_say += jokes[-1]
        to_say += "aaaah ahhh  ahhh ahhh ahhhr."


    if custom_greeting(cardid):
        to_say = custom_greeting(cardid)

    os.system("cd /var/www/fusolab/media/salutatore; echo \"" + to_say + "\"|/usr/bin/text2wave -eval \"(voice_pc_diphone)\" -o saluto.wav -; lame -b 80 saluto.wav saluto.mp3")
    wrapper = FileWrapper(file( '/var/www/fusolab/media/salutatore/saluto.mp3' ))
    response = HttpResponse(wrapper, content_type='audio/mpeg')
    response['Content-Length'] = os.path.getsize( '/var/www/fusolab/media/salutatore/saluto.mp3' )
    return response
