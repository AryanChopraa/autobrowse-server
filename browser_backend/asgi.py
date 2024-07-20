import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import automations.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'browser_backend.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            automations.routing.websocket_urlpatterns
        )
    ),
})


