from django.contrib import admin
from .models import User, Collection, Bouquet, Order, OrderItem, ContactMessage, BestSeller, TeamMember, Testimonial

# Регистрация моделей в админке
admin.site.register(User)
admin.site.register(Collection)
admin.site.register(Bouquet)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ContactMessage)

@admin.register(BestSeller)
class BestSellerAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'is_featured')
    list_filter = ('is_featured',)
    search_fields = ('title',)

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'role')
    search_fields = ('name', 'role')

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('author',)
    search_fields = ('author',)
