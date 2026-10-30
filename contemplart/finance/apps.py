from django.apps import AppConfig


class FinanceConfig(AppConfig):
    name = 'contemplart.finance'
    label = 'finance'
    verbose_name = 'Financeiro'

    def ready(self):
        from . import signals  # noqa: F401
