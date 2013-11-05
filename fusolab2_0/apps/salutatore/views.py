from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect, HttpResponseServerError
from django.utils import simplejson
from django.conf import settings
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.core.servers.basehttp import FileWrapper
from django.contrib.auth.decorators import login_required
from django.utils import timesince
import os, mimetypes, urllib
from ingresso.models import Card
from salutatore.models import Greeting, ToBeSaid
from sorl.thumbnail import get_thumbnail
from base.utils import * 

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

@csrf_exempt
@login_required
def sentences_list(request):
    import json
    if request.method == "POST" and request.is_ajax():
        #create new element
        json_data = simplejson.loads(request.raw_post_data)
        try:
            post_txt = json_data['text'] 
        except KeyError:
            HttpResponseServerError("Malformed data!")

        if post_txt:
            if is_polite(post_txt):
                ToBeSaid(sentence=post_txt, user=request.user.get_profile()).save()
            else:
                raise ValidationError('Ti perdono, ma non lo posso scrivere!')

        return HttpResponse(str(request.raw_post_data))
    else:
        qs = ToBeSaid.objects.all().order_by("-created_on")[:5]
        mlist = []
        for q in reversed(qs): 
            im_url = ""
            if q.user.photo:
                im_url = get_thumbnail(q.user.photo , '50x50', crop='center', quality=99).url 
            else:
                im_url = settings.STATIC_URL + "images/fusolab_unnamed_avatar.jpg" 
            mlist.append({"id": q.id, "sender": q.user.user.username, "text": q.sentence, "image": im_url , "date": timesince.timesince(q.created_on)})
        return HttpResponse(json.dumps(mlist), content_type="application/json")
