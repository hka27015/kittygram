from datetime import timedelta, time as dt_time
from datetime import date

from django.db.models import Count, Q
from django.utils.timezone import now

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from cats.models import Cat

from .models import DailyCat, CatVote, Prediction
from .serializers import (
    CatVoteSerializer,
    DailyCatSerializer,
    PredictionCreateSerializer,
    PredictionSerializer
)

VOTE_END_TIME = dt_time(23, 59, 59)


def get_today():
    return now().date()

def get_yesterday():
    return get_today() - timedelta(days=1)


def is_voting_closed():
    return now().time() >= VOTE_END_TIME

def update_daily_cat(date):
    leader = (
        CatVote.objects
        .filter(vote_date=date)
        .values('cat')
        .annotate(score=Count('id'))
        .order_by('-score')
        .first()
    )

    if not leader or leader.get("cat") is None:
        # Если голосов нет, удаляем запись за этот день, если она есть
        DailyCat.objects.filter(date=date).delete()
        return None

    cat_id = leader["cat"]
    score = leader["score"]

    obj, created = DailyCat.objects.update_or_create(
        date=date,
        defaults={
            "cat_id": cat_id,
            "score": score,
            "is_finalized": False  # сбрасываем finalized при обновлении
        }
    )

    return obj


def finalize_day(date):
    daily_cat = update_daily_cat(date)

    if daily_cat is None:
        # Если нет победителя, но есть запись - удаляем её
        DailyCat.objects.filter(date=date, is_finalized=False).delete()
        return None

    if daily_cat.is_finalized:
        return daily_cat

    daily_cat.is_finalized = True
    daily_cat.save(update_fields=["is_finalized"])

    winner_id = daily_cat.cat_id

    if winner_id:
        # Сначала сбрасываем все неуспешные прогнозы
        Prediction.objects.filter(date=date).exclude(cat_id=winner_id).update(is_success=False)
        # Потом отмечаем успешные
        Prediction.objects.filter(date=date, cat_id=winner_id).update(is_success=True)

    return daily_cat


def finalize_previous_day():
    yesterday = get_yesterday()

    daily_cat = DailyCat.objects.filter(date=yesterday).first()

    if daily_cat and daily_cat.is_finalized:
        return

    finalize_day(yesterday)


class DailyCatViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = DailyCat.objects.all().order_by('-date')
    serializer_class = DailyCatSerializer

    @action(detail=False, methods=['get'])
    def today(self, request):
        finalize_previous_day()
        today_date = get_today()

        daily_cat = update_daily_cat(today_date)

        if daily_cat is None:
            return Response(
                {"detail": "Сегодня ещё нет голосов", "cat": None, "score": 0},
                status=200
            )

        return Response(DailyCatSerializer(daily_cat).data)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def vote(self, request):
        finalize_previous_day()

        if is_voting_closed():
            finalize_day(get_today())
            return Response({"detail": "Голосование закрыто"}, status=400)

        serializer = CatVoteSerializer(
            data=request.data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)

        serializer.save(
            user=request.user,
            vote_date=get_today()
        )

        update_daily_cat(get_today())

        return Response({"detail": "Голос учтён"}, status=201)

    @action(detail=False, methods=['get'])
    def top_week(self, request):
        finalize_previous_day()
        week_ago = get_today() - timedelta(days=7)

        data = (
            DailyCat.objects
            .filter(
                date__gte=week_ago,
                is_finalized=True
            )
            .order_by('-score')
        )

        return Response(DailyCatSerializer(data, many=True).data)

    @action(detail=False, methods=['get'])
    def history(self, request):
        finalize_previous_day()

        data = (
            DailyCat.objects
            .filter(is_finalized=True)
            .order_by('-date')
        )

        return Response(DailyCatSerializer(data, many=True).data)

    @action(detail=False, methods=['get'])
    def cat_stats(self, request):
        cat_id = request.query_params.get("cat_id")

        if not cat_id:
            return Response(
                {"error": "cat_id required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        wins = DailyCat.objects.filter(
            cat_id=cat_id,
            is_finalized=True
        ).count()

        votes = CatVote.objects.filter(
            cat_id=cat_id
        ).count()

        return Response({
            "cat_id": cat_id,
            "wins": wins,
            "votes": votes
        })

    @action(detail=False, methods=['get'])
    def cat_rating(self, request):
        finalize_previous_day()

        cats = (
            Cat.objects
            .annotate(
                wins_count=Count(
                    'daily_wins',
                    filter=Q(daily_wins__is_finalized=True)
                ),
                votes_count=Count('votes')
            )
            .order_by('-wins_count', '-votes_count')[:10]
        )

        return Response([
            {
                "id": cat.id,
                "name": cat.name,
                "wins": cat.wins_count,
                "votes": cat.votes_count
            }
            for cat in cats
        ])

    @action(detail=False, methods=['get'])
    def user_rating(self, request):
        finalize_previous_day()

        data = (
            Prediction.objects
            .filter(is_success=True)
            .values('user_id', 'user__username')
            .annotate(success_count=Count('id'))
            .order_by('-success_count')[:10]
        )

        return Response(list(data))


class PredictionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post']

    def get_queryset(self):
        return (
            Prediction.objects
            .filter(user=self.request.user)
            .select_related('cat')
            .order_by('-date')
        )

    def get_serializer_class(self):
        if self.action == 'create':
            return PredictionCreateSerializer
        return PredictionSerializer

    def perform_create(self, serializer):
        finalize_previous_day()
        serializer.save(
            user=self.request.user,
            date=get_today()
        )

    @action(detail=False, methods=['get'])
    def stats(self, request):
        finalize_previous_day()

        user = request.user

        total_predictions = Prediction.objects.filter(
            user=user
        ).count()

        successful_predictions = Prediction.objects.filter(
            user=user,
            is_success=True
        ).count()

        failed_predictions = Prediction.objects.filter(
            user=user,
            is_success=False
        ).count()

        pending_predictions = Prediction.objects.filter(
            user=user,
            is_success__isnull=True
        ).count()

        return Response({
            "total_predictions": total_predictions,
            "successful_predictions": successful_predictions,
            "failed_predictions": failed_predictions,
            "pending_predictions": pending_predictions
        })
