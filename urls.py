from django.conf.urls import patterns, include, url
import views 

urlpatterns = patterns('',
	url(r'^$', views.IndexView.as_view(), name='index'),
	url(r'^info/$', views.InfoView.as_view(), name='info'),
	url(r'^stop_list/$', views.StopListView.as_view(), name='stop_list')
)
