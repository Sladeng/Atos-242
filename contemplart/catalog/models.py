import uuid

from django.db import models


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.nome


class Product(models.Model):
    PHYSICAL = 'physical'
    DIGITAL = 'digital'
    PRODUCT_TYPE_CHOICES = [
        (PHYSICAL, 'Físico'),
        (DIGITAL, 'Digital'),
    ]

    GESSO = 'gesso'
    RESINA = 'resina'
    PLA = 'pla'
    MATERIAL_CHOICES = [
        (GESSO, 'Gesso'),
        (RESINA, 'Resina'),
        (PLA, 'PLA'),
    ]

    # TODO(Fase 1): arquivo_digital (FK DigitalAsset), imagens e
    # ProductVariant do DATA_MODEL.md ainda não foram implementados.
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    descricao = models.TextField(blank=True)
    tipo_produto = models.CharField(max_length=20, choices=PRODUCT_TYPE_CHOICES, default=PHYSICAL)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    preco_atacado = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    categoria = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name='produtos', null=True, blank=True
    )
    material = models.CharField(max_length=20, choices=MATERIAL_CHOICES, null=True, blank=True)
    quantidade_estoque = models.PositiveIntegerField(null=True, blank=True)
    ativo = models.BooleanField(default=True)
    custo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    peso_g = models.DecimalField('peso (g)', max_digits=10, decimal_places=2, null=True, blank=True)
    tempo_impressao = models.DurationField(null=True, blank=True)

    def __str__(self):
        return self.nome
