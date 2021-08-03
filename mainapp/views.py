from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import TemplateView, ListView
from django.http import JsonResponse, HttpResponse, Http404
from django.contrib.auth.mixins import LoginRequiredMixin

import time
from paygate.models import Package, Order
from paygate.coinbase_client import coinbase_api

from .main.driver import Driver

from .models import DiscordServer, DirectMessage


class Dashboard(LoginRequiredMixin, TemplateView):
    template_name = 'mainapp/dashboard.html'
    extra_context = {
        'title': 'Dashboard'
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["orders"] = self.request.user.profile.order_set.all()
        context["messages_sent"] = DirectMessage.objects.filter().count_sent()
        return context
    

class Packages(LoginRequiredMixin, ListView):
    template_name = 'mainapp/packages.html'
    extra_context = {
        'title': 'Packages'
    }
    model = Package
    context_object_name = 'packages'
    
    def get_queryset(self):
        return super().get_queryset().filter(active=True)

    @property
    def object_list(self):
        checkouts = coinbase_api.list_checkout()
        # return self.get_queryset()
        return checkouts
    
    def get(self, request, *args, **kwargs):
        context = self.get_context_data()

        # If package_uid of package was sent create a charge and redirect user to payment link
        checkout_id = request.GET.get('checkout')
        if checkout_id:
            charge_url = coinbase_api.create_charge(checkout_id, self.request.user, request)
            return redirect(charge_url)
            
        return render(request, self.template_name, context)
    

class Support(LoginRequiredMixin, TemplateView):
    template_name = 'mainapp/support.html'
    extra_context = {
        'title': 'Support'
    }

class Faq(LoginRequiredMixin, TemplateView):
    template_name = 'mainapp/faq.html'
    extra_context = {
        'title': 'Frequently Asked Questions'
    }


drivers = []
class DmPanel(LoginRequiredMixin, TemplateView):
    template_name = 'mainapp/dmpanel.html'
    extra_context = {
        'title': 'DM Panel'
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["listed_servers"] = self.request.user.discordserver_set.all()
        context['messages_left'] = Order.objects.filter(profile=self.request.user.profile).count_dm() - DirectMessage.objects.filter().count_sent()
        return context
    
    def get_driver(self):
        driver_instance = None
        print(drivers)
        if len(drivers) > 0:
            for i in drivers:
                if i.working == False:
                    driver_instance = i
        if driver_instance is None:
            print('Created new driver')
            driver_instance = Driver()
        return driver_instance

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        context = self.get_context_data()

        listed_servers = context['listed_servers']

        # time.sleep(10)

        if request.is_ajax():
            # Identify which codes will be processed
            discord_server_invite_link = request.POST.get('discord_server_invite_link')
            connect_id = request.POST.get('connect_id')

            if discord_server_invite_link:
                # Get discord name and save
                result = listed_servers.filter(link__exact=discord_server_invite_link)
                if result.exists():
                    return JsonResponse({'data': 'invalid', 'message': 'Server has already been added'}, status=400)
                else:
                    # Try to find if there are other discord servers with the same invite link
                    queryset = DiscordServer.objects.filter(link__exact=discord_server_invite_link)
                    if queryset.exists():
                        obj = queryset.first()
                        server = DiscordServer.objects.create(
                            link=discord_server_invite_link,
                            user=request.user,
                            name = obj.name,
                            members = obj.members,
                            icon = obj.icon,
                        )
                    else:
                        server = DiscordServer.objects.create(link=discord_server_invite_link, user=request.user)
                        driver_instance = self.get_driver()
                        response = driver_instance.parse_server_basic(server)

                        # Add the driver to memory
                        if driver_instance not in drivers:
                            drivers.append(driver_instance)

                        if response != True:
                            server.delete()
                            return self.json_err_response(response)

                return JsonResponse({'data': 'success', 'message':'Server has been succesfully added', 'object': {'name': server.name, 'members': server.members, 'icon': server.icon}}, status=200)
            elif connect_id:
                # Verify the connect_id
                discord_server = get_object_or_404(DiscordServer, uid=connect_id)

                # Get usable driver and parse out users
                driver_instance = self.get_driver()
                response = driver_instance.parse_users(discord_server)

                if response != True:
                    return self.json_err_response(response)
                
                if driver_instance not in drivers:
                    drivers.append(driver_instance)
                
                return JsonResponse({'data': 'success', 'message':f'Server has been parsed, {discord_server.member_set.count()} members parsed to receive messages'}, status=200)

        return render(request, self.template_name, context)
    
    def json_err_response(self, response):
        message = 'Problem connecting with server, try again in a few mins'
        if isinstance(response, str):
            # This means a message was passed
            message = response
        return JsonResponse({'data': 'invalid', 'message': message}, status=400)