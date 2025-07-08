from django.views.generic import TemplateView

from accounts.models import About


class Homepage(TemplateView):
    template_name = "homepage.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] =About.objects.first()
        return context

# class About(TemplateView):
#     template_name = "about.html"

class Privacy(TemplateView):
    template_name = "privacy.html"

# class Dashboard(TemplateView):
#     template_name = "dashboard.html"


class Terms(TemplateView):
    template_name = "terms.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] =About.objects.only("email", "phone").first()
        return context
