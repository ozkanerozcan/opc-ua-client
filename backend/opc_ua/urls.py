from django.urls import path
from .views import OPCUAConnectView, OPCUADataView, OPCUARegisterView, OPCUASubscribeView

urlpatterns = [
    path("connection/", OPCUAConnectView.as_view(), name="opcua-connection"),
    path("read-write/", OPCUADataView.as_view(), name="opcua-read-write"),
    path("register/", OPCUARegisterView.as_view(), name="opcua-register"),
    path("subscribe/", OPCUASubscribeView.as_view(), name="opcua-subscribe"),
]