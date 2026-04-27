from rest_framework import serializers
from django.utils.timezone import now
from .models import DailyCat, CatVote


class DailyCatSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyCat
        fields = "__all__"


class CatVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CatVote
        fields = ["id", "cat"]

    def validate(self, data):
        request = self.context["request"]
        user = request.user
        cat = data.get("cat")

        if not user or not user.is_authenticated:
            raise serializers.ValidationError("Нужна авторизация")

        if cat.owner_id == user.id:
            raise serializers.ValidationError("Нельзя голосовать за своего кота")

        today = now().date()

        if CatVote.objects.filter(user=user, vote_date=today).exists():
            raise serializers.ValidationError("Вы уже голосовали сегодня")

        return data

    def create(self, validated_data):
        return CatVote.objects.create(
            user=self.context["request"].user,
            cat=validated_data["cat"],
            vote_date=now().date()
        )
