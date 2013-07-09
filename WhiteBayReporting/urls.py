from django.conf.urls import patterns, include, url
from hello.views import hello_world
from trades.views import *
from reports.views import *
from accounts.views import *
from admins.views import *
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
    url(r'^settings/changePassword/', changePasswordView),
    url(r'^settings/', settingView),
    
    
    # admin
    url(r'^firmProfile/', firmView),
    url(r'^traderProfile/', traderView),
    url(r'^systemProfile/', systemView),
    url(r'^routeDetail/', routeView),
    url(r'^employerProfile/', employerView),
    url(r'^futureFeeRateProfile/', futureFeeRateView),
    url(r'^futureFeeGroupProfile/', futureFeeGroupView),
    url(r'^accountProfile/', accountView),
    url(r'^groupProfile/', groupView),
    url(r'^log/', logView),
    url(r'^addBroker/', addBroker),
    url(r'^modBroker/', modBroker),
    url(r'^addTrader/', addTrader),
    url(r'^modTrader/', modTrader),
    url(r'^addSystem/', addSystem),
    url(r'^modSystem/', modSystem),
    url(r'^modFirm/', modFirm),
    url(r'^addEmployer/', addEmployer),
    url(r'^modEmployer/', modEmployer),
    url(r'^addFuture/', addFuture),
    url(r'^modFuture/', modFuture),
    url(r'^addAccount/', addAccount),
    url(r'^modAccount/', modAccount),
    url(r'^modFeeGroup/', modFeeGroup),
    url(r'^addGroup/', addGroup),
    url(r'^modGroup/', modGroup),
    
    # firm
    url(r'^firmReport/', firmReportView),
    
    # reports
    url(r'^report/(?P<account>.+)/', reportView),
    url(r'^reportQuery/', reportQueryView),
    url(r'^monthlyReport/(?P<account>.+)/(?P<year>\d{4})/(?P<month>\d{1,2})/$', monthlyReportView),
    url(r'^dailyReport/(?P<account>.+)/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$', dailyReportViewAjax),
    #url(r'^dailyReport/(?P<tab>.+)/(?P<strorder>\d{1})/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<strpage>\d+)/$', dailyReportViewAjax),
    #url(r'^dailyReport/(?P<tab>.+)/(?P<strorder>\d{1})/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<strpage>\d+)/$', dailyReportView),
    
    # trades & files
    url(r'^tradeQuery/', tradeQueryView),
    url(r'^symbol/(?P<account>.+)/(?P<symbol>.+)/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$', symbolViewAjax),
    url(r'^document/', documentView),
    url(r'^upload/', upload),
    url(r'^uploadMarks/', uploadMarks),
    
    url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),
    url(r'^admin/', include(admin.site.urls)),
)+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += staticfiles_urlpatterns()
