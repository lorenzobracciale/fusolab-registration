from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect, HttpResponseServerError
from django.utils import simplejson
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from django.core.servers.basehttp import FileWrapper
from django.contrib.auth.decorators import login_required
from django.utils import timesince
import os, mimetypes, urllib
from baraled.models import LedString 
from sorl.thumbnail import get_thumbnail
from base.utils import *

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
            # protocollo:
            # http://www.areasx.com/files/articoli/8195/Protocollo%20MEDIA-LINK%201.1.pdf
            if is_polite(post_txt):
                LedString(sentence=post_txt, coded_sentence="<ID00><FD>" + post_txt, user=request.user.get_profile()).save()
            else:
                raise ValidationError('Ti perdono, ma non lo posso scrivere!')

        return HttpResponse(str(request.raw_post_data))
    else:
        qs = LedString.objects.all().order_by("-created_on")[:5]
        mlist = []
        for q in reversed(qs): 
            im_url = ""
            if q.user.photo:
                im_url = get_thumbnail(q.user.photo , '50x50', crop='center', quality=99).url 
            else:
                im_url = settings.STATIC_URL + "images/fusolab_unnamed_avatar.jpg" 
            mlist.append({"id": q.id, "sender": q.user.user.username, "text": q.sentence, "image": im_url , "date": timesince.timesince(q.created_on)})
        return HttpResponse(json.dumps(mlist), content_type="application/json")
