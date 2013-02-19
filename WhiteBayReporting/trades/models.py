from django.db import models
from django.contrib import admin

class Trade(models.Model):

    SIDE_CHOICES = (('S', 'S'), ('B', 'B'), ('SS', 'SS'))

    account = models.CharField( max_length=20 )
    symbol = models.CharField( max_length=10 )
    side = models.CharField( choices=SIDE_CHOICES, max_length=5, default="S")
    quantity = models.IntegerField( default=0 )
    price = models.FloatField( default=0.00 )
    broker = models.CharField( max_length=20, blank=True, null=True, default="")
    tradeDate = models.DateTimeField( auto_now_add=False )
    exchange = models.CharField( max_length=20, blank=True, null=True, default="")
    executionId = models.CharField( max_length=50, default="0" )
    
    def save(self, *args, **kwargs): 
        super(Trade, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return str(self.id)
    
admin.site.register(Trade)