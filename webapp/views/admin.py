from django.views.generic import TemplateView


class Dashboard(TemplateView):
    template_name = "admin_custom/dashboard.html"

