from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

class HomeView(TemplateView):
    template_name = 'core/index.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            return redirect('/transactions/report/')
        return super().dispatch(request, *args, **kwargs)
