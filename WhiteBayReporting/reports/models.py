from django.db import models
from django.contrib import admin
from settings import SESSION_REDIS_HOST, SESSION_REDIS_PORT
import redis

# symbol 
class Symbol(models.Model):
    
    symbol = models.CharField( max_length=10 )
    closing = models.FloatField( default=0.00 ) # closing price of day
    symbolDate = models.DateField( auto_now_add=False )
    
    def save(self, *args, **kwargs): 
        super(Symbol, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return str(self.symbol) + " " + str(self.symbolDate)

# security information
class Security(models.Model):
    
    symbol = models.CharField( max_length=10 )
    name = models.CharField( max_length=200 ) # description of the symbol
    market = models.CharField( max_length=10 )
    
    def save(self, *args, **kwargs): 
        super(Security, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return str(self.symbol)

# report for each symbol everyday
class Report(models.Model):
    
    account = models.CharField( max_length=20 )
    symbol = models.CharField( max_length=50 )
    SOD = models.IntegerField( default=0 )
    buys = models.IntegerField( default=0 )
    buyAve = models.FloatField( default=0.00 )
    sells = models.IntegerField( default=0 )
    sellAve = models.FloatField( default=0.00 )
    grossPNL = models.FloatField( default=0.00 )
    unrealizedPNL = models.FloatField( default=0.00 )
    netPNL = models.FloatField( default=0.00 )
    LMV = models.FloatField( default=0.00 )
    SMV = models.FloatField( default=0.00 )
    mark = models.FloatField( default=0.00 ) # mark price of yesterday
    closing = models.FloatField( default=0.00 ) # closing price of today
    EOD = models.IntegerField( default=0 )
    
    commission = models.FloatField( default=0.00 ) # commission = brokerCommission + clearance Fees
    brokerCommission = models.FloatField( default=0.00 )
    clearanceFees = models.FloatField( default=0.00 )
    secFees = models.FloatField( default=0.00 )
    ecnFees = models.FloatField( default=0.00 )
    
    reportDate = models.DateField( auto_now_add=False )
    
    def save(self, *args, **kwargs): 
        super(Report, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return str(self.id)

# report of summary data every day
class DailyReport(models.Model):
    
    account = models.CharField( max_length=20 )
    SOD = models.IntegerField( default=0 )
    buys = models.IntegerField( default=0 )
    sells = models.IntegerField( default=0 )
    grossPNL = models.FloatField( default=0.00 )
    unrealizedPNL = models.FloatField( default=0.00 )
    netPNL = models.FloatField( default=0.00 )
    LMV = models.FloatField( default=0.00 )
    SMV = models.FloatField( default=0.00 )
    EOD = models.IntegerField( default=0 )
    
    commission = models.FloatField( default=0.00 )
    brokerCommission = models.FloatField( default=0.00 )
    clearanceFees = models.FloatField( default=0.00 )
    secFees = models.FloatField( default=0.00 )
    ecnFees = models.FloatField( default=0.00 )
                                 
    reportDate = models.DateField( auto_now_add=False )
    
    def save(self, *args, **kwargs): 
        super(DailyReport, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return str(self.id)

# report of summary data every month
class MonthlyReport(models.Model):
    
    account = models.CharField( max_length=20 )
    buys = models.IntegerField( default=0 )
    sells = models.IntegerField( default=0 )
    grossPNL = models.FloatField( default=0.00 )
    unrealizedPNL = models.FloatField( default=0.00 )
    netPNL = models.FloatField( default=0.00 )
    
    commission = models.FloatField( default=0.00 )
    brokerCommission = models.FloatField( default=0.00 )
    clearanceFees = models.FloatField( default=0.00 )
    secFees = models.FloatField( default=0.00 )
    ecnFees = models.FloatField( default=0.00 )
    
    reportDate = models.DateField( auto_now_add=False )
    
    def save(self, *args, **kwargs): 
        super(MonthlyReport, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return str(self.id)

admin.site.register(Symbol)    
admin.site.register(Security) 
admin.site.register(Report)
admin.site.register(DailyReport)
admin.site.register(MonthlyReport)



# -------------------------------------- Cache API
class cacheReport:
    def __init__(self):
        pass


class cacheReportApi:

    def __init__(self):
        self.server = redis.Redis(SESSION_REDIS_HOST, SESSION_REDIS_PORT)
        
    # cache report by date 
    def cacheReport(self, report):

        key = "report:%s" % str(report.id)
        if self.server.hexists(key,"id"):
            return 
        self.server.hset(key, "symbol", report.symbol)
        self.server.hset(key, "SOD", report.SOD)
        self.server.hset(key, "mark", report.mark)
        self.server.hset(key, "buys", report.buys)
        self.server.hset(key, "buyAve", report.buyAve)
        self.server.hset(key, "sells", report.sells)
        self.server.hset(key, "sellAve", report.sellAve)
        self.server.hset(key, "grossPNL", report.grossPNL)
        self.server.hset(key, "unrealizedPNL", report.unrealizedPNL)
        self.server.hset(key, "fees", report.fees)
        self.server.hset(key, "netPNL", report.netPNL)
        self.server.hset(key, "LMV", report.LMV)
        self.server.hset(key, "SMV", report.SMV)
        self.server.hset(key, "EOD", report.EOD)
        self.server.hset(key, "closing", report.closing)

        self.cacheReportToDate(report, key)
    
    def cacheReportToDate(self, report, key):
        name = "reportDate:%s" % (report.reportDate.strftime("%Y-%m-%d"))
        self.server.sadd(name, key) # add rkey to set
    
    def cacheReportConsistency(self):
        reports = Report.objects.all()
        for report in reports:
            self.cacheReport(report)


class getCacheReportApi:
    
    def __init__(self):
        self.server = redis.Redis(SESSION_REDIS_HOST, SESSION_REDIS_PORT)
    
    def getReportsByDate(self, today):
        name = "reportDate:%s" % (today.strftime("%Y-%m-%d")) 
        keyList = self.server.smembers(name) # get all keys
        
        reports = []
        for key in keyList:
            report = self.server.hgetall(key)
#            r = cacheReport()
#            r.symbol = report['symbol']
#            r.SOD = report['SOD']
#            r.mark = report['mark']
#            r.buys = report['buys']
#            r.buyAve = report['buyAve']
#            r.sells = report['sells']
#            r.sellAve = report['sellAve']
#            r.grossPNL = report['grossPNL']
#            r.unrealizedPNL = report['unrealizedPNL']
#            r.fees = report['fees']
#            r.netPNL = report['netPNL']
#            r.LMV = report['LMV']
#            r.SMV = report['SMV']
#            r.EOD = report['EOD']
#            r.closing = report['closing']
#            reports.append(r)
            reports.append(report)
        
        if len(reports) == 0:
            return None
        
        return reports


class delCacheReportApi:
    
    def __init__(self):
        self.server = redis.Redis(SESSION_REDIS_HOST, SESSION_REDIS_PORT)
    
    def delReportsByDate(self, today):
        name = "reportDate:%s" % (today.strftime("%Y-%m-%d")) 
        keyList = self.server.smembers(name) # get all keys

        for key in keyList:
            self.server.delete(key)
        
        self.server.delete(name)
    
    
    