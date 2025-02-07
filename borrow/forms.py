from django import forms
from .models import Borrow, BorrowRequest

class BorrowForm(forms.ModelForm):
    class Meta:
        model = Borrow
        fields = ['book']




class BorrowRequestForm(forms.ModelForm):
    class Meta:
        model = BorrowRequest
        fields = ['book']
