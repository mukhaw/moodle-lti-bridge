from django.urls import path
from . import views

app_name = 'bridge'

urlpatterns = [
    path('', views.consumer, name='consumer'),
    path('grade', views.grade, name='grade'),
    path('progress', views.progress, name='progress'),
    path('provider', views.provider),
    path('graph', views.graph, name='graph'),
    path('test_tree',views.test_html,name = 'test_html'),
    path('home_vis',views.home_vis,name = 'home_vis'),
    path('sunburst',views.sunburst,name ="sunburst")
]
