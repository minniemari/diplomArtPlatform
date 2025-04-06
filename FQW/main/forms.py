from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *
from django.forms import modelformset_factory


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    specialization = forms.CharField(max_length=255, required=False)
    description = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class CommissionForm(forms.ModelForm):
    class Meta:
        model = Commission
        fields = ['title', 'type', 'description', 'needsForOrder', 'image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['type'].queryset = Type.objects.all()

class OptionForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = [
            'package_type',
            'description',
            'is_sketch',
            'for_print',
            'difficult_bg',
            'full_height',
            'details',
            'vector',
            'psd',
            'amount',
            'deadline',
            'price',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Скрываем поле commission
        # self.fields['commission'].widget = forms.HiddenInput()

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('description'):
            raise forms.ValidationError("Описание обязательно.")
        if not cleaned_data.get('amount') or cleaned_data['amount'] <= 0:
            raise forms.ValidationError("Количество объектов должно быть больше 0.")
        if not cleaned_data.get('deadline') or cleaned_data['deadline'] <= 0:
            raise forms.ValidationError("Срок выполнения должен быть больше 0.")
        if not cleaned_data.get('price') or cleaned_data['price'] <= 0:
            raise forms.ValidationError("Цена должна быть больше 0.")
        return cleaned_data

class BonusOptionForm(forms.ModelForm):
    class Meta:
        model = BonusOption
        fields = ['name', 'price', 'description', 'deadline']

BonusOptionFormSet = modelformset_factory(
    BonusOption,
    form=BonusOptionForm,
    extra=1,
    can_delete=True
)

class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ['image', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].required = False

class BirzhaForm(forms.ModelForm):
    class Meta:
        model = Birzha
        fields = ['title', 'description', 'file', 'type', 'price', 'increasedPrice']

class UserResponseForm(forms.ModelForm):
    class Meta:
        model = UserResponse
        fields = [
            'technical_task',  # Техническое задание
            'files',
            'delivery_time',
        ]
        widgets = {
            'technical_task': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Опишите ваше техническое задание'}),
            'delivery_time': forms.DateInput(attrs={'type': 'date'}),
        }