from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'text']
        widgets = {
            'rating': forms.RadioSelect(choices=[(i, f'{i} stars') for i in range(1, 6)]),
            'text': forms.Textarea(attrs={'placeholder': 'Write your review here...'}),
        }
