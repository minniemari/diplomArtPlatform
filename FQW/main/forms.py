from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import *
from django.forms import modelformset_factory
from .widgets import MultipleFileInput


class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label

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


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class BirzhaForm(forms.ModelForm):
    files = forms.FileField(
        widget=MultipleFileInput(),  # ✅ Используем наш виджет
        required=False,
        label="Прикрепить файлы",
        help_text="Можно загрузить до 10 файлов, до 100 МБ"
    )

    class Meta:
        model = Birzha
        fields = ['title', 'description', 'type', 'price', 'increasedPrice', 'files']

class UserResponseForm(forms.ModelForm):
    class Meta:
        model = UserResponse
        fields = [
            'package_type',
            'technical_task',  # Техническое задание
            'files',           # Прикрепленные файлы
            'description',     # Описание (обязательно для биржи)
            'price',           # Стоимость (обязательно для биржи)
            'delivery_time',   # Срок выполнения (обязательно для биржи)
            'birzha',          # Биржа (скрытое поле)
        ]
        widgets = {
            'technical_task': forms.Textarea(attrs={'rows': 4}),
            'description': forms.Textarea(attrs={'rows': 4,'id': 'id_description'}),
            'price': forms.NumberInput(attrs={'min': 1,'id': 'id_price'}),
            'delivery_time': forms.NumberInput(attrs={'min': 1, 'id': 'delivery_time'}),
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
        fields = ['specialization', 'description', 'skills']
        widgets = {
            'skills': forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        print("Skills queryset:", self.fields['skills'].queryset)  # Отладка

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review  # Используем правильную модель
        fields = ['communication_rating', 'result_rating', 'recommend_rating', 'comment']

class CancelOrderForm(forms.Form):
    reason = forms.ChoiceField(choices=[
        ('style', 'Не устраивает стиль'),
        ('tz', 'Не соблюдено ТЗ'),
        ('other', 'Другое'),
    ])
    other_reason = forms.CharField(required=False)

