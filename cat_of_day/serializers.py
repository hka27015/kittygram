from rest_framework import serializers
from django.utils.timezone import now

from .models import CatVote, DailyCat, Prediction
from cats.models import Cat


class CatShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cat
        fields = ['id', 'name']


class DailyCatSerializer(serializers.ModelSerializer):
    cat = CatShortSerializer()

    class Meta:
        model = DailyCat
        fields = ['date', 'cat', 'score']


class CatVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CatVote
        fields = ['id', 'cat']

    def validate(self, data):
        user = self.context['request'].user
        cat = data['cat']
        today = now().date()

        if cat.owner_id == user.id:
            raise serializers.ValidationError("Нельзя голосовать за своего кота")

        if CatVote.objects.filter(user=user, vote_date=today).exists():
            raise serializers.ValidationError("Вы уже голосовали сегодня")

        return data


class PredictionSerializer(serializers.ModelSerializer):
    cat_name = serializers.CharField(source='cat.name', read_only=True)

    class Meta:
        model = Prediction
        fields = ['id', 'cat', 'cat_name', 'date', 'is_success']


class PredictionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prediction
        fields = ['cat']

    def validate(self, data):
        user = self.context['request'].user
        today = now().date()

        if Prediction.objects.filter(user=user, date=today).exists():
            raise serializers.ValidationError("Уже есть прогноз на сегодня")

        if data['cat'].owner_id == user.id:
            raise serializers.ValidationError("Нельзя выбрать своего кота")

        return data
