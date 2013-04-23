'''''
This logic file contains useful methods for importing data from a new account that does not exist in system.
'''''


import os
from admins.models import Firm, Account
from trades.models import Trade, RollTrade
from reports.models import Symbol, Report, DailyReport, MonthlyReport
from datetime import date
import time
from time import strftime
from django.db.models import Q
import csv
from settings import ERROR_LOG


def getTrades(filepath):
    header = True
    file = open(filepath, 'rb')
    
    for row in csv.reader(file.read().splitlines(), delimiter=','):
        if not header:
            try:
                date_str = row[10].split("/")
                today = date(int(date_str[2]), int(date_str[0]), int(date_str[1]))
                
                trade = Trade()
                trade.account = row[0]
                trade.symbol = row[1]
                trade.securityType = row[2]
                trade.side = row[3]
                trade.quantity = row[4]
                trade.price = row[5]
                trade.route = row[6]
                trade.destination = row[7]
                trade.liqFlag = row[9]
                trade.tradeDate = today
                trade.executionId = row[11]
                trade.save() # save into database
            except Exception, e:
                print str(e.message)
                continue
        else:
            header = False
            
    file.close()


def getMarksByDir(path, account):
    
    print "Getting marks and calculating reports..."    
    filelist = os.listdir(path)
    filelist.sort()
    log = open(ERROR_LOG, "a")
    
    for filename in filelist: # each file represent one day
        filepath = os.path.join(path, filename)
        print filepath
        file = open(filepath, 'rb')
        
        for row in csv.reader(file.read().splitlines(), delimiter=','): # all marks in this file
            try:
                symbol = row[19].strip()
                if symbol == "" or symbol == None:
                    continue
                
                closing = round(float(row[12]), 2)
                if closing == 0.0: # invalid symbol
                    continue
                
                type = row[4].strip()
                if type == "B" or type == "J":
                    continue
                
                date_str = row[2].split("/")
                mark_date = date(int(date_str[2]), int(date_str[0]), int(date_str[1]))
                
                try:
                    new_symbol = Symbol.objects.get(Q(symbol=symbol) & Q(symbolDate=mark_date))
                    new_symbol.closing = closing
                    new_symbol.save()
                except Symbol.DoesNotExist:
                    new_symbol = Symbol.objects.create(symbol=symbol, symbolDate=mark_date, closing=closing)
                
            except Exception, e:
                print str(e.message)
                log.write( strftime("%Y-%m-%d %H:%M:%S", time.localtime()) )
                log.write( "\tGet mark price of %s failed: %s\n" % (symbol, str(e.message)) )
                continue
            
        file.close()
        getReportByDate(mark_date, account)
    
    log.close()
    print "Done"
    return True


def getSupplement(filepath, mark_date, account):
    
    print "Getting marks and calculating reports..."    
    
    print filepath + " " + str(mark_date)
    file = open(filepath, 'rb')
    log = open(ERROR_LOG, "a")
        
    for row in csv.reader(file.read().splitlines(), delimiter=','): 
        try:
            # please modify row number here according to the supplement file format
            symbol = row[5].strip()
            if symbol == "" or symbol == None:
                continue
            
            if row[8] != "":
                continue
            
            closing = round(float(row[12]), 2)
            if closing == 0.0: # invalid symbol
                continue

            try:
                new_symbol = Symbol.objects.get(Q(symbol=symbol) & Q(symbolDate=mark_date))
                new_symbol.closing = closing
                new_symbol.save()
            except Symbol.DoesNotExist:
                new_symbol = Symbol.objects.create(symbol=symbol, symbolDate=mark_date, closing=closing)
                
        except Exception, e:
            print str(e.message)
            log.write( strftime("%Y-%m-%d %H:%M:%S", time.localtime()) )
            log.write( "\tGet mark price of %s failed: %s\n" % (symbol, str(e.message)) )
            continue
            
    getReportByDate(mark_date, account)
    
    log.close()
    file.close()
    print "Done"
    return True


def refreshReports(today, account):
    log = open(ERROR_LOG, "a")
    
    try: # get latest report date
        last_date =  Report.objects.filter( Q(reportDate__lt=today) & Q(account=account) ).order_by("-reportDate")[0].reportDate
        old_reports = Report.objects.filter( Q(reportDate=last_date) & Q(account=account) )
        for old_report in old_reports:
            old_report.pk = None
            old_report.save() # clone a new one
            new_report = old_report  
            new_report.buys = 0 
            new_report.sells = 0
            new_report.buyAve = 0.0 
            new_report.sellAve = 0.0
            new_report.commission = 0.0
            new_report.clearanceFees = 0.0
            new_report.secFees = 0.0
            new_report.SOD = new_report.EOD 
            new_report.mark = new_report.closing
            new_report.reportDate = today
            new_report.save()
                
    except Exception, e: # old report does not exist
        print str(e.message)
        log.write( strftime("%Y-%m-%d %H:%M:%S", time.localtime()) )
        log.write("\tRefresh reports Failed: %s\n" % str(e.message))
    
    log.close()


def newReport(account, symbol, today):
    
    try:
        new_report = Report.objects.get(Q(account=account) & Q(symbol=symbol) & Q(reportDate=today))
            
    except Report.DoesNotExist: # today's new does not exist  
        new_report = Report()
        new_report.account = account
        new_report.symbol = symbol      
        new_report.reportDate = today
        new_report.save()
        #new_report = Report.objects.create(symbol=symbol, reportDate=today)
        
    return new_report
    

###########################################################
# calcluate pnls for each report
def getPNLs(report_date, account):
    log = open(ERROR_LOG, "a")
    report_list = Report.objects.filter( Q(reportDate = report_date) & Q(account=account) )
    for report in report_list: 
        symbol = report.symbol
        mark = report.mark # mark to market value
        closing = report.closing # closing price today
        SOD = report.SOD # start of day
        buys = report.buys
        buyAve = report.buyAve
        sells = report.sells
        sellAve = report.sellAve
        
        # check closing 
        try:
            symbol_mark = Symbol.objects.get(Q(symbol=symbol) & Q(symbolDate=report_date))
            closing = symbol_mark.closing
            report.closing = closing
        except: 
            log.write( strftime("%Y-%m-%d %H:%M:%S", time.localtime()) )
            log.write("\tWarnning: Cannot get closing price of %s.\n" % symbol)
        
        if mark == 0: # check mark
            try:
                symbol_mark = Symbol.objects.filter( Q(symbol=symbol) & Q(symbolDate__lt=report_date) ).order_by("-reportDate")[0]
                mark = symbol_mark.closing
                report.mark = mark
            except: # ignore this right now, TODO: log this error
                log.write( strftime("%Y-%m-%d %H:%M:%S", time.localtime()) )
                log.write("\tWarnning: Cannot get mark price of %s.\n" % symbol) 
        
        # check SOD
        if SOD == 0:
            try:
                last_report = Report.objects.filter( Q(symbol=symbol) & Q(reportDate__lt=report_date) & Q(account=account) ).order_by("-reportDate")[0]
                SOD = last_report.EOD
                report.SOD = SOD
            except:
                pass
        
        # discard useless report
        if SOD == 0 and buys == 0 and sells == 0:
            report.delete()
            continue
        
        # calculate EOD
        EOD = SOD + buys - sells

        if SOD > 0:
            total = buys * buyAve + mark * SOD
            buys += SOD
            buyAve = total / buys
        elif SOD < 0:
            total = sells * sellAve + mark * (-SOD)
            sells -= SOD
            sellAve = total / sells
            
        if buys >= sells:
            common = sells
        else:
            common = buys
        
        # gross PNL    
        grossPNL = common * (sellAve - buyAve)
        report.grossPNL = grossPNL
        
        # left shares
        buys -= common
        sells -= common
        unrealizedPNL = (closing - buyAve) * buys + (sellAve - closing) * sells
        report.unrealizedPNL = unrealizedPNL

        # net PNL
        report.netPNL = grossPNL + unrealizedPNL #- report.secFees - report.clearanceFees - report.commission
        
        # LMV and SMV
        if EOD >=0:
            report.LMV = EOD * closing
            report.SMV = 0
        else:
            report.LMV = 0
            report.SMV = EOD * closing
        
        report.EOD = EOD   
        report.save()
    
    log.close()
        
###########################################################
# calcluate fees for trades
def getRollTrades(today, account):
    trades = Trade.objects.filter(Q(tradeDate=today) & Q(account=account))
    for trade in trades:
        try:
            
            # TODO: add more fields here to roll
            # TempKey = bo.account + "," + bo.bs + "," + bo.shortSign + "," + bo.symbol + "," + bo.extPrice + "," 
            #           + bo.service + "," + bo.execBrkr + "," + bo.delBrkr + "," + bo.delBrkrNum 
            #           + "," + bo.blotter + "," + bo.exchange;
            
            rtrade = RollTrade.objects.get(Q(account=trade.account) & Q(symbol=trade.symbol) & 
                                           Q(side=trade.side) & Q(price=trade.price) & 
                                           #Q(route=trade.route) & Q(destination=trade.destination) & Q(liqFlag=trade.liqFlag) &    
                                           Q(tradeDate=trade.tradeDate) )
            rtrade.quantity += trade.quantity
            rtrade.save()
        except RollTrade.DoesNotExist:
            RollTrade.objects.create(account=trade.account, symbol=trade.symbol, side=trade.side, 
                                     price=trade.price, quantity=trade.quantity, 
                                     #route=trade.route, destination=trade.destination, liqFlag=trade.liqFlag,
                                     tradeDate=trade.tradeDate)
    
    return RollTrade.objects.filter(tradeDate=today)

def fe():
    #s = date(2013, 1, 3) 
    
    ms = MonthlyReport.objects.all()
    for m in ms:
        m.secFees = 0
        m.clearanceFees = 0
        m.brokerCommission = 0
        m.commission = 0
        m.ecnFees = 0
        m.save()
    
    ds = DailyReport.objects.all().order_by("reportDate") #filter(reportDate__gte = s)
    for d in ds:
        d.secFees = 0
        d.clearanceFees = 0
        d.brokerCommission = 0
        d.commission = 0
        d.ecnFees = 0
        d.save()
        today = d.reportDate
        getFees(today)

        
def getFees(today, account):
    log = open(ERROR_LOG, "a")
    firm = Firm.objects.all()[0]
    secRate = firm.secFee
    
    reports = Report.objects.filter( Q(reportDate=today) & Q(account=account) )
    for report in reports:
        report.secFees = 0
        report.clearanceFees = 0
        report.brokerCommission = 0
        report.commission = 0
        report.ecnFees = 0
        report.save()
    
    # clearance fees
    # after 2012-11-20, should do roll up
    if today <= date(2012, 11, 20):
        rollTrades = Trade.objects.filter( Q(tradeDate = today) & Q(account=account) )
    else:
        rollTrades = getRollTrades(today, account)
        
    # SEC fees and commission for each trade
    for trade in rollTrades:
        report = Report.objects.get( Q(account=trade.account) & Q(symbol=trade.symbol) & Q(reportDate=today) )

        # sec fees
        if trade.side != "BUY":
            secFees = trade.price * trade.quantity * secRate
            rsecFees = round(secFees, 2)
            
            if secFees > rsecFees:
                secFees = rsecFees + 0.01
            else:
                secFees = rsecFees
        else:
            secFees = 0

#        ### broker commission
#        try:
#            broker = Broker.objects.get(name=trade.broker)
#            brokerCommission = broker.commission * trade.quantity
#        except Broker.DoesNotExist:
#            brokerCommission = 0
#            log.write( strftime("%Y-%m-%d %H:%M:%S", time.localtime()) )
#            log.write("\tWarnning: Cannot get broker (commission) %s.\n" % trade.broker) 
        

        ### clearance fees         
        clearance = trade.quantity * 0.0001 # TODO: make this argument as a member of firm
        clearance = round(clearance, 2)
        
        if clearance > 3.00:
            clearance = 3.00
        elif clearance < 0.01:
            clearance = 0.01
        
        report.clearanceFees += clearance
#        report.brokerCommission += brokerCommission
        report.commission += clearance #+ brokerCommission
        report.secFees += secFees 
        report.save()
    
    
    # ECN fees
    '''
    if today > date(2013, 1, 2):
        trades = Trade.objects.filter(tradeDate = today)
        for trade in trades:
            report = Report.objects.get(Q(account=trade.account) & Q(symbol=trade.symbol) & Q(reportDate=today) )
        
            # ecn fees
            ecnFees = 0.0
            try:
                security = Security.objects.get(symbol = trade.symbol)
                market = security.market
                if market == "U":
                    primary = "ALL"
                elif market == "AMEX":
                    primary = "AMEX"
                elif market == "NASDAQ":
                    primary = "OTC"
                else: # NYSE, ARCA
                    primary = "NYSE"
                route = Route.objects.get( Q(routeId = trade.destination) & Q(flag = trade.liqFlag) & Q(primaryExchange = primary) )
                if route.feeType == "FLAT PER SHARE":
                    ecnFees = route.rebateCharge * trade.quantity
                    #print ecnFees
            except Exception, e:
                print str(e.message)
                log.write( strftime("%Y-%m-%d %H:%M:%S", time.localtime()) )
                log.write("\tWarnning: Cannot get route (ecn fees) %s | %s.\n" % (trade.destination, trade.liqFlag)) 
                pass
        
            report.ecnFees += ecnFees
            report.save()
    '''

    
    if today > date(2012, 11, 20):
        rollTrades.delete()
    log.close()


# get summary data of reports with a specific date
def getDailyReport(report_date, account):
    report_list = Report.objects.filter( Q(reportDate = report_date) & Q(account=account) )
    
    if report_list.count() == 0:
        return 
    
    for report in report_list:
        try:
            daily_report = DailyReport.objects.get( Q(account = report.account) & Q(reportDate = report_date) )
        except DailyReport.DoesNotExist:
            daily_report = DailyReport.objects.create(account = report.account, reportDate = report_date)
        daily_report.SOD += report.SOD
        daily_report.buys += report.buys
        daily_report.sells += report.sells
        daily_report.grossPNL += report.grossPNL
        daily_report.unrealizedPNL += report.unrealizedPNL
        daily_report.secFees += report.secFees
        daily_report.clearanceFees += report.clearanceFees
        daily_report.brokerCommission += report.brokerCommission
        daily_report.commission += report.commission
        daily_report.ecnFees += report.ecnFees
        daily_report.netPNL += report.netPNL
        daily_report.LMV += report.LMV
        daily_report.SMV += report.SMV
        daily_report.EOD += report.EOD
        daily_report.save()
    
    daily_reports = DailyReport.objects.filter( Q(reportDate = report_date) & Q(account=account))
    for daily_report in daily_reports:
        getMonthlyReport(daily_report)
        getAccountSummary(daily_report)
        
# add daily data to account summary
def getAccountSummary(daily_report):
    account = Account.objects.get(account=daily_report.account)
    account.grossPNL += daily_report.grossPNL
    account.unrealizedPNL += daily_report.unrealizedPNL
    account.secFees += daily_report.secFees
    account.commission += daily_report.commission
    account.ecnFees += daily_report.ecnFees
    account.save()


# get summary data of reports for a specific month
def getMonthlyReport(daily_report):
    year = daily_report.reportDate.year
    month = daily_report.reportDate.month
    #today = date.today()
    
    try:
        monthly_report = MonthlyReport.objects.get(Q(account = daily_report.account) & Q(reportDate__year = year) & Q(reportDate__month = month))
        monthly_report.buys += daily_report.buys
        monthly_report.sells += daily_report.sells
        monthly_report.grossPNL += daily_report.grossPNL
        monthly_report.unrealizedPNL += daily_report.unrealizedPNL
        monthly_report.secFees += daily_report.secFees
        monthly_report.clearanceFees += daily_report.clearanceFees
        monthly_report.brokerCommission += daily_report.brokerCommission
        monthly_report.commission += daily_report.commission
        monthly_report.ecnFees += daily_report.ecnFees
        monthly_report.netPNL += daily_report.netPNL
        monthly_report.save()
        
    except MonthlyReport.DoesNotExist:
        monthly_report = MonthlyReport(account = daily_report.account, reportDate = daily_report.reportDate) # create a new for this month
        dreports = DailyReport.objects.filter(Q(account = daily_report.account) & Q(reportDate__year = year) & Q(reportDate__month = month))
        for dr in dreports:
            monthly_report.buys += dr.buys
            monthly_report.sells += dr.sells
            monthly_report.grossPNL += dr.grossPNL
            monthly_report.unrealizedPNL += dr.unrealizedPNL
            monthly_report.secFees += dr.secFees
            monthly_report.clearanceFees += dr.clearanceFees
            monthly_report.brokerCommission += dr.brokerCommission
            monthly_report.commission += dr.commission
            monthly_report.ecnFees += dr.ecnFees
            monthly_report.netPNL += dr.netPNL
        monthly_report.save()
        
        
def getReportByDate(today, account):
    log = open(ERROR_LOG, "a")
    
    refreshReports(today, account) # create new reports for those symbols have reports last trade date
    
    trades = Trade.objects.filter( Q(tradeDate = today) & Q(account=account) ) 
    
    for trade in trades:
        new_report = newReport(trade.account, trade.symbol, today) # get report
                
        # update report
        if trade.side == "BUY":
            total = new_report.buys * new_report.buyAve
            total += trade.quantity * trade.price # new total
            new_report.buys += trade.quantity # new buys
            new_report.buyAve = total / new_report.buys # new buy ave
            
        elif trade.side == "SEL" or trade.side == "SS":
            total = new_report.sells * new_report.sellAve
            total += trade.quantity * trade.price # new total
            new_report.sells += trade.quantity # new sells
            new_report.sellAve = total / new_report.sells # new sell ave
            
        else:
            print "Error: Invalid Side."
            continue
        
        new_report.save() # save result
        
    getFees(today, account) # calculate fees
    getPNLs(today, account) # calculate PNLS
    getDailyReport(today, account) # get daily summary report
    # now delete marks lt today, we do not need them anymore
    Symbol.objects.filter( symbolDate__lt=today ).delete() 
    
    log.write( strftime("%Y-%m-%d %H:%M:%S", time.localtime()) )
    log.write("\tReports calculating done.\n")
    log.close()
    
            
            
            
            
