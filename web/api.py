from rest_framework import viewsets
from rest_framework import permissions
from web.models import Statue, Score
from web.serializers import StatueSerializer, ScoreSerializer
from rest_framework.decorators import action
from rest_framework.response import Response

class StatueViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Statue.objects.all().order_by('name')
    serializer_class = StatueSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = []
    http_method_names = ['post', 'patch','get']
    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def add_score(self, request, pk=None):
        obj = self.get_object()
        obj.add_score(request.data, request.user)
        return Response("OK")


class ScoreViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Score.objects.all()
    serializer_class = ScoreSerializer
    permission_classes = [permissions.IsAuthenticated]
