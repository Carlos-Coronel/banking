from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.views import LoginView
from django.shortcuts import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, RedirectView
from rest_framework_simplejwt.tokens import RefreshToken

from .forms import UserRegistrationForm, UserAddressForm
from core.models import Auditoria
from uuid import getnode as get_mac


User = get_user_model()


class UserRegistrationView(TemplateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'accounts/user_registration.html'

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return HttpResponseRedirect(
                reverse_lazy('transactions:transaction_report')
            )
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        registration_form = UserRegistrationForm(self.request.POST)
        address_form = UserAddressForm(self.request.POST)

        if registration_form.is_valid() and address_form.is_valid():
            user = registration_form.save()
            address = address_form.save(commit=False)
            address.user = user
            address.save()

            login(self.request, user)
            messages.success(
                self.request,
                (
                    'Gracias por crear una cuenta bancaria.'
                    f'Su número de cuenta es {user.account.account_no}. '
                )
            )
            return HttpResponseRedirect(
                reverse_lazy('transactions:deposit_money')
            )

        return self.render_to_response(
            self.get_context_data(
                registration_form=registration_form,
                address_form=address_form
            )
        )

    def get_context_data(self, **kwargs):
        if 'registration_form' not in kwargs:
            kwargs['registration_form'] = UserRegistrationForm()
        if 'address_form' not in kwargs:
            kwargs['address_form'] = UserAddressForm()

        return super().get_context_data(**kwargs)

class UserLoginView(LoginView):
    template_name='accounts/user_login.html'
    redirect_authenticated_user = False

    def form_valid(self, form):
        # Realizar el inicio de sesión
        response = super().form_valid(form)

        if self.request.user.is_authenticated:
            # Obtener la dirección MAC
            mac_int = get_mac()
            dir_mac = ':'.join(("%012X" % mac_int)[i:i + 2] for i in range(0, 12, 2))

            Auditoria.objects.create(
                ip=self.request.META['REMOTE_ADDR'],
                nombre_pc=self.request.META['COMPUTERNAME'],
                usuario=self.request.user,
                evento='login',
                nivel='normal',
                mac=dir_mac
            )

            # Generar tokens de acceso y actualización
            refresh = RefreshToken.for_user(self.request.user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            # Agregar tokens al contexto de la respuesta
            response.set_cookie(key='access_token', value=access_token)
            response.set_cookie(key='refresh_token', value=refresh_token)

        return response


   # def form_valid(self, form):
    #    user = form.get_user()
     #   if not hasattr(user, 'account'):
      #      messages.error(self.request, "Tu cuenta no tiene una cuenta bancaria asociada.")
       #     logout(self.request)
        #    return super().form_invalid(form)

        #return super().form_valid(form)

class LogoutView(RedirectView):
    pattern_name = 'home'

    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.is_authenticated:

            # Obtener el token de actualización de las cookies
            refresh_token = self.request.COOKIES.get('refresh_token')

            if refresh_token:
                # Invalidar el token de actualización
                refresh = RefreshToken(refresh_token)
                refresh.blacklist()

            # Cerrar la sesión del usuario
            logout(self.request)

        return super().get_redirect_url(*args, **kwargs)
