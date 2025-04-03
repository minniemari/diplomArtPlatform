from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    specialization = forms.CharField(max_length=255, required=False)
    description = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class CommissionForm(forms.ModelForm):
    # Поля для Commission
    title = forms.CharField(label="Название")
    type = forms.ModelChoiceField(queryset=Type.objects.all(), label="Тип")
    description = forms.CharField(widget=forms.Textarea, label="Описание")
    needsForOrder = forms.CharField(widget=forms.Textarea, label="От покупателя нужно")
    image = forms.ImageField(required=False, label="Обложка коммишена", widget=forms.ClearableFileInput(attrs={'accept': 'image/*'}))

    # Поля для Option (пакеты)
    package_type = forms.ChoiceField(choices=Option.PACKAGE_CHOICES, widget=forms.RadioSelect, label="Тип пакета")
    is_sketch = forms.BooleanField(required=False, label="Скетч")
    for_print = forms.BooleanField(required=False, label="Для печати")
    difficult_bg = forms.BooleanField(required=False, label="Проработка окружающего")
    full_height = forms.BooleanField(required=False, label="Персонаж в полный рост")
    details = forms.BooleanField(required=False, label="Проработка деталей")
    vector = forms.BooleanField(required=False, label="Исходник в векторе")
    psd = forms.BooleanField(required=False, label="Исходник в PSD")
    amount = forms.IntegerField(label="Количество объектов")
    deadline = forms.IntegerField(label="Срок выполнения (дней)")
    price = forms.DecimalField(label="Цена")

    # Поля для BonusOption (дополнительные опции)
    additional_option_name = forms.CharField(required=False, label="Название дополнительной опции")
    additional_option_price = forms.DecimalField(required=False, label="Цена дополнительной опции")
    additional_option_deadline = forms.IntegerField(required=False, label="Срок выполнения дополнительной опции")
    additional_option_description = forms.CharField(required=False, widget=forms.Textarea, label="Описание дополнительной опции")

    class Meta:
        model = Commission
        fields = ['title', 'type', 'description', 'needsForOrder', 'image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.option_fields = [
            'is_sketch', 'for_print', 'difficult_bg', 'full_height', 'details', 'vector', 'psd',
            'amount', 'deadline', 'price'
        ]

    def save(self, commit=True):
        commission = super().save(commit=False)
        commission.user = self._user  # Установка пользователя при создании
        if commit:
            commission.save()

        # Сохранение пакета
        option_data = {
            field: self.cleaned_data[field] for field in self.option_fields
        }
        option = Option.objects.create(commission=commission, **option_data)

        # Сохранение дополнительных опций
        if self.cleaned_data['additional_option_name']:
            bonus_option = BonusOption.objects.create(
                name=self.cleaned_data['additional_option_name'],
                price=self.cleaned_data['additional_option_price'],
                deadline=self.cleaned_data['additional_option_deadline'],
                description=self.cleaned_data['additional_option_description']
            )
            commission.bonus_options.add(bonus_option)

        return commission

    def set_user(self, user):
        self._user = user


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