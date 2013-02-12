from django.db import models
from django.contrib import admin

# report for each symbol everyday
class Report(models.Model):
    
    symbol = models.CharField( max_length=10 )
    SOD = models.IntegerField( default=0 )
    buys = models.IntegerField( default=0 )
    buyAve = models.FloatField( default=0.00 )
    sells = models.IntegerField( default=0 )
    sellAve = models.FloatField( default=0.00 )
    grossPNL = models.FloatField( default=0.00 )
    unrealizedPNL = models.FloatField( default=0.00 )
    fees = models.FloatField( default=0.00 )
    netPNL = models.FloatField( default=0.00 )
    LMV = models.FloatField( default=0.00 )
    SMV = models.FloatField( default=0.00 )
    mark = models.FloatField( default=0.00 ) # closing price of the day
    EOD = models.IntegerField( default=0 )
    reportDate = models.DateTimeField( auto_now_add=False )
    
    def save(self, *args, **kwargs): 
        super(Report, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return str(self.id)

# report of summary data every day
class DailyReport(models.Model):
    
    SOD = models.IntegerField( default=0 )
    buys = models.IntegerField( default=0 )
    #buyAve = models.FloatField( default=0.00 )
    sells = models.IntegerField( default=0 )
    #sellAve = models.FloatField( default=0.00 )
    grossPNL = models.FloatField( default=0.00 )
    unrealizedPNL = models.FloatField( default=0.00 )
    fees = models.FloatField( default=0.00 )
    netPNL = models.FloatField( default=0.00 )
    LMV = models.FloatField( default=0.00 )
    SMV = models.FloatField( default=0.00 )
    mark = models.FloatField( default=0.00 ) # closing price of the day
    EOD = models.IntegerField( default=0 )
    reportDate = models.DateField( auto_now_add=False )
    
    def save(self, *args, **kwargs): 
        super(DailyReport, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return str(self.id)

# report of summary data every month
class MonthlyReport(models.Model):
    
    SOD = models.IntegerField( default=0 )
    buys = models.IntegerField( default=0 )
    #buyAve = models.FloatField( default=0.00 )
    sells = models.IntegerField( default=0 )
    #sellAve = models.FloatField( default=0.00 )
    grossPNL = models.FloatField( default=0.00 )
    unrealizedPNL = models.FloatField( default=0.00 )
    fees = models.FloatField( default=0.00 )
    netPNL = models.FloatField( default=0.00 )
    LMV = models.FloatField( default=0.00 )
    SMV = models.FloatField( default=0.00 )
    mark = models.FloatField( default=0.00 ) # closing price of the day
    EOD = models.IntegerField( default=0 )
    reportDate = models.DateField( auto_now_add=False )
    
    def save(self, *args, **kwargs): 
        super(MonthlyReport, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return str(self.id)
    
admin.site.register(Report)
admin.site.register(DailyReport)
admin.site.register(MonthlyReport)