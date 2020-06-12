from rest_framework import serializers
from ..models import Reference


class ReferenceSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    
    class Meta:
        model = Reference
        fields = ['id', 'title', 'slug', 'description', 'link', 'author']
