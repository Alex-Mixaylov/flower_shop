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
    list_display = ('id', 'user', 'created_at', 'updated_at', 'item_count', 'total_cost')
    list_filter = ('created_at', 'updated_at')  # Фильтрация по дате создания и обновления
    search_fields = ('user__username',)  # Поиск по имени пользователя

    @admin.display(description='Item Count')
    def item_count(self, obj):
        return obj.items.count()

    @admin.display(description='Total Cost')
    def total_cost(self, obj):
        return sum(item.total_price() for item in obj.items.all())

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'product', 'quantity', 'total_price')
    list_filter = ('cart__created_at', 'product__name')  # Фильтрация по дате создания корзины и имени товара
    search_fields = ('product__name', 'cart__user__username')  # Поиск по имени товара и имени пользователя

    @admin.display(description='Total Price')
    def total_price(self, obj):
        return obj.total_price()

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'cart', 'status', 'created_at', 'updated_at_display')  # Добавлено отображение updated_at
    list_filter = ('status', 'created_at', 'updated_at')  # Фильтрация по статусу, created_at и updated_at
    search_fields = ('user__username', 'cart__id')  # Поиск по имени пользователя и ID корзины

    # Метод для отображения updated_at в list_display
    def updated_at_display(self, obj):
        return obj.updated_at
    updated_at_display.short_description = 'Updated At'  # Название колонки в админке


@admin.register(BestSeller)
class BestSellerAdmin(admin.ModelAdmin):
    list_display = ('get_title', 'get_price', 'get_old_price', 'is_featured', 'created_at')

    def get_title(self, obj):
        return obj.product.title
    get_title.short_description = "Название товара"

    def get_price(self, obj):
        return obj.product.price
    get_price.short_description = "Цена"

    def get_old_price(self, obj):
        return obj.product.old_price
    get_old_price.short_description = "Старая цена"

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
    def size_option(self, obj):
        return f"{obj.size_option.size} ({obj.size_option.stems_count} стеблей)" if obj.size_option else "N/A"

    size_option.short_description = "Размер (Количество стеблей)"

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
