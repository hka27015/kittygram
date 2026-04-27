from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from django.utils.timezone import now
from django.db.models import Count
from datetime import timedelta

from cats.models import Cat
from .models import DailyCat, CatVote
from .serializers import CatVoteSerializer, DailyCatSerializer


class DailyCatViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DailyCat.objects.all().order_by('-date')
    serializer_class = DailyCatSerializer


    @action(detail=False, methods=['get'])
    def today(self, request):
        today = now().date()

        daily = DailyCat.objects.filter(date=today).first()

        if not daily or not daily.cat:
            return Response({
                "detail": "Кот дня ещё не выбран"
            }, status=200)

        return Response(DailyCatSerializer(daily).data)


    @action(detail=False, methods=['post'])
    def vote(self, request):
        serializer = CatVoteSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        vote = serializer.save()

        today = now().date()

        top = (
            CatVote.objects
            .filter(vote_date=today)
            .values('cat')
            .annotate(score=Count('id'))
            .order_by('-score')
            .first()
        )

        if not top:
            return Response({"detail": "Голос учтён"}, status=201)

        cat_id = top['cat']
        score = top['score']

        cat = Cat.objects.filter(id=cat_id).first()
        if not cat:
            return Response({"detail": "Кот не найден"}, status=201)

        daily, _ = DailyCat.objects.get_or_create(date=today)

        daily.cat = cat
        daily.score = score
        daily.save()

        return Response({"detail": "Голос учтён"}, status=201)


    @action(detail=False, methods=['get'])
    def top_week(self, request):
        week_ago = now().date() - timedelta(days=7)

        data = (
            DailyCat.objects
            .filter(date__gte=week_ago, cat__isnull=False)
            .order_by('-score')
        )

        return Response(DailyCatSerializer(data, many=True).data)


    @action(detail=False, methods=['get'])
    def history(self, request):
        data = DailyCat.objects.all().order_by('-date')

        return Response(DailyCatSerializer(data, many=True).data)
    
    @action(detail=False, methods=['get'])
    def cat_stats(self, request):
        cat_id = request.query_params.get("cat_id")

        if not cat_id:
            return Response({"error": "cat_id required"}, status=400)

        votes = CatVote.objects.filter(cat_id=cat_id).count()

        return Response({
            "cat_id": cat_id,
            "votes": votes
        })
