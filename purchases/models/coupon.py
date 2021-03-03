
# From django 
from django.db import models
from django.core.validators import MinValueValidator, \
    MaxValueValidator

# Utils 
import string, random


class Coupon(models.Model):
    
    id = models.CharField(primary_key=True,
            max_length=6,
            verbose_name='Coupon id')
    
    discount_percent = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0, 'error, el porcentaje no puede ser inferior a 0'), \
            MaxValueValidator(99, 'error, el porcentaje no puede superar 99')]
    )

    valid_until = models.DateField()

    def __str__(self):
        return 'Cupon de {} de descuento'.format(self.discount_percent)

    def save(self, *args, **kwargs):
        if not self.id:
            while (True):
                new_id = generate_random(6)
                if not Coupon.objects.filter(id=new_id).exists():
                    break
            self.id = new_id
        self.id = self.id.upper()
        super().save(*args, **kwargs)
        

    class Meta:
        ordering = ['-valid_until']


def generate_random(n):
    return ''.join(random.sample(string.ascii_uppercase, n))