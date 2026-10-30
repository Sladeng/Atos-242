"""
URL configuration for contemplart project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve
from wagtail.admin import urls as wagtailadmin_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    # Painel de gestão (Wagtail) para quem não é dev: produtos, clientes, pedidos.
    path('painel/', include(wagtailadmin_urls)),
    # Uploads servidos pelo próprio Django, também em produção (volume do
    # Railway; o whitenoise só serve arquivos estáticos). Suficiente para o
    # volume da v1 — se o tráfego crescer, migrar para S3/R2.
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
