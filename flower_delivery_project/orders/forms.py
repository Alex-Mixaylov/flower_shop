from django import forms
from django.forms import RadioSelect
from .models import Review, Delivery, Order

# Кастомный виджет
class StarsRadioSelect(RadioSelect):
    template_name = 'orders/widgets/radio_star.html'

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'text']
        widgets = {
            'rating': StarsRadioSelect(
                choices=[
                    (5, '5 stars'),
                    (4, '4 stars'),
                    (3, '3 stars'),
                    (2, '2 stars'),
                    (1, '1 star'),
                ]
            ),
            'text': forms.Textarea(attrs={'class': 'form-control ted', 'placeholder': 'Write your review here...'}),
        }

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer_name', 'customer_email', 'customer_phone']
        widgets = {
            'customer_name': forms.TextInput(attrs={'id': 'customer_name', 'class': 'form-control'}),
            'customer_email': forms.EmailInput(attrs={'id': 'customer_email', 'class': 'form-control'}),
            'customer_phone': forms.TextInput(attrs={'id': 'customer_phone', 'class': 'form-control'}),
        }

class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = ['full_name', 'country', 'state', 'city', 'zipcode', 'address', 'phone']
        widgets = {
            'full_name': forms.TextInput(attrs={'id': 'full_name', 'class': 'form-control'}),
            'country': forms.TextInput(attrs={'id': 'country', 'class': 'form-control'}),
            'state': forms.TextInput(attrs={'id': 'state', 'class': 'form-control'}),
            'city': forms.TextInput(attrs={'id': 'city', 'class': 'form-control'}),
            'zipcode': forms.TextInput(attrs={'id': 'zipcode', 'class': 'form-control'}),
            'address': forms.Textarea(attrs={'id': 'address', 'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'id': 'phone', 'class': 'form-control'}),
        }