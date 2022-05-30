from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from advertisements.models import Advertisement, Favorites


class UserSerializer(serializers.ModelSerializer):
    """Serializer для пользователя."""

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name',
                  'last_name',)
        read_only_fields = ['id', 'username', 'first_name',
                            'last_name', ]


class AdvertisementSerializer(serializers.ModelSerializer):
    """Serializer для объявления."""

    creator = UserSerializer(
        read_only=True,
    )

    class Meta:
        model = Advertisement
        fields = ('id', 'title', 'description', 'creator',
                  'status', 'created_at',)

    def create(self, validated_data):
        """Метод для создания"""

        # Простановка значения поля создатель по-умолчанию.
        # Текущий пользователь является создателем объявления
        # изменить или переопределить его через API нельзя.
        # обратите внимание на `context` – он выставляется автоматически
        # через методы ViewSet.
        # само поле при этом объявляется как `read_only=True`
        validated_data["creator"] = self.context["request"].user
        return super().create(validated_data)

    def validate(self, data):
        """Метод для валидации. Вызывается при создании и обновлении."""
        if 'status' in data:
            if data['status'] == 'CLOSED':
                return data
        name_user = self.context["request"].user
        number_users_open_ads = Advertisement.objects.filter(creator=name_user, status='OPEN').count()
        if number_users_open_ads >= 10:
            raise ValidationError('Превышено количество открытых объявлений')
        else:
            return data


class FavoritesSerializer(serializers.ModelSerializer):
    favorites = AdvertisementSerializer(read_only=True)
    # user = UserSerializer(read_only=True)

    class Meta:
        model = Favorites
        fields = ('id', 'user', 'favorites')
