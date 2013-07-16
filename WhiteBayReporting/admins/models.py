from django.db import models
from django.contrib import admin

    
# future fees rate based on symbol
class FutureFeeRate(models.Model):
    
    symbol = models.CharField( max_length=50 )
    clearingFeeRate = models.FloatField( default=0.00 )
    exchangeFeeRate = models.FloatField( default=0.00 )
    nfaFeeRate = models.FloatField( default=0.00 )
    
    group = models.CharField( max_length=30, default="")
    
    def save(self, *args, **kwargs): 
        super(FutureFeeRate, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return str(self.symbol)
    
# future multiplier per contract based on symbol
class FutureMultiplier(models.Model):
    
    symbol = models.CharField( max_length=50 )
    multiplier = models.IntegerField( default=1 )
    
    def save(self, *args, **kwargs): 
        super(FutureMultiplier, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return str(self.symbol)


class Broker(models.Model):
    
    brokerNumber = models.CharField( max_length=50 )
    securityType = models.CharField( max_length=10 )
    commissionRate = models.FloatField( default=0.00 )
    
    def save(self, *args, **kwargs): 
        super(Broker, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return str(self.brokerNumber)



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



class Group(models.Model):
    
    name = models.CharField( max_length=30 )
    
    def save(self, *args, **kwargs): 
        super(Group, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return str(self.group)



class Account(models.Model):
    
    account = models.CharField( max_length=30 )
    grossPNL = models.FloatField( default=0.00 )
    unrealizedPNL = models.FloatField( default=0.00 )
    netPNL = models.FloatField( default=0.00 )
    
    commission = models.FloatField( default=0.00 )
    secFees = models.FloatField( default=0.00 )
    ecnFees = models.FloatField( default=0.00 )
    # for the trades whose Route is "WBPT" and Destination is "FBCO", "UBS", or "BARC"
    accruedSecFees = models.FloatField(default=0.00 )

    
    #group = models.CharField( max_length=30, blank=True, null=True, default="" ) # group name, empty for no group
    
    def save(self, *args, **kwargs): 
        super(Account, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return str(self.account)

# account's future group
class FutureFeeGroup(models.Model):
    
    account = models.CharField( max_length=30 )
    symbol = models.CharField( max_length=50 )
    group = models.CharField( max_length=30 )   
    
    def save(self, *args, **kwargs):
        super(FutureFeeGroup, self).save(*args, **kwargs)
        
    def __unicode__(self):
        return str(self.account + " " + self.symbol)

# firm profile
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
    
    
# routes, related to ecn fees
class Route(models.Model):

    seqNo = models.IntegerField( default=0 )
    routeId = models.CharField( max_length=10 )
    effectiveFrom = models.DateTimeField( blank=True, null=True )
    effectiveTo = models.DateTimeField( blank=True, null=True )
    flag = models.CharField( max_length=5, blank=True, null=True, default="" )
    primaryExchange = models.CharField( max_length=10, blank=True, null=True, default="" )
    tape = models.CharField( max_length=5, blank=True, null=True, default="" )
    isETF = models.CharField( max_length=5, blank=True, null=True, default="" )
    priceFrom = models.FloatField( default=0.00 )
    priceTo = models.FloatField( default=0.00 )
    rebateCharge = models.FloatField( default=0.00 )
    feeType = models.CharField( max_length=20, blank=True, null=True, default="" )
    description = models.CharField( max_length=100, blank=True, null=True, default="" )
    insertedBy = models.CharField( max_length=20, blank=True, null=True, default="" )
    insertedDate = models.DateTimeField(blank=True, null=True)
    modifiedBy = models.CharField( max_length=20, blank=True, null=True, default="" )
    modifiedDate = models.DateTimeField(blank=True, null=True)
    
    
    def save(self, *args, **kwargs): 
        super(Route, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return str(self.seqNo)

admin.site.register(Broker)
admin.site.register(Trader)
admin.site.register(System)
admin.site.register(Firm)
admin.site.register(Route)
admin.site.register(Account)