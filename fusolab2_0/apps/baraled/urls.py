from django.conf.urls.defaults import *

urlpatterns = patterns('',
        url(r'sentences_list/$', 'baraled.views.sentences_list', name="baraled_sentences_list"),
)


