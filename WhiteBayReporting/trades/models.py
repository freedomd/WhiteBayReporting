from django.db import models
from django.contrib import admin

class Trade(models.Model):

    SIDE_CHOICES = (('SEL', 'SEL'), ('BUY', 'BUY'), ('SS', 'SS'))

    account = models.CharField( max_length=20 )
    symbol = models.CharField( max_length=10 )
    side = models.CharField( choices=SIDE_CHOICES, max_length=5, default="SEL")
    quantity = models.IntegerField( default=0 )
    price = models.FloatField( default=0.00 )
    broker = models.CharField( max_length=20 )
    tradeDate = models.DateTimeField( auto_now_add=False )
    exchange = models.CharField( max_length=20, blank=True, null=True )
    executionId = models.BigIntegerField( default=0 )
    
    def save(self, *args, **kwargs): 
        super(Trade, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return str(self.id)
    
admin.site.register(Trade)