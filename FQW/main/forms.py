from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *
from django.forms import modelformset_factory


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    # specialization = forms.CharField(max_length=255, required=False)
    # description = forms.CharField(widget=forms.Textarea, required=False)

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
        self.fields['package_type'].widget = forms.HiddenInput()

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
            'files',           # Прикрепленные файлы
            'description',     # Описание (обязательно для биржи)
            'price',           # Стоимость (обязательно для биржи)
            'delivery_time',   # Срок выполнения (обязательно для биржи)
            'birzha',          # Биржа (скрытое поле)
        ]
        widgets = {
            'technical_task': forms.Textarea(attrs={'rows': 4}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'price': forms.NumberInput(attrs={'min': 1}),
            'delivery_time': forms.NumberInput(attrs={'min': 1}),
            'birzha': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        birzha = kwargs.pop('birzha', None)  # Получаем флаг, указывающий, что это отклик на биржу
        super().__init__(*args, **kwargs)
        self.fields['files'].required = False  # Файлы необязательны

        # Если это отклик на биржу, делаем поля description, price и delivery_time обязательными
        if birzha:
            self.fields['description'].required = True
            self.fields['price'].required = True
            self.fields['delivery_time'].required = True
        else:
            # Если это отклик на коммишку, делаем поля необязательными
            self.fields['description'].required = False
            self.fields['price'].required = False
            self.fields['delivery_time'].required = False

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['specialization', 'description', 'image', 'skills']
        widgets = {
            'skills': forms.SelectMultiple(),
        }