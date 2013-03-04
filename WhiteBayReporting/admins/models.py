from django.db import models
from django.contrib import admin

class Broker(models.Model):
    
    name = models.CharField( max_length=50 )
    commission = models.FloatField( default=0.00 )
    
    def save(self, *args, **kwargs): 
        super(Broker, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return str(self.name)


class Trader(models.Model):
    
    name = models.CharField( max_length=30 )
    SSN = models.CharField( max_length=20, blank=True, null=True, default="")
    addr = models.CharField( max_length=100, blank=True, null=True, default="" )
    phone = models.CharField( max_length=20, blank=True, null=True, default="" )
    email = models.EmailField( blank=True, null=True )
    username = models.CharField( max_length=30, blank=True, null=True, default="" )
    password = models.CharField( max_length=30, blank=True, null=True, default="" )
    clearanceFee = models.FloatField( blank=True, null=True, default=0.00 )
    brokerFee = models.FloatField( blank=True, null=True, default=0.00 )
    
    def save(self, *args, **kwargs): 
        super(Trader, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return str(self.name)

admin.site.register(Broker)
admin.site.register(Trader)