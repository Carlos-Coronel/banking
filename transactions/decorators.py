from django.urls import reverse
from django.shortcuts import redirect

def user_has_bank_account(view_func):
    def _wrapped_view(request, *args, **kwargs):
        user = request.user

        if not hasattr(user, 'account'):
            #return HttpResponseForbidden("No tienes una cuenta bancaria para acceder a esta página.")
            admin_login_url = reverse('admin:login')
            return redirect(admin_login_url)

        return view_func(request, *args, **kwargs)

    return _wrapped_view
