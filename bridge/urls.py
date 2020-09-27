from django.urls import path
from . import views

app_name = 'bridge'

urlpatterns = [
    path('', views.consumer, name='consumer'),
    path('grade', views.grade, name='grade'),
    path('progress', views.progress, name='progress'),
    path('provider', views.provider)
]