from django.urls import path
from .views import CompanyView
#CREACION DEL ARCHIVO URL PARA RESPUESTAS GET,POST,DELETE,PUT
#path(ruta raiz, la view, nombre del endpoint)
urlpatterns=[
path('companies/',CompanyView.as_view(),name='companies_list'),
path('companies/<int:id>',CompanyView.as_view(),name='companies_process')
]