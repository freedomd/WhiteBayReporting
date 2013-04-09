from django.db import models
from django.contrib import admin

class Trade(models.Model):

    SIDE_CHOICES = (('SEL', 'SEL'), ('BUY', 'BUY'), ('SS', 'SS'))

    account = models.CharField( max_length=20 )
    symbol = models.CharField( max_length=10 )
    securityType = models.CharField( max_length=10, blank=True, null=True, default="")
    side = models.CharField( choices=SIDE_CHOICES, max_length=5, default="SEL")
    quantity = models.IntegerField( default=0 )
    price = models.FloatField( default=0.00 )
    broker = models.CharField( max_length=20, blank=True, null=True, default="")
    route = models.CharField( max_length=10, blank=True, null=True, default="")
    destination = models.CharField( max_length=10, blank=True, null=True, default="")
    liqFlag = models.CharField( max_length=5, blank=True, null=True, default="")
    tradeDate = models.DateField( auto_now_add=False )
    executionId = models.CharField( max_length=50, default="0" )
#    clearanceFees = models.FloatField( default=0.00 )
#    brokerCommission = models.FloatField( default=0.00 )
#    commission = models.FloatField( default=0.00 )
#    secFees = models.FloatField( default=0.00 )
#    ecnFees = models.FloatField( default=0.00 )
    
    def save(self, *args, **kwargs): 
        super(Trade, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return str(self.id)
    


class RollTrade(models.Model):

    SIDE_CHOICES = (('SEL', 'SEL'), ('BUY', 'BUY'), ('SS', 'SS'))
    
    account = models.CharField( max_length=20 )
    symbol = models.CharField( max_length=10 )
    side = models.CharField( choices=SIDE_CHOICES, max_length=5, default="SEL")
    quantity = models.IntegerField( default=0 )
    price = models.FloatField( default=0.00 )
    route = models.CharField( max_length=10, blank=True, null=True, default="")
    destination = models.CharField( max_length=10, blank=True, null=True, default="")
    liqFlag = models.CharField( max_length=5, blank=True, null=True, default="")
    tradeDate = models.DateField( auto_now_add=False )
#    clearanceFees = models.FloatField( default=0.00 )
    
    def save(self, *args, **kwargs): 
        super(RollTrade, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return str(self.id)

admin.site.register(Trade)
admin.site.register(RollTrade)