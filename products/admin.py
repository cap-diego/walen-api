# From django
from django.contrib import admin

# From w 
from products.models import Product, ProductTag, Category


class ProductAdmin(admin.ModelAdmin):
    pass

class ProductTagAdmin(admin.ModelAdmin):
    pass

class CategoryAdmin(admin.ModelAdmin):
    pass

admin.site.register(ProductTag, ProductTagAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
