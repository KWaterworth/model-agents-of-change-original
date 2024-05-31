from django.contrib import admin
from django.urls import path, include
from thesisapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
	path('', views.index, name='index'),
    path('', include('thesisapp.urls')),
]
