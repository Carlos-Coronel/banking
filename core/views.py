from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Auditoria
from .serializers import AuditoriaSerializer
from uuid import getnode as get_mac

class HomeView(TemplateView):
    template_name = 'core/index.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            return redirect('/transactions/report/')
        return super().dispatch(request, *args, **kwargs)




@api_view(['POST'])
def record_auditoria_api(request, evento, nivel):
    mac_int = get_mac()
    dir_mac = ':'.join(("%012X" % mac_int)[i:i + 2] for i in range(0, 12, 2))
    origin = request.META.get('HTTP_ORIGIN', '')
    ip = request.data.get('ip', '')

    # Crear una instancia de Auditoria
    auditoria_instance = Auditoria(
        ip=ip,
        servidor=request.META.get('COMPUTERNAME', ''),
        usuario=request.user,
        evento=evento,
        nivel=nivel,
        mac=dir_mac,
        origin=origin,
    )

    # Guardar la instancia en la base de datos
    auditoria_instance.save()

    # Serializar y devolver la respuesta
    serializer = AuditoriaSerializer(auditoria_instance)
    return Response(serializer.data)