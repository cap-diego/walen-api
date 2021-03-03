# From django
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

# From w 
from products.models import Product, ProductTag,\
    Category, ProductReview, ProductPhoto, Product


class ProductListStockFilter(admin.SimpleListFilter):
    title = _('Filtros por stock')
    parameter_name = 'curren_stock_filter'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('10', _('10 menos')),
            ('20', _('20 o menos')),
            ('50', _('50 o menos')),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value() in ['10', '20', '50']:
            return queryset.filter(current_stock__lte=self.value())

class ProductAdmin(admin.ModelAdmin):
    search_fields = ('current_stock', 'description', 'display_name')
    list_filter = ('tags', 'category', 'reviews__rating', ProductListStockFilter)
    ordering = ['current_stock']

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        return queryset, use_distinct 

class ProductTagAdmin(admin.ModelAdmin):
    pass

class CategoryAdmin(admin.ModelAdmin):
    pass

class ProductReviewAdmin(admin.ModelAdmin):
    pass

class ProductPhotoAdmin(admin.ModelAdmin):
    pass 


admin.site.register(ProductTag, ProductTagAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(ProductReview, ProductReviewAdmin)
admin.site.register(ProductPhoto, ProductPhotoAdmin)