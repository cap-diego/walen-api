# From django
from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

# From w
from products.constants import MEASURE_UNIT_CHOICES, \
MIN_VALUE_ZERO_ERROR_MSG


class Category(models.Model):
    description = models.CharField(max_length=50, unique=True)
    
    class Meta:
        ordering = ['description']
    def __str__(self):
       return self.description

class Product(models.Model):
    display_name = models.CharField(max_length=100)
    description = models.CharField(max_length=255, blank=True)
    featured_photo_url = models.URLField(blank=True)
    unitary_price = models.FloatField(
        validators=[MinValueValidator(0, MIN_VALUE_ZERO_ERROR_MSG)])
    measure_unit = models.CharField(max_length=3,
        choices=MEASURE_UNIT_CHOICES)
    current_stock = models.PositiveSmallIntegerField()

    category = models.ForeignKey(to=Category, on_delete=models.SET_NULL,
        related_name='products', null=True)

    class Meta:
        ordering = ['id']
        indexes = [
            models.Index(fields=['category'], name='category_idx'),
        ]

    def __str__(self):
        return '{}  [stock: {}]'.format(self.display_name, self.current_stock)
    
    def clean(self):
        if self.unitary_price < 0:
            raise ValidationError(MIN_VALUE_ZERO_ERROR_MSG)
        return super().clean()
    
    def save(self, *args, **kwarsg):
        self.clean()
        return super().save()

class ProductTag(models.Model):
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE, 
        related_name='tags')
    tag = models.CharField(max_length=20)

    def __str__(self):
        return self.tag
    
class ProductPhoto(models.Model):
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE, 
        related_name='photos')
    photo = models.URLField()

    def __str__(self):
        return 'Foto de {}'.format(self.product.display_name)
    
class ProductReview(models.Model):
    author_name = models.CharField(max_length=50)
    commentary = models.TextField()
    
    class Meta:
        ordering = ['-date']
        
    class Rating(models.IntegerChoices):
            BAD = 1
            NOT_GOOD = 2
            GOOD = 3
            EXCELENT = 4
            PERFECT = 5

    rating = models.IntegerField(choices=Rating.choices)

    product = models.ForeignKey(to=Product, on_delete=models.CASCADE,
        related_name='reviews')
    
    date = models.DateField(auto_now=True)
