from django.db import models
from django.contrib import admin

class Trade(models.Model):

    SIDE_CHOICES = (('SEL', 'SEL'), ('SELL OPEN', 'SELL OPEN'), ('SELL CLOSE', 'SELL CLOSE'),
                    ('BUY', 'BUY'), ('BUY OPEN', 'BUY OPEN'), ('BUY CLOSE', 'BUY CLOSE'), ('SS', 'SS'))

    account = models.CharField( max_length=20 )
    symbol = models.CharField( max_length=50 )
    securityType = models.CharField( max_length=10, blank=True, null=True, default="")
    side = models.CharField( choices=SIDE_CHOICES, max_length=10, default="SEL")
    quantity = models.IntegerField( default=0 )
    price = models.FloatField( default=0.00 )
    broker = models.CharField( max_length=20, blank=True, null=True, default="")
    route = models.CharField( max_length=10, blank=True, null=True, default="")
    destination = models.CharField( max_length=10, blank=True, null=True, default="")
    liqFlag = models.CharField( max_length=5, blank=True, null=True, default="")
    tradeDate = models.DateField( auto_now_add=False )
    executionId = models.CharField( max_length=100, default="0" )
    baseMoney = models.FloatField( default=0.00 )
    description = models.CharField( max_length=100, default="NORMAL TRADE")
    ecnFees = models.FloatField( default=0.00 )
    
    def save(self, *args, **kwargs): 
        super(Trade, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return str(self.account + " " + self.symbol + " " + str(self.tradeDate))
    


class RollTrade(models.Model):

    SIDE_CHOICES = (('SEL', 'SEL'), ('SELL OPEN', 'SELL OPEN'), ('SELL CLOSE', 'SELL CLOSE'),
                    ('BUY', 'BUY'), ('BUY OPEN', 'BUY OPEN'), ('BUY CLOSE', 'BUY CLOSE'), ('SS', 'SS'))
    
    account = models.CharField( max_length=20 )
    symbol = models.CharField( max_length=50 )
    securityType = models.CharField( max_length=10, blank=True, null=True, default="")
    side = models.CharField( choices=SIDE_CHOICES, max_length=10, default="SEL")
    quantity = models.IntegerField( default=0 )
    price = models.FloatField( default=0.00 )
    broker = models.CharField( max_length=20, blank=True, null=True, default="")
    route = models.CharField( max_length=10, blank=True, null=True, default="")
    destination = models.CharField( max_length=10, blank=True, null=True, default="")
    liqFlag = models.CharField( max_length=5, blank=True, null=True, default="")
    tradeDate = models.DateField( auto_now_add=False )
    baseMoney = models.FloatField( default=0.00 )
    description = models.CharField( max_length=100, default="NORMAL TRADE")
    
    # after rolling, this ecnFees is the sum of ecnFees of the rolled trades
    ecnFees = models.FloatField( default=0.00 )
    
    def save(self, *args, **kwargs): 
        super(RollTrade, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return str(self.id)

admin.site.register(Trade)
admin.site.register(RollTrade)
