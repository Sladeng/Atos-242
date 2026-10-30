from django.apps import AppConfig
from django.db.models.signals import post_migrate

# Perfil de quem opera a loja pelo painel, sem acesso ao financeiro nem a
# usuários/configurações. Recriado (idempotente) a cada `migrate`.
GRUPO_OPERADOR = 'Operador'
PERMISSOES_OPERADOR = [
    ('wagtailadmin', 'access_admin'),
    ('catalog', 'view_product'), ('catalog', 'add_product'), ('catalog', 'change_product'),
    ('catalog', 'view_category'), ('catalog', 'add_category'), ('catalog', 'change_category'),
    ('accounts', 'view_customer'), ('accounts', 'add_customer'), ('accounts', 'change_customer'),
    ('crm', 'view_interaction'), ('crm', 'add_interaction'), ('crm', 'change_interaction'),
    ('orders', 'view_order'), ('orders', 'add_order'), ('orders', 'change_order'),
    ('orders', 'view_orderitem'), ('orders', 'add_orderitem'), ('orders', 'change_orderitem'),
    ('orders', 'delete_orderitem'),
]


def criar_grupo_operador(sender, **kwargs):
    from django.apps import apps
    from django.contrib.auth.models import Group, Permission

    # post_migrate dispara uma vez por app; só depois do último todas as
    # permissões já existem.
    if sender is not list(apps.get_app_configs())[-1]:
        return

    grupo, _ = Group.objects.get_or_create(name=GRUPO_OPERADOR)
    for app_label, codename in PERMISSOES_OPERADOR:
        permissao = Permission.objects.filter(content_type__app_label=app_label, codename=codename).first()
        if permissao:
            grupo.permissions.add(permissao)


class CmsConfig(AppConfig):
    name = 'contemplart.cms'
    label = 'cms'
    verbose_name = 'Conteúdo'

    def ready(self):
        post_migrate.connect(criar_grupo_operador)
