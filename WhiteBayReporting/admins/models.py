from django.db import models
from django.contrib import admin

class Broker(models.Model):
    
    name = models.CharField( max_length=50 )
    commission = models.FloatField( default=0.00 )
    
    def save(self, *args, **kwargs): 
        super(Broker, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return str(self.name)

admin.site.register(Broker)