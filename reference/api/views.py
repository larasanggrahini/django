from rest_framework import generics, mixins, permissions
from ..models import Reference
from .serializers import ReferenceSerializer
from .permissions import IsAuthorOrReadOnly
from django.utils.text import slugify

class ReferenceListView(generics.ListCreateAPIView):
    queryset = Reference.getReference.all()
    serializer_class = ReferenceSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        if serializer.is_valid():
            serializer.save(author = self.request.user, slug=slugify(serializer.validated_data['title'], allow_unicode=True))

class ReferenceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Reference.getReference.all()
    serializer_class = ReferenceSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def perform_update(self, serializer):
        if serializer.is_valid():
            serializer.save(slug=slugify(serializer.validated_data['title'], allow_unicode=True))