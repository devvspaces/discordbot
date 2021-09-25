import time
import threading
import logging
# Create the logger and set the logging level
logger = logging.getLogger('basic')
err_logger = logging.getLogger('basic.error')

from django.contrib.sites.shortcuts import get_current_site

from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import TemplateView, ListView, DetailView
from django.http import JsonResponse, HttpResponse, Http404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings

from paygate.models import Package, Order
from paygate.coinbase_client import coinbase_api

from .main.driver import Driver

from .models import Blacklist, DiscordServer, DirectMessage, BlacklistParent, Member

from .mixins import AjaxResponders


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
    

class DiscordServerDetail(LoginRequiredMixin, DetailView, AjaxResponders):
    template_name = 'mainapp/server_detail.html'
    extra_context = {
        'title': ''
    }
    slug_url_kwarg = 'uid'
    slug_field = 'uid'
    context_object_name = 'server'
    model = DiscordServer

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["blacklists"] = self.request.user.blacklistparent_set.all()
        context["title"] = self.get_object().name
        return context
    
    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            uid = request.POST.get('uid')
            blacklist = request.POST.get('blacklist')
            link = request.POST.get('link')
            
            # Get the server object
            server = self.get_object()

            if uid:
                user = self.request.user

                # Verify the uid
                try:
                    member = server.member_set.get(uid=uid)
                except Member.DoesNotExist:
                    return self.json_err_response('Error processing request')
                
                if blacklist == 'true':
                    blacklist_uid = request.POST.get('blacklist_uid')

                    # Verify the blacklist_uid
                    try:
                        blacklist_obj = user.blacklistparent_set.get(uid=blacklist_uid)
                    except BlacklistParent.DoesNotExist:
                        return self.json_err_response('Error processing request')
                    
                    # Create the blacklist for this user and delete member
                    member.delete()
                    blacklist_obj.blacklist_set.get_or_create(username=member.username)

                    return JsonResponse(data={'message': 'Member is successfully deleted and added to blacklist'}, status=200)

                else:
                    member.delete()
                    del member
                    return JsonResponse(data={'message': 'Member is successfully deleted'}, status=200)
            
            if link:
                validation_errors = []
                valid = True

                # Verify the link
                if len(link) > 40:
                    valid = False
                    validation_errors.append('Your discord link is too long')
                
                # Verify the link
                if not link.startswith('https://discord.gg/'):
                    valid = False
                    validation_errors.append('Your discord link is not valid')
                
                # Send errors if not valid
                if not valid:
                    return self.json_err_response('<br>'.join(validation_errors))
                

                # Update the server link
                server.link = link
                server.save()
                return JsonResponse(data={'message': 'Discord server invite link is successfully updated'}, status=200)

            return self.json_err_response('You request could not be processed')


class BlacklistDetail(LoginRequiredMixin, DetailView, AjaxResponders):
    template_name = 'mainapp/blacklist_detail.html'
    extra_context = {
        'title': ''
    }
    slug_url_kwarg = 'uid'
    slug_field = 'uid'
    context_object_name = 'blacklist'
    model = BlacklistParent

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.get_object().gen_name()
        context["back_url"] = self.request.META.get('HTTP_REFERER', '/')
        return context
    
    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            uid = request.POST.get('uid')

            if uid:
                # Get the blacklist parent
                parent = self.get_object()

                # Verify the uid
                try:
                    blacklist = parent.blacklist_set.get(id=uid)
                except Blacklist.DoesNotExist:
                    return self.json_err_response('Error processing request')

                else:
                    blacklist.delete()
                    del blacklist
                    return JsonResponse(data={'message': 'User is successfully removed from blacklist'}, status=200)

            return self.json_err_response('You request could not be processed')
    

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
events_dict = dict()

class DmPanel(LoginRequiredMixin, TemplateView, AjaxResponders):
    template_name = 'mainapp/dmpanel.html'
    extra_context = {
        'title': 'DM Panel'
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["listed_servers"] = self.request.user.discordserver_set.all()

        user_profile = self.request.user.profile
        total_sent = DirectMessage.objects.filter(profile=user_profile).count_sent()
        total_messages = Order.objects.filter(profile=user_profile).count_dm()
        context['total_messages'] = total_messages
        context['total_sent'] = total_sent
        context['messages_left'] = total_messages - total_sent

        context['blacklists'] = BlacklistParent.objects.filter(user = self.request.user)
        context['room_name'] = str(self.request.user.profile.discord_username)

        # Get the uid of any running messages
        running_e = DirectMessage.objects.filter(completed=False)
        if running_e.exists():
            context['running_message'] = running_e.first().uid
        
        return context
    
    def get_driver(self):
        driver_instance = None
        for i in drivers:
            if i.working == False:
                driver_instance = i
                break

        if (driver_instance is None) and (len(drivers) <= settings.BOT_MAX):
            try:
                driver_instance = Driver()
                drivers.append(driver_instance)
                logger.debug(f'Appended the new driver, new length: {len(drivers)}')
            except Exception as e:
                err_logger.exception(e)
            
        logger.debug(f'Bot that was found: {driver_instance}')

        return driver_instance

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        context = self.get_context_data()

        listed_servers = context['listed_servers']

        if request.is_ajax():
            # Identify which codes will be processed
            data = request.POST
            discord_server_invite_link = data.get('discord_server_invite_link')
            connect_id = data.get('connect_id')

            blacklist_user_name = request.POST.get('blacklist_user_name')
            d_file = request.FILES.get('blacklist_user_id')

            blacklist_uid = data.get('blacklist_uid')
            send_dm = data.get('send_dm')
            delete_uid = data.get('delete_uid')

            stop_message = data.get('stop_message')


            if discord_server_invite_link:
                # Check if user has bought messages
                if context['messages_left'] <= 0:
                    return self.json_err_response('You do not have any messages left, Kindly buy by making a new order.')

                # Get discord name and save
                result = listed_servers.filter(link__exact=discord_server_invite_link)
                if result.exists():
                    return self.json_err_response('Server has already been added')
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
                        driver_instance = self.get_driver()
                        if driver_instance is None:
                            return self.json_err_response('There are currently no bots available')

                        # Bot found
                        server = DiscordServer(link=discord_server_invite_link, user=request.user)

                        response = driver_instance.parse_server_basic(server)

                        if response != True:
                            return self.json_err_response(response)

                return JsonResponse({
                    'data': 'success',
                    'message':'Server has been succesfully added',
                    'object': {
                        'name': server.name[:13],
                        'members': server.members,
                        'icon': server.icon if server.icon else f'http://{get_current_site(request)}/static/assets/images/feature-module.png',
                        'uid': str(server.uid),
                        'url': server.get_absolute_url()
                    }
                }, status=200)

            elif connect_id:
                # Check if user has bought messages
                if context['messages_left'] <= 0:
                    return self.json_err_response('You do not have any messages left, Kindly buy by making a new order.')

                # Verify the connect_id
                try:
                    discord_server = DiscordServer.objects.get(uid=connect_id)
                except DiscordServer.DoesNotExist:
                    return self.json_err_response('Error processing request')

                # Know which request was sent
                req_type = data.get('req_type')

                if req_type == 'connect':
                    # Get usable driver and parse out users
                    driver_instance = self.get_driver()
                    if driver_instance is None:
                        return self.json_err_response('There are currently no bots available')

                    # This is to get the online members in the server and its also updates the server details in the database
                    response = driver_instance.get_server_details(discord_server)

                    if not isinstance(response, int):
                        return self.json_err_response(response)
                    
                    return JsonResponse({
                        'data': 'success',
                        'message':f"Discord server is successfully connected, {response} members are available to receive messages"}, status=200)

                elif req_type == 'remove':
                    discord_server.delete()
                    return JsonResponse({
                        'data':'success',
                        'message': f'Discord server {discord_server.name} is successfully removed'}, status=200)
            
            elif d_file or blacklist_user_name:
                blacklist_parent = BlacklistParent(user=self.request.user)

                if blacklist_user_name:
                    # Validate name length first
                    if len(blacklist_user_name) > 50:
                        return self.json_err_response('Your blacklist name is too long')

                    blacklist_parent.name = blacklist_user_name
                    blacklist_parent.save()

                if d_file:
                    usernames = set([i.strip() for i in d_file.read().decode().split(',')])

                    # Create blacklist with usernames
                    for i in usernames:
                        blacklist_parent.blacklist_set.create(username=i)
                    
                    blacklist_parent.save()

                return JsonResponse({
                    'data': 'success',
                    'message': 'Added the blacklist',
                    'object': {
                        'name': blacklist_parent.gen_name()[:13],
                        'members': blacklist_parent.count_list(),
                        'uid': str(blacklist_parent.uid),
                        'url': blacklist_parent.get_absolute_url()
                    }}, status=200)
            
            elif send_dm == 'true':
                # Get the needed data
                blacklist_uid = data.get('blacklist_uid')
                connect_uid = data.get('connect_uid')
                direct_message = data.get('direct_message')
                stop_after_amount = data.get('stop_after_amount')
                add_friend_checkbox = data.get('add_friend_checkbox')
                add_to_blacklist_checkbox = data.get('add_to_blacklist_checkbox')
                delay = data.get('delay')
                blacklist = ''

                # Validate the data
                valid = True
                validation_errors = []
                if len(direct_message) == 0:
                    valid = False
                    validation_errors.append('Your message can\'t be empty')
                
                # Verify the blacklist_uid
                try:
                    if blacklist_uid:
                        blacklist = BlacklistParent.objects.get(uid=blacklist_uid)
                        if blacklist.count_list() == 0:
                            valid = False
                            validation_errors.append('Blacklist selected contains no username')
                except BlacklistParent.DoesNotExist:
                    valid = False
                    validation_errors.append('Blacklist selected not found')
                
                # Verify the connect_uid
                try:
                    if connect_uid:
                        server = DiscordServer.objects.get(uid=connect_uid)
                        if server.members <= 0:
                            valid = False
                            validation_errors.append('Server selected contains no members')
                    else:
                        valid = False
                        validation_errors.append('You must connect a server')
                except DiscordServer.DoesNotExist:
                    valid = False
                    validation_errors.append('Discord Server selected not found')
                
                # Validate delay
                try:
                    if int(delay) < 15:
                        raise ValueError
                except  ValueError:
                    valid = False
                    validation_errors.append('Your delay time must be greater than 15')
                
                # Validate stop_after_amount
                try:
                    stop_after_amount = int(stop_after_amount)
                except  ValueError:
                    valid = False
                    validation_errors.append('Your form is invalid')
                
                # Validate add_to_blacklist_checkbox
                if add_to_blacklist_checkbox == 'true':
                    # If true user must have selected a blacklist
                    if not blacklist:
                        valid = False
                        validation_errors.append('You must select a blacklist to use Repeat Users to Blacklist option')
                    
                
                # Verify if user has a message still processing
                profile = request.user.profile
                if DirectMessage.objects.filter(profile=profile, completed=False).count() > 0:
                    valid = False
                    validation_errors.append('You have a message still sending, stop before sending another message')
                
                # Verify if the user has any messages left
                messages_left = context['messages_left']
                if messages_left <= 0:
                    valid = False
                    validation_errors.append('You don\'t have any messages left, kindly go to the new order section to buy any package suitable for your use')

                if not valid:
                    return self.json_err_response('<br>'.join(validation_errors))

                
                # Create new message
                message = DirectMessage(profile=profile, message=direct_message, delay=delay, server=server)
                if stop_after_amount:
                    message.message_stop = stop_after_amount
                
                if add_friend_checkbox == 'true':
                    message.add_users = True
                
                if add_to_blacklist_checkbox == 'true':
                    message.blacklist_users = True
                
                if blacklist_uid:
                    message.blacklist = blacklist
                
                message.save()
                
                # Get the driver instance and send the message
                driver_instance = self.get_driver()
                if driver_instance is None:
                    return self.json_err_response('There are not bots available now, try again later')


                # Create an event for this
                new_event = threading.Event()

                t1 = threading.Thread(target=driver_instance.send_message, args=(message, new_event))
                t1.start()

                # Add the event to dict
                events_dict[message.uid] = new_event

                # Send the result back to the page
                return JsonResponse({
                    'data': 'success',
                    'message_uid': message.uid,
                    'message': 'Started sending message'
                    }, status=200)

            elif blacklist_uid:
                # Verify the blacklist_uid
                try:
                    blacklist = BlacklistParent.objects.get(uid=blacklist_uid)
                    blacklist.delete()
                except BlacklistParent.DoesNotExist:
                    return self.json_err_response('Error processing your request')
                
                return JsonResponse({
                    'data': 'success',
                    'message': 'Removed the blacklist'
                    }, status=200)
            
            elif delete_uid:
                # Get the sent uids and verify all
                uids = delete_uid.split('|')
                uid_objs = []
                for i in uids:
                    # Verify the connect_id
                    try:
                        uid_objs.append(DiscordServer.objects.get(uid=i))
                    except DiscordServer.DoesNotExist:
                        return self.json_err_response('Error processing request')
                
                for i in uid_objs:
                    i.delete()

                return JsonResponse({
                    'data': 'success',
                    'message':'Servers have been successfully removed'}, status=200)

            elif stop_message:
                # Verify if the message exists
                try:
                    message = DirectMessage.objects.get(uid=stop_message)
                except DirectMessage.DoesNotExist:
                    return self.json_err_response('Error processing your request')
                
                message.setStop()
                
                return JsonResponse({
                    'data': 'success',
                    'message':'Message is successfully set to stop'}, status=200)
            
        return render(request, self.template_name, context)
    