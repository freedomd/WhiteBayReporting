from django.db import models
from django.contrib import admin


class Broker(models.Model):
    
    name = models.CharField( max_length=50 )
    commission = models.FloatField( default=0.00 )
    
    def save(self, *args, **kwargs): 
        super(Broker, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return str(self.name)


class System(models.Model):
    
    name = models.CharField( max_length=50 )
    cost = models.FloatField( default=0.00 )
    
    def save(self, *args, **kwargs): 
        super(System, self).save(*args, **kwargs)
    
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
    systems = models.ManyToManyField( System, blank=True, null=True )
    
    def save(self, *args, **kwargs): 
        super(Trader, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return str(self.name)
    
class Employer(models.Model):
    
    name = models.CharField( max_length=30 )
    
    def save(self, *args, **kwargs): 
        super(Employer, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return str(self.name)
    
    
class Firm(models.Model):
    
    # clearance fee
    equity = models.FloatField( default=0.00 )
    DVP = models.FloatField( default=0.00 )
    options = models.FloatField( default=0.00 )
    H2B = models.FloatField( default=0.00 )
    clearanceMax = models.FloatField( default=3.00 )
    clearanceMin = models.FloatField( default=0.01 )
    brokers = models.ManyToManyField( Broker, blank=True, null=True )
    secFee = models.FloatField( default=0.00 )
    rent = models.FloatField( default=0.00 )
    technology = models.CharField( max_length=30, blank=True, null=True, default="" )
    
    
    def save(self, *args, **kwargs): 
        super(Firm, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return str(self.id)

admin.site.register(Broker)
admin.site.register(Trader)
admin.site.register(System)
admin.site.register(Firm)