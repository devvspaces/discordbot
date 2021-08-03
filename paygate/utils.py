from django.contrib.sites.shortcuts import get_current_site

def build_uri(relative_path, request):
    site = get_current_site(request).domain
    return site + relative_path