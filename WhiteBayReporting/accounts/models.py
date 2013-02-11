from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin

class UserProfile(models.Model):

    user = models.OneToOneField(User, unique=True)
    
    def __unicode__(self):
        return self.user.username
    
admin.site.register(UserProfile)