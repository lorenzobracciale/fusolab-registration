from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import user_passes_test
from base.tests import in_turnisti


@user_passes_test(in_turnisti)
def open_gate(request):
    import socket
    from fusolab2_0 import settings
    UDP_IP = settings.IP_OPENER
    UDP_PORT = settings.PORT_OPENER
    MESSAGE = settings.OPEN_GATE_PW
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
    return HttpResponse("Cancello Aperto")


