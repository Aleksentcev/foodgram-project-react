from django.urls import include, path
from rest_framework import routers

app_name = 'api'

router = routers.DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
]
