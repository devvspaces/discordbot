from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import TemplateView

from account.models import DiscordAccount

from .forms import AddAccountForm, UploadAccountForm, AddProxyForm, UploadProxyForm


class AddAccount(LoginRequiredMixin, TemplateView):
    template_name = 'admin_panel/add_account.html'
    extra_context = {
        'title': 'Add Account'
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["manual"] = AddAccountForm()
        context["csv_form"] = UploadAccountForm()
        return context
    
    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        data = request.POST
        submit = data.get('submit')
        
        if submit == 'manual':
            form = AddAccountForm(request.POST)
            if form.is_valid():
                obj = form.save()
                messages.success(request, f'Account {obj.email} is successfully added')
                
                # Redirect to admin list view
                return redirect('admin_panel:add_account')
            
            context['manual'] = form
        
        elif submit == 'file':
            form = UploadAccountForm(files=request.FILES)
            if form.is_valid():
                created = form.save()
                messages.success(request, f'Created {len(created)} new Accounts successfully')
                
                # Redirect to admin list view
                return redirect('admin_panel:add_account')
            
            context['csv_form'] = form
        
        return render(request, self.template_name, context)


class AddProxy(LoginRequiredMixin, TemplateView):
    template_name = 'admin_panel/add_proxy.html'
    extra_context = {
        'title': 'Add Proxy'
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["manual"] = AddProxyForm()
        context["csv_form"] = UploadProxyForm()
        return context
    
    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        data = request.POST
        submit = data.get('submit')
        
        if submit == 'manual':
            form = AddProxyForm(request.POST)
            if form.is_valid():
                obj = form.save()
                messages.success(request, f'Proxy {obj.ip_port} is successfully added')
                
                # Redirect to admin list view
                return redirect('admin_panel:add_proxy')
            
            context['manual'] = form
        
        elif submit == 'file':
            form = UploadProxyForm(files=request.FILES)
            if form.is_valid():
                created = form.save()
                messages.success(request, f'Created {len(created)} new Proxies successfully')
                
                # Redirect to admin list view
                return redirect('admin_panel:add_proxy')
            
            context['csv_form'] = form
        
        return render(request, self.template_name, context)