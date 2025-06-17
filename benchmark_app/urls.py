from django.urls import path
from . import views

app_name = 'benchmark'

urlpatterns = [
    path('', views.BenchmarkView.as_view(), name='dashboard'),
    path('api/run-benchmark/', views.run_benchmark, name='run_benchmark'),
]