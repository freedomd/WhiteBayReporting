from django.conf.urls import patterns, include, url
from hello.views import hello_world
from trades.views import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', home),
    url(r'^upload/', upload),
    
    url(r'^admin/', include(admin.site.urls)),
)
