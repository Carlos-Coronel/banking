from django.http import HttpResponseRedirect
from django.urls import reverse
from rest_framework_simplejwt.tokens import AccessToken

class TokenExpiryMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.path == reverse('accounts:user_logout'):
            token = request.COOKIES.get('access_token')
            if token and self.is_token_expired(token):
                # Redirige al usuario a la vista LogoutView
                return HttpResponseRedirect(reverse('accounts:user_logout'))

        response = self.get_response(request)
        return response

    def is_token_expired(self, token):
        try:
            AccessToken(token)
            return False
        except Exception as e:
            return True
