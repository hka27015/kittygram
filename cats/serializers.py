import datetime as dt
from rest_framework import serializers
from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer as DjoserUserSerializer

from .models import Cat, Achievement, AchievementCat, CHOICES

User = get_user_model()

class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = ('id', 'name')

class CatSerializer(serializers.ModelSerializer):
    achievements = AchievementSerializer(many=True, required=False)
    age = serializers.SerializerMethodField()
    color = serializers.ChoiceField(choices=CHOICES)
    owner = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Cat
        fields = (
            'id', 'name', 'color', 'birth_year', 'achievements', 'age', "owner"
        )

    def get_age(self, obj):
        return dt.datetime.now().year - obj.birth_year

    def validate_birth_year(self, value):
        year = dt.datetime.now().year
        if not (year - 40 < value <= year):
            raise serializers.ValidationError('Проверьте год рождения!')
        return value

    def validate(self, data):
        if data.get('color') == data.get('name'):
            raise serializers.ValidationError('Имя не может совпадать с цветом!')
        return data

    def create(self, validated_data):
        if 'achievements' not in self.initial_data:
            cat = Cat.objects.create(**validated_data)
            return cat

        achievements = validated_data.pop('achievements')
        cat = Cat.objects.create(**validated_data)

        for achievement in achievements:
            current_achievement, status = Achievement.objects.get_or_create(
                **achievement
            )
            AchievementCat.objects.create(
                achievement=current_achievement, cat=cat
            )

        return cat

class UserSerializer(DjoserUserSerializer):
    cats = serializers.StringRelatedField(many=True, read_only=True)

    class Meta(DjoserUserSerializer.Meta):
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'cats')