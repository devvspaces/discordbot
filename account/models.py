import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.mail import send_mail
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.urls import reverse

from .managers import DiscordAccountManager


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, is_active=True, is_staff=False, is_admin=False):
        if not email:
            raise ValueError("User must provide an email")
        if not password:
            raise ValueError("User must provide a password")

        user = self.model(
            email=self.normalize_email(email)
        )
        user.set_password(password)
        user.active = is_active
        user.admin = is_admin
        user.staff = is_staff
        user.save(using=self._db)
        return user

    def create_staff(self, email, password=None):
        user = self.create_user(email=email, password=password, is_staff=True)
        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(email=email, password=password, is_staff=True, is_admin=True)
        return user

    def get_staffs(self):
        return self.filter(staff=True)

    def get_admins(self):
        return self.filter(admin=True)


class User(AbstractBaseUser):
    email = models.EmailField(unique=True)

    # Admin fields
    active = models.BooleanField(default=False)
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    start_date = models.DateTimeField(auto_now=True)

    REQUIRED_FIELDS = []
    USERNAME_FIELD = "email"

    objects = UserManager()

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True
    
    @property
    def discord_username(self):
        return self.profile.discord_username
    
    @property
    def get_emailname(self):
        # Return the x part of an email e.g [x]@gmail.com
        return self.email.split('@')[0]

    def __str__(self):
        return self.email

    # def get_absolute_url(self):
    #     return reverse('profile', kwargs = [self.id])

    def email_user(self, subject, message, fail=True):
        print(message)
        val = send_mail(subject=subject, message=message, from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=[self.email], fail_silently=fail)
        return True if val else False

    @property
    def is_active(self):
        return self.active

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_admin(self):
        return self.admin


class DiscordAccount(models.Model):
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField()
    password = models.CharField(max_length=200)
    token = models.CharField(max_length=200)
    active = models.BooleanField(default=False)
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    use_count = models.IntegerField(default=0)

    objects = DiscordAccountManager()

    def __str__(self):
        return str(self.uid)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    discord_username = models.CharField(max_length=200, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return str(self.uid)

    # def get_absolute_url(self):
    #     return reverse('profile', args=[self.first_name])


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    profile = Profile.objects.get_or_create(user=instance)