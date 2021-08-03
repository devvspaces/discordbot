from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.generic import TemplateView


class Landing(TemplateView):
    template_name = 'static_app/index.html'

    def get(self, request, *args, **kwargs):
        # Check if user is already logged in
        if request.user.is_authenticated:
            return redirect('dashboard:home')

        return render(request, self.template_name, self.get_context_data())


class Pricing(TemplateView):
    template_name = 'static_app/pricing.html'
    extra_context = {
        'title': 'Pricing'
    }
