from django import forms
from django.forms import RadioSelect
from .models import Review

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
            'text': forms.Textarea(attrs={'placeholder': 'Write your review here...'}),
        }
