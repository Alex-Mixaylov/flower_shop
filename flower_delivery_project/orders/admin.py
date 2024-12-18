from django.contrib import admin
from .models import (
    User,
    Collection,
    Bouquet,
    Order,
    OrderItem,
    ContactMessage,
    BestSeller,
    TeamMember,
    Testimonial,
    Category,
    Product,
    Review,
    SizeOption,
    RelatedProduct,
    ComboOffer,
    Slide,
    Cart,
    CartItem,
)

# Регистрация моделей в админке
admin.site.register(User)
admin.site.register(Bouquet)
admin.site.register(OrderItem)
admin.site.register(ContactMessage)

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session_id', 'created_at', 'updated_at')
    search_fields = ('user__username', 'session_id')
    list_filter = ('created_at',)

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'product', 'quantity')
    search_fields = ('cart__id', 'product__name')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_price', 'created_at')
    search_fields = ('user__username', 'customer_name', 'customer_email')
    list_filter = ('status', 'created_at')
@admin.register(BestSeller)
class BestSellerAdmin(admin.ModelAdmin):
    # Отображение в списке
    list_display = ('title', 'price', 'old_price', 'tag', 'is_featured', 'created_at')
    # Фильтры для быстрого поиска
    list_filter = ('is_featured', 'tag', 'created_at')
    # Поля для поиска
    search_fields = ('title', 'description', 'tag')
    # Поля, которые можно редактировать прямо в списке
    list_editable = ('is_featured',)
    # Группировка в админке
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'image')
        }),
        ('Цены и метки', {
            'fields': ('price', 'old_price', 'tag', 'is_featured')
        }),
        ('Дополнительные данные', {
            'fields': ('created_at',),
        }),
    )
    # Поля, которые нельзя редактировать
    readonly_fields = ('created_at',)

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'role')
    search_fields = ('name', 'role')

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('author',)
    search_fields = ('author',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

class SizeOptionInline(admin.TabularInline):
    model = SizeOption
    extra = 1

class RelatedProductInline(admin.TabularInline):
    model = RelatedProduct
    fk_name = 'product'
    extra = 1

class ComboOfferInline(admin.TabularInline):
    model = ComboOffer
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category', 'rating', 'is_featured', 'created_at')  # Добавили rating и created_at
    list_filter = ('category', 'is_featured', 'rating')  # Добавили rating
    search_fields = ('name', 'category__name')
    list_editable = ('is_featured',)  # Позволяет редактировать is_featured прямо из списка
    ordering = ('-created_at',)  # Последние добавленные товары сверху
    inlines = [SizeOptionInline, RelatedProductInline, ComboOfferInline]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'author', 'rating', 'created_at')
    list_filter = ('product', 'rating')
    search_fields = ('author', 'product__name')

@admin.register(SizeOption)
class SizeOptionAdmin(admin.ModelAdmin):
    list_display = ('product', 'size', 'stems_count')
    list_filter = ('product',)
    search_fields = ('product__name', 'size')

@admin.register(RelatedProduct)
class RelatedProductAdmin(admin.ModelAdmin):
    list_display = ('product', 'related_product')
    list_filter = ('product',)
    search_fields = ('product__name', 'related_product__name')

@admin.register(ComboOffer)
class ComboOfferAdmin(admin.ModelAdmin):
    list_display = ('product', 'name', 'price')
    list_filter = ('product',)
    search_fields = ('product__name', 'name')

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Slide)
class SlideAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'created_at')
    list_editable = ('order',)
    readonly_fields = ('created_at',)
    search_fields = ('title',)
