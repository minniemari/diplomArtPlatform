from rest_framework import serializers
from .models import *
from rest_framework import serializers
from .models import Commission, Option

class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = '__all__'

class CommissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commission
        fields = '__all__'

    def create(self, validated_data):
        request_user = self.context['request'].user  # Получаем пользователя из запроса
        validated_data['user'] = request_user  # Добавляем его в данные

        # Извлекаем связанные данные
        options_data = validated_data.pop('options', [])
        bonus_options_data = validated_data.pop('bonus_options', [])
        # Создаем объект Commission
        commission = Commission.objects.create(**validated_data)

        if not options_data:
            raise serializers.ValidationError({"options": "Нужно выбрать хотя бы одну опцию."})
        # Устанавливаем связи с options и bonus_options
        if options_data:
            commission.options.set(options_data)
        if bonus_options_data:
            commission.bonus_options.set(bonus_options_data)

        return commission