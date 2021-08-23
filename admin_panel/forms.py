from django import forms

from account.models import DiscordAccount, ProxyPort

from django.db.utils import IntegrityError

from .utils import checkIP


class AddAccountForm(forms.ModelForm):
    class Meta:
        model = DiscordAccount
        fields = ('email', 'password', 'token',)


class UploadAccountForm(forms.Form):
    csv_file = forms.FileField()

    def clean_csv_file(self):

        file = self.cleaned_data.get('csv_file')
        
        try:
            # Read and decode the file
            stringd = file.read().decode().strip(',').strip()
            file_str = set(stringd.strip().split(','))

            # Loop through each data point and split
            mother = []
            for i in file_str:
                if i.find(':') != -1:
                    mother.append([x.strip() for x in i.split(':')])
                else:
                    raise ValueError
            
            return mother
        except ValueError:
            raise forms.ValidationError('Your CSV File is not in the right format')

    def save(self, *args, **kwargs):
        mother = self.cleaned_data.get('csv_file')
        created = []
        for i in mother:
            try:
                email, password, token = i
                d = DiscordAccount.objects.create(email=email, password=password, token=token)
                created.append(d)
            except (ValueError, IntegrityError,):
                pass
        
        return created


class AddProxyForm(forms.ModelForm):
    class Meta:
        model = ProxyPort
        fields = ('ip_port',)
    
    def clean_ip_port(self):

        ip_port = self.cleaned_data.get('ip_port')
        
        try:
            if ip_port.find(':') == -1:
                raise ValueError

            ip = ip_port.split(':')[0]
            if checkIP(ip) == False:
                raise ValueError

        except (ValueError, IndexError,):
            raise forms.ValidationError('Your Proxy Address is not Valid')
        
        return ip_port


class UploadProxyForm(forms.Form):
    csv_file = forms.FileField()

    def clean_csv_file(self):

        file = self.cleaned_data.get('csv_file')
        
        try:
            # Read and decode the file
            stringd = file.read().decode().strip(',').strip()
            file_str = set([i.strip() for i in stringd.strip().split(',')])

            # Validate each address in the list
            for i in file_str:
                if i.find(':') == -1:
                    raise ValueError

                ip = i.split(':')[0]
                if checkIP(ip) == False:
                    raise ValueError

            return file_str

        except (ValueError, IndexError,):
            raise forms.ValidationError('Your CSV File is not in the right format')

    def save(self, *args, **kwargs):
        mother = self.cleaned_data.get('csv_file')
        created = []
        for i in mother:
            try:
                d = ProxyPort.objects.create(ip_port=i)
                created.append(d)
            except (ValueError, IntegrityError,):
                pass
        
        return created