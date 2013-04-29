from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin

class UserProfile(models.Model):

    user = models.OneToOneField(User, unique=True)
    addr = models.CharField( max_length=100, blank=True, null=True, default="" )
    phone = models.CharField( max_length=20, blank=True, null=True, default="" )
    description = models.CharField( max_length=500, blank=True, null=True, default="")
    
    def save(self, *args, **kwargs): 
        super(UserProfile, self).save(*args, **kwargs)
        
    def __unicode__(self):
        return self.user.username
    
admin.site.register(UserProfile)