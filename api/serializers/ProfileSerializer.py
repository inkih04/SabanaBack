from rest_framework import serializers

from api.serializers import UserSerializer
from issues.models import Profile



class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = ['id', 'user', 'biography', 'avatar']