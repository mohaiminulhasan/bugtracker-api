from datetime import datetime
from django.shortcuts import render
from rest_framework.response import Response

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

# Create your views here.
class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        now = datetime.now()
        then = datetime(1970, 1, 1)
        auth_validity_time = 60 * 60 # in seconds
        time_in_seconds = round((now-then).total_seconds() + auth_validity_time)

        return Response({
            'message': 'Login success!',
            'token': token.key,
            'expiresAt': time_in_seconds,
            'userInfo': {
                'id': user.pk,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            },
        })
