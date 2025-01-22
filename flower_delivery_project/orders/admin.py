from django.contrib import admin
from .models import (
    CustomUser,
    Collection,
    Order,
    OrderItem,
    Delivery,
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
    FlowerType,
    FlowerColor,
)
from django.utils.html import format_html

# Регистрация моделей в админке
admin.site.register(CustomUser)
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

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('get_order_id', 'get_user', 'get_status', 'get_created_at', 'product', 'quantity', 'item_price')
    search_fields = ('order__id', 'order__user__username', 'order__status')
    list_filter = ('order__id', 'order__status', 'order__created_at')
    list_select_related = ('order', 'product')  # Оптимизация запросов

    def get_order_id(self, obj):
        return obj.order.id
    get_order_id.short_description = 'Номер заказа'
    get_order_id.admin_order_field = 'order__id'

    def get_user(self, obj):
        return obj.order.user.username
    get_user.short_description = 'Пользователь'
    get_user.admin_order_field = 'order__user__username'

    def get_status(self, obj):
        return obj.order.status
    get_status.short_description = 'Статус заказа'
    get_status.admin_order_field = 'order__status'

    def get_created_at(self, obj):
        return obj.order.created_at
    get_created_at.short_description = 'Дата создания заказа'
    get_created_at.admin_order_field = 'order__created_at'

@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('order', 'full_name', 'country', 'state', 'city', 'zipcode', 'address')
    search_fields = ('full_name', 'country', 'state', 'city', 'zipcode')
    list_filter = ('country', 'state', 'city')

@admin.register(BestSeller)
class BestSellerAdmin(admin.ModelAdmin):
    list_display = ('get_name', 'get_price', 'get_old_price', 'is_featured', 'created_at')

    def get_name(self, obj):
        return obj.product.name
    get_name.short_description = "Название товара"

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

# Регистрация модели FlowerType
@admin.register(FlowerType)
class FlowerTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# Регистрация модели FlowerColor
@admin.register(FlowerColor)
class FlowerColorAdmin(admin.ModelAdmin):
    list_display = ('name', 'color_code')
    search_fields = ('name',)
    readonly_fields = ('color_reference',)

    # Метод для отображения справочного списка HEX-кодов
    def color_reference(self, obj):
        return format_html(
            """
            <table style="border-collapse: collapse; width: 100%; margin-top: 10px;">
                <tr>
                    <th style="border: 1px solid #ddd; padding: 8px;">Цвет</th>
                    <th style="border: 1px solid #ddd; padding: 8px;">HEX-код</th>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px;">Красный</td>
                    <td style="border: 1px solid #ddd; padding: 8px;">#FF0000</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px;">Белый</td>
                    <td style="border: 1px solid #ddd; padding: 8px;">#FFFFFF</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px;">Желтый</td>
                    <td style="border: 1px solid #ddd; padding: 8px;">#FFFF00</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px;">Черный</td>
                    <td style="border: 1px solid #ddd; padding: 8px;">#000000</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px;">Салатовый</td>
                    <td style="border: 1px solid #ddd; padding: 8px;">#32CD32</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px;">Оранжевый</td>
                    <td style="border: 1px solid #ddd; padding: 8px;">#FFA500</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px;">Фиолетовый</td>
                    <td style="border: 1px solid #ddd; padding: 8px;">#800080</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px;">Синий</td>
                    <td style="border: 1px solid #ddd; padding: 8px;">#0000FF</td>
                </tr>
            </table>
            """
        )

    color_reference.short_description = "Справочник HEX-кодов цветов"

# Регистрация модели Product
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category', 'rating', 'is_featured', 'created_at')
    list_filter = ('category', 'flower_types', 'flower_colors', 'is_featured', 'rating')  # Добавлены flower_types и flower_colors
    search_fields = ('name', 'description', 'category__name')
    list_editable = ('is_featured',)
    ordering = ('-created_at',)
    inlines = [SizeOptionInline, RelatedProductInline, ComboOfferInline]

    # Пользовательский метод для отображения размера и количества стеблей
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
