from django.conf.urls import patterns, include, url
from hello.views import hello_world
from trades.views import *
from reports.views import *
from accounts.views import *
from brokers.views import *
from django.conf.urls.static import static
from django.conf import settings
from dajaxice.core import dajaxice_autodiscover, dajaxice_config
dajaxice_autodiscover()
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', home),
    # accounts
    url(r'^register/', register),
    url(r'^login/', login),
    url(r'^logout/', logout_view),
    
    # admin
    url(r'^management/', adminView),
    url(r'^addBroker/', addBroker),
    url(r'^modBroker/', modBroker),
    
    # reports
    url(r'^report/', reportView),
    url(r'^monthlyReport/(?P<year>\d{4})/(?P<month>\d{1,2})/$', monthlyReportView),
    url(r'^dailyReport/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$', dailyReportViewAjax),
    #url(r'^dailyReport/(?P<tab>.+)/(?P<strorder>\d{1})/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<strpage>\d+)/$', dailyReportViewAjax),
    #url(r'^dailyReport/(?P<tab>.+)/(?P<strorder>\d{1})/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<strpage>\d+)/$', dailyReportView),
    
    # trades & files
    url(r'^trade/', queryView),
    url(r'^symbol/(?P<symbol>.+)/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<strpage>\d+)/$', symbolView),
    url(r'^document/', documentView),
    url(r'^upload/', upload),
    url(r'^uploadMarks/', uploadMarks),
    
    url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),
    url(r'^admin/', include(admin.site.urls)),
)+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += staticfiles_urlpatterns()
