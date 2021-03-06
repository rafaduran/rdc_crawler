from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'rdc_crawler.views.home', name='home'),
    # url(r'^rdc_crawler/', include('rdc_crawler.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^index', 'rdc_crawler.crawler.views.index', name='index'),
    url(r'^search','rdc_crawler.crawler.views.search', name='search')
)
