import uuid

from django.db import models
from django.utils.text import slugify


def slug_unico(model, texto, excluir_id=None):
    """Slug a partir de `texto`, com sufixo -2, -3... se já estiver em uso."""
    base = slugify(texto)[:240] or 'item'
    slug, n = base, 2
    while model.objects.filter(slug=slug).exclude(id=excluir_id).exists():
        slug, n = f'{base}-{n}', n + 1
    return slug


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True, help_text='Gerado a partir do nome se ficar vazio.')

    class Meta:
        verbose_name = 'categoria'
        verbose_name_plural = 'categorias'
        ordering = ['nome']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slug_unico(Category, self.nome, self.id)
        super().save(*args, **kwargs)

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
    slug = models.SlugField(max_length=255, unique=True, blank=True, help_text='Gerado a partir do nome se ficar vazio.')
    descricao = models.TextField('descrição', blank=True)
    tipo_produto = models.CharField('tipo', max_length=20, choices=PRODUCT_TYPE_CHOICES, default=PHYSICAL)
    preco = models.DecimalField('preço varejo', max_digits=10, decimal_places=2)
    preco_atacado = models.DecimalField(
        'preço atacado', max_digits=10, decimal_places=2, null=True, blank=True,
        help_text='Deixe vazio para clientes de atacado pagarem o preço de varejo.',
    )
    categoria = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name='produtos', null=True, blank=True
    )
    material = models.CharField(max_length=20, choices=MATERIAL_CHOICES, null=True, blank=True)
    quantidade_estoque = models.PositiveIntegerField('estoque', null=True, blank=True)
    ativo = models.BooleanField(default=True, help_text='Desmarque para esconder o produto da loja.')
    custo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    peso_g = models.DecimalField('peso (g)', max_digits=10, decimal_places=2, null=True, blank=True)
    tempo_impressao = models.DurationField(
        'tempo de impressão', null=True, blank=True, help_text='Formato HH:MM:SS.'
    )

    class Meta:
        verbose_name = 'produto'
        verbose_name_plural = 'produtos'
        ordering = ['nome']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slug_unico(Product, self.nome, self.id)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome
