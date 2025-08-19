from django.urls import path
from . import views

urlpatterns = [
    path("process-documentation", views.process_documentation, name="process_documentation"),
    path("processing-status/<str:chat_id>", views.processing_status, name="processing_status"),
    path("chat/<str:chat_id>", views.chat_view, name="chat_view"),
    path("chat-history/<str:chat_id>", views.chat_history, name="chat_history"),
    path("prueba-de-formulario/", views.prueba_de_formulario, name="prueba_formulario"),
]