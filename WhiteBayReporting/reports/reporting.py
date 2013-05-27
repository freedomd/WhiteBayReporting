'''
Created on May 1, 2013

@author: ZhiZeng
'''
import os
from admins.models import Firm, Broker, Route, Account
from trades.models import Trade, RollTrade
from reports.models import Security, Symbol, Report, DailyReport, MonthlyReport
from datetime import date
import time
from time import strftime
from django.db.models import Q
import paramiko
import csv
from settings import ERROR_LOG
from settings import DATASOURCE, DATASOURCE_USERNAME, DATASOURCE_PASSWORD
from settings import TRADE_PATH, MARK_PATH, TEMP_PATH
from settings import TRADE_FILE_NAME, MARK_FILE_NAME
import string
    
    
def getSupplementByDate(path, mark_date):
    print "Getting supplement marks and calculating reports..."
    filelist = os.listdir(path)
    filelist.sort()
    
    #read all the mark files for mark_date
    for filename in filelist:
        if filename == ".DS_Store":
            continue
        print filename
        filepath = os.path.join(path, filename)
        #print filepath
        file = open(filepath, 'rb')
        log = open(ERROR_LOG, "a")
        header = True
        
        #read one mark file
        for row in csv.reader(file.read().splitlines(), delimiter=','): # all marks in this file
            if not header:               
                try:      
                    #symbol
                    type = row[6].strip()
                    if type == "SCO":
                        #expiration date
                        exp_date = row[8].split("/")
                        if len(exp_date[0]) == 1:
                            month = "0" + exp_date[0]
                        else:
                            month = exp_date[0]
                        if len(exp_date[1]) == 1:
                            day = "0" + exp_date[1]
                        else:
                            day = exp_date[1]
                        year = exp_date[2]
                        date_str = year + month + day
                        
                        #strike
                        strike = float(row[9])
                        strike_str = str(int(strike * 1000))
                        while (len(strike_str) < 8):
                            strike_str = "0" + strike_str
                        
                        symbol = row[5].strip() + "   " + date_str + "C" + strike_str
                        #print symbol
                    elif type == "SPO":
                        #expiration date
                        exp_date = row[8].split("/")
                        if len(exp_date[0]) == 1:
                            month = "0" + exp_date[0]
                        else:
                            month = exp_date[0]
                        if len(exp_date[1]) == 1:
                            day = "0" + exp_date[1]
                        else:
                            day = exp_date[1]
                        year = exp_date[2]
                        date_str = year + month + day
                        
                        #strike
                        strike = float(row[9])
                        strike_str = str(int(strike * 1000))
                        while (len(strike_str) < 8):
                            strike_str = "0" + strike_str
                        
                        symbol = row[5].strip() + "   " + date_str + "P" + strike_str
                        #print symbol
                    else:     
                        symbol = row[5].strip()
                        #print symbol
                    if symbol == "" or symbol == None:
                        continue
                        
                    closing = round(float(row[17]), 2)
                    #print closing
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
                    log.write( "\tGet mark price of %s from %s failed: %s\n" % (symbol, filepath, str(e.message)) )
                    continue
            else:
                header = False
        file.close()
        log.close()
    
    if mark_date:
        print "Start calculating report..."
        getReportByDate(mark_date)
    
    print "Done"
    return True
    

    
def getMarksByDir(path):
    
    print "Getting marks and calculating reports..."    
    filelist = os.listdir(path)
    filelist.sort()
    log = open(ERROR_LOG, "a")
    
    for filename in filelist: # each file represent one day
        if filename == ".DS_Store":
            continue
        filepath = os.path.join(path, filename)
        print filepath
        file = open(filepath, 'rb')
        mark_date = None
        
        for row in csv.reader(file.read().splitlines(), delimiter=','): # all marks in this file
            try:
                symbol = row[19].strip()
                if symbol == "" or symbol == None:
                    continue
                                
                closing = float(row[12])
                if closing == 0.0: # invalid symbol
                    continue
                
#                 type = row[4].strip()
#                 if type == "B" or type == "J":
#                     continue
                
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
                log.write( "\tGet mark price from %s failed: %s\n" % (filename, str(e.message)) )
                continue
            
        file.close()
        if mark_date:
            getReportByDate(mark_date)
    
    log.close()
    print "Done"
    return True

def refreshReports(today):
    log = open(ERROR_LOG, "a")
    
    try: # get latest report date
        last_date =  Report.objects.filter( Q(reportDate__lt=today) ).order_by("-reportDate")[0].reportDate
        old_reports = Report.objects.filter( Q(reportDate=last_date) )
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
        mainAccount = account[:5]
        new_report = Report.objects.get(Q(account=mainAccount) & Q(symbol=symbol) & Q(reportDate=today))
            
    except Report.DoesNotExist: # today's new does not exist  
        new_report = Report()
        new_report.account = mainAccount
        new_report.symbol = symbol      
        new_report.reportDate = today
        new_report.save()
        #new_report = Report.objects.create(symbol=symbol, reportDate=today)
        
    return new_report    

def getRollTrades(today):
    trades = Trade.objects.filter(tradeDate=today)
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

###########################################################
# calcluate pnls for each report
def getPNLs(report_date):
    log = open(ERROR_LOG, "a")
    report_list = Report.objects.filter( Q(reportDate = report_date) )
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
        report.netPNL = grossPNL + unrealizedPNL# - report.secFees - report.clearanceFees - report.commission
        
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

def getReportByDate(today):
    log = open(ERROR_LOG, "a")
    
    refreshReports(today) # create new reports for those symbols have reports last trade date
    
    # after 2012-11-20, should do roll up the trades
    if today <= date(2012, 11, 20):
        rollTrades = Trade.objects.filter(tradeDate = today)
    else:
        rollTrades = getRollTrades(today)
    
    for rtrade in rollTrades:
        new_report = newReport(rtrade.account, rtrade.symbol, today)
            # buy and sell
        if rtrade.side == "BUY":
            total = new_report.buys * new_report.buyAve
            total += rtrade.quantity * rtrade.price # new total
            new_report.buys += rtrade.quantity # new buys
            new_report.buyAve = total / new_report.buys # new buy ave
                
        elif rtrade.side == "SEL" or rtrade.side == "SS":
            total = new_report.sells * new_report.sellAve
            total += rtrade.quantity * rtrade.price # new total
            new_report.sells += rtrade.quantity # new sells
            new_report.sellAve = total / new_report.sells # new sell ave
                
        else:
            print "Error: Invalid Side."
            continue
            
            
        #Fees
        firm = Firm.objects.all()[0]
        secRate = firm.secFee            
        ## sec fees
        if rtrade.side != "BUY":
            secFees = rtrade.price * rtrade.quantity * secRate
            rsecFees = round(secFees, 2)
                
            if secFees > rsecFees:
                secFees = rsecFees + 0.01
            else:
                secFees = rsecFees
        else:
            secFees = 0
        ## broker commission, not implemented yet
        ## clearance fee
        clearance = rtrade.quantity * 0.0001 # TODO: make this argument as a member of firm
        clearance = round(clearance, 2)            
        if clearance > 3.00:
            clearance = 3.00
        elif clearance < 0.01:
            clearance = 0.01
        ## update report
        new_report.clearanceFees += clearance
        # new_report.brokerCommission += brokerCommission
        new_report.commission += clearance #+ brokerCommission
        new_report.secFees += secFees
        new_report.save()            
    
    #getPNLs(today)
    getDailyReport(today)
    
    # now delete marks lt today, we do not need them anymore
    Symbol.objects.filter( symbolDate__lt=today ).delete() 
    
    log.write( strftime("%Y-%m-%d %H:%M:%S", time.localtime()) )
    log.write("\tReports calculating done.\n")
    log.close()
    

# get summary data of reports with a specific date
def getDailyReport(report_date):
    log = open(ERROR_LOG, "a")
    report_list = Report.objects.filter( Q(reportDate = report_date) )
    
    for report in report_list: 
        # calculate the PNL first
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
        report.netPNL = grossPNL + unrealizedPNL# - report.secFees - report.clearanceFees - report.commission
        
        # LMV and SMV
        if EOD >=0:
            report.LMV = EOD * closing
            report.SMV = 0
        else:
            report.LMV = 0
            report.SMV = EOD * closing
        
        report.EOD = EOD   
        report.save() 
    
        # get daily report
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
    
    daily_reports = DailyReport.objects.filter(reportDate = report_date)
    for daily_report in daily_reports:
        getMonthlyReport(daily_report)
        getAccountSummary(daily_report)

# add daily data to account summary
def getAccountSummary(daily_report):
    try:
        account = Account.objects.get(account=daily_report.account)
        account.grossPNL += daily_report.grossPNL
        account.unrealizedPNL += daily_report.unrealizedPNL
        account.secFees += daily_report.secFees
        account.commission += daily_report.commission
        account.ecnFees += daily_report.ecnFees
        account.netPNL += daily_report.netPNL
        account.save()
    except Account.DoesNotExist:
        report_list = DailyReport.objects.filter(account = daily_report.account)
        account = Account.objects.create(account=daily_report.account)
        for report in report_list:
            account.grossPNL += report.grossPNL
            account.unrealizedPNL += report.unrealizedPNL
            account.secFees += report.secFees
            account.commission += report.commission
            account.ecnFees += report.ecnFees
            account.netPNL += report.netPNL
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
        
        
        
#get trades by file
def getTrades(filepath):
    print "Getting trades record from "  + filepath
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
    
def getTradesByDir(path):
    print "Getting trades record from files..."    
    filelist = os.listdir(path)
    filelist.sort()
    log = open(ERROR_LOG, "a")
    
    for filename in filelist: # each file represent one day
        if string.find(filename, ".DS_Store"):
            continue
        filepath = os.path.join(path, filename)
        print filepath
        file = open(filepath, 'rb')
        header = True
        for row in csv.reader(file.read().splitlines(), delimiter=','): # all marks in this file
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
                    log.write( strftime("%Y-%m-%d %H:%M:%S", time.localtime()) )
                    log.write( "\tGet trades file from %s failed: %s\n" % (filename, str(e.message)) )
                    continue
            else:
                header = False
        file.close()    
    log.close()
    print "Done"
    return True

#import the transfer activities as trades
def getTransferAsTradesByDir(path):
    print "Getting transfer record from files..."    
    filelist = os.listdir(path)
    filelist.sort()
    log = open(ERROR_LOG, "a")
    print str(len(filelist)) + ' files'
    
    for filename in filelist: # each file represent one day
        #print filename
        if filename == ".DS_Store":
            continue
        filepath = os.path.join(path, filename)
        print filepath
        file = open(filepath, 'rb')
        header = True
        for row in csv.reader(file.read().splitlines(), delimiter=','): # all marks in this file
            #print header
            if not header:
                try:
                    date_str = row[5]
                    today = date(int(date_str[0:4]), int(date_str[4:6]), int(date_str[6:]))
                    #print today
                    
                    trade = Trade()
                    trade.account = row[2]
                    trade.symbol = row[8]
                    sec = row[4]
                    if sec == "OPTION":
                        trade.securityType = "OPT"
                    else:
                        trade.securityType = "SEC"
                    
                    side = row[19]
                    if side == "BUY" or side == "BUY OPEN":
                        trade.side = "BUY"
                    else:
                        trade.side = "SEL"
                    
                    trade.quantity = int(row[20].split('.')[0].replace(',',''))
                    
                    trade.price = float(row[21])
                    trade.tradeDate = today
                    trade.save() # save into database
                except Exception, e:
                    print str(e.message)
                    log.write( strftime("%Y-%m-%d %H:%M:%S", time.localtime()) )
                    log.write( "\tGet trade %s from transfer file %s failed: %s\n" % (trade.symbol, filename, str(e.message)) )
                    continue
            else:
                header = False
        file.close()    
    log.close()
    print "Done"
    return True    