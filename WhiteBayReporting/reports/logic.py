import os
from admins.models import Firm, Broker
from trades.models import Trade, RollTrade
from reports.models import Symbol, Report, DailyReport, MonthlyReport
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


#############################################
# get data files
def getMarkFile(file_date):
    # create ssh tunnel to read files from ssh server
    try:
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=DATASOURCE, username=DATASOURCE_USERNAME, password=DATASOURCE_PASSWORD)
        ftp = ssh.open_sftp() 
    except Exception, e:
        print str(e.message)
        log = open(ERROR_LOG, "a")
        log.write( strftime("%Y-%m-%d %H:%M:%S", time.localtime()) )
        log.write("\tCannot connect to datasource: %s\n" % str(e.message))
        log.close()
        return None
        
    try:
#        filename = MARK_FILE_NAME + file_date.strftime('%Y%m%d') + ".CSV"
        filename = "WSB858TJ.CST_20130220.CSV"
        filepath = MARK_PATH + filename
        temppath = TEMP_PATH + filename
        ftp.get(filepath, temppath) 
        return temppath # return file path
            
    except Exception, e:
        print str(e.message)
        log = open(ERROR_LOG, "a")
        log.write( strftime("%Y-%m-%d %H:%M:%S", time.localtime()) )
        log.write("\tGet mark file failed: %s\n" % str(e.message))
        log.close()
        return None

def getTradeFile(file_date):
    # create ssh tunnel to read files from ssh server
    try:
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=DATASOURCE, username=DATASOURCE_USERNAME, password=DATASOURCE_PASSWORD)
        ftp = ssh.open_sftp() 
    except Exception, e:
        print str(e.message)
        log = open(ERROR_LOG, "a")
        log.write( strftime("%Y-%m-%d %H:%M:%S", time.localtime()) )
        log.write("\tCannot connect to datasource: %s\n" % str(e.message))
        log.close()
        return None
    
    try:
#        today = date.today()
#        filename = TRADE_FILE_NAME + file_date.strftime('%Y_%m_%d') + ".csv"
        filename = "WBPT_LiquidEOD_2013_02_19.csv"
        filepath = TRADE_PATH + filename
        temppath = TEMP_PATH + filename
        ftp.get(filepath, temppath) 
        return temppath # return file path
            
    except Exception, e:
        print str(e.message)
        log = open(ERROR_LOG, "a")
        log.write( strftime("%Y-%m-%d %H:%M:%S", time.localtime()) )
        log.write("\tGet trade file failed: %s\n" % str(e.message))
        log.close()
        return None
    
#############################################
# save data into database

# this is a test function
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
            

def getMarks(today):
    
#    filepath = getMarkFile(today)
#    if filepath == None:
#        return False
    print "Getting marks..."
    filepath = './temp/WSB858TJ.CST425PO_20130217.CSV'
    log = open(ERROR_LOG, "a")
    
    file = open(filepath, 'rb')
    for row in csv.reader(file.read().splitlines(), delimiter=','):
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
                new_symbol = Symbol.objects.get(Q(symbol=symbol) & Q(symbolDatet=mark_date))
                new_symbol.closing = closing
                new_symbol.save()
            except Symbol.DoesNotExist:
                new_symbol = Symbol.objects.create(symbol=symbol, symbolDate=mark_date, closing=closing)

        except Exception, e:
            print str(e.message)
            log.write( strftime("%Y-%m-%d %H:%M:%S", time.localtime()) )
            log.write( "\tGet mark price of %s failed: %s\n" % (symbol, str(e.message)) )
            continue
    
    #os.remove(filepath) # remove temporary file
    file.close()
    log.close()
    print "Done"
    return True


def getMarksByDir(path):
    
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
        getReportByDate(mark_date)
    
    log.close()
    print "Done"
    return True

def getSupplement(filepath, mark_date):
    
    print "Getting marks and calculating reports..."    
    
    print filepath + " " + str(mark_date)
    file = open(filepath, 'rb')
    log = open(ERROR_LOG, "a")
        
    for row in csv.reader(file.read().splitlines(), delimiter=','): # all marks in this file
        try:
            symbol = row[5].strip()
            if symbol == "" or symbol == None:
                continue
                
            closing = round(float(row[13]), 2)
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
            
    getReportByDate(mark_date)
    
    log.close()
    file.close()
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


def newReport(symbol, today):
    
    try:
        new_report = Report.objects.get(Q(symbol=symbol) & Q(reportDate=today))
            
    except Report.DoesNotExist: # today's new does not exist  
        new_report = Report()
        new_report.symbol = symbol      
        new_report.reportDate = today
        new_report.save()
        #new_report = Report.objects.create(symbol=symbol, reportDate=today)
        
    return new_report
    

def getReport(today):
    
#    filepath = getTradeFile(today)
#    if filepath == None:
#        return False
    print "Getting reports..."
    filepath = './temp/WBPT_LiquidEOD_2013_01_07.csv'
    file = open(filepath, 'rb')
    log = open(ERROR_LOG, "a")
    
    refreshReports(today) # create 
    
    header = True
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
                
                new_report = newReport(trade.symbol, today) # get report
                
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
                
                trade.save() # save into database
                new_report.save() # save result
                
            except Exception, e:
                print str(e.message)
                log.write( strftime("%Y-%m-%d %H:%M:%S", time.localtime()) )
                log.write("\tGet report Failed: %s\n" % str(e.message))
                continue
        else:
            header = False
    
    print "Done"
    print "Calculating PNLS and summary reports..."
    
    getFees(today) # calculate fees
    getPNLs(today) # calculate PNLS
    getDailyReport(today) # get daily summary report
    # now delete marks lt today, we do not need them anymore
    Symbol.objects.filter( symbolDate__lt=today ).delete() 
    #os.remove(filepath) # remove temporary file
    
    log.write( strftime("%Y-%m-%d %H:%M:%S", time.localtime()) )
    log.write("\tReports calculating done.")
    file.close()
    log.close()
    return True


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
                last_report = Report.objects.filter( Q(symbol=symbol) & Q(reportDate__lt=report_date) ).order_by("-reportDate")[0]
                SOD = last_report.EOD
                report.SOD = SOD
            except:
                pass
        
        # discard useless report
        if SOD == 0 and buys == 0 and sells == 0:
            report.delete()
        
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
        report.netPNL = grossPNL + unrealizedPNL - report.secFees - report.clearanceFees - report.commission
        
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
def getRollTrades(today):
    trades = Trade.objects.filter(tradeDate=today)
    for trade in trades:
        try:
            rtrade = RollTrade.objects.get( Q(symbol=trade.symbol) & Q(side=trade.side) & Q(price=trade.price) & Q(tradeDate=trade.tradeDate) )
            rtrade.quantity += trade.quantity
            rtrade.save()
        except RollTrade.DoesNotExist:
            RollTrade.objects.create(symbol=trade.symbol, side=trade.side, price=trade.price, quantity=trade.quantity, tradeDate=trade.tradeDate)
    
    return RollTrade.objects.filter(tradeDate=today)

def fe():
    s = date(2012, 11, 21) 
        
    ds = DailyReport.objects.filter(reportDate__gte = s)
    for d in ds:
        today = d.reportDate
        getFees(today)
        
    ms = MonthlyReport.objects.all()
    for m in ms:
        today = m.reportDate
        m.secFees = 0
        m.clearanceFees = 0
        ds = DailyReport.objects.filter(Q(reportDate__year=today.year) & Q(reportDate__month=today.month))
        
def getFees(today):
    log = open(ERROR_LOG, "a")
    firm = Firm.objects.all()[0]
    secRate = firm.secFee
    
    reports = Report.objects.filter(reportDate=today)
    for report in reports:
        report.secFees = 0
        report.clearanceFees = 0
        report.save()
    
    # clearance fees
    # after 2012-11-20, should do roll up
    trades = getRollTrades(today)
    for trade in trades:
        report = Report.objects.get( Q(symbol=trade.symbol) & Q(reportDate=today) )
        clearance = trade.quantity * 0.0001
        clearance = round(clearance, 2)
        
        if clearance > 3.00:
            report.clearanceFees += 3.00
        elif clearance < 0.01:
            report.clearanceFees += 0.01
        else:
            report.clearanceFees += clearance
        report.save()
    
    
    # SEC fees and commission for each trade
    for trade in trades:
        if trade.side != "BUY":
            secFees = trade.price * trade.quantity * secRate
            rsecFees = round(secFees, 2)
            
            if secFees > rsecFees:
                secFees = rsecFees + 0.01
            else:
                secFees = rsecFees
        else:
            secFees = 0
            
#        try:
#            broker = Broker.objects.get(name=trade.broker)
#            trade.commission = broker.commission * trade.quantity
#        except Broker.DoesNotExist:
#            trade.commission = 0
#            log.write( strftime("%Y-%m-%d %H:%M:%S", time.localtime()) )
#            log.write("\tWarnning: Cannot get broker (commission) %s.\n" % trade.broker) 
        
        #trade.save()
        
        report = Report.objects.get( Q(symbol=trade.symbol) & Q(reportDate=today) )
        report.secFees += secFees #trade.secFees
        #report.commission += trade.commission
        report.save()
    
    
    # TODO: delete this part
    dreport = DailyReport.objects.get(reportDate=today)
    dreport.secFees = 0
    dreport.clearanceFees = 0
    reports = Report.objects.filter(reportDate=today)
    for report in reports:
        dreport.secFees += report.secFees
        dreport.clearanceFees += report.clearanceFees
        #dreport.commission += report.commission
    dreport.save()
    
    
#    mreport = MonthlyReport.objects.get( Q(reportDate__year=today.year) & Q(reportDate__month=today.month) )
#    mreport.secFees += dreport.secFees
#    mreport.clearanceFees += dreport.clearanceFees
#    #mreport.commission += dreport.commission
#    mreport.save()
#    # TODO: delete this part
    
    trades.delete()
    
    log.close()
    
  
# get summary data of reports with a specific date
def getDailyReport(report_date):
    daily_report = DailyReport()
    report_list = Report.objects.filter( Q(reportDate = report_date) )
    
    if report_list.count() == 0:
        return 
    
    for report in report_list:
        daily_report.SOD += report.SOD
        daily_report.buys += report.buys
        daily_report.sells += report.sells
        daily_report.grossPNL += report.grossPNL
        daily_report.unrealizedPNL += report.unrealizedPNL
        daily_report.secFees += report.secFees
        daily_report.clearanceFees += report.clearanceFees
        daily_report.commission += report.commission
        daily_report.netPNL += report.netPNL
        daily_report.LMV += report.LMV
        daily_report.SMV += report.SMV
        daily_report.EOD += report.EOD
    daily_report.reportDate = report_date
    daily_report.save()
    
    getMonthlyReport(daily_report)


# get summary data of reports for a specific month
def getMonthlyReport(daily_report):
    year = daily_report.reportDate.year
    month = daily_report.reportDate.month
    #today = date.today()
    
    try:
        monthly_report = MonthlyReport.objects.get(Q(reportDate__year = year) & Q(reportDate__month = month))
        monthly_report.buys += daily_report.buys
        monthly_report.sells += daily_report.sells
        monthly_report.grossPNL += daily_report.grossPNL
        monthly_report.unrealizedPNL += daily_report.unrealizedPNL
        monthly_report.secFees += daily_report.secFees
        monthly_report.clearanceFees += daily_report.clearanceFees
        monthly_report.commission += daily_report.commission
        monthly_report.netPNL += daily_report.netPNL
        monthly_report.save()
        
    except MonthlyReport.DoesNotExist:
        monthly_report = MonthlyReport(reportDate = daily_report.reportDate) # create a new for this month
        dreports = DailyReport.objects.filter(Q(reportDate__year = year) & Q(reportDate__month = month))
        for dr in dreports:
            monthly_report.buys += dr.buys
            monthly_report.sells += dr.sells
            monthly_report.grossPNL += dr.grossPNL
            monthly_report.unrealizedPNL += dr.unrealizedPNL
            monthly_report.secFees += dr.secFees
            monthly_report.clearanceFees += dr.clearanceFees
            monthly_report.commission += dr.commission
            monthly_report.netPNL += dr.netPNL
        monthly_report.save()
        
        
def getReportByDate(today):
    log = open(ERROR_LOG, "a")
    
    refreshReports(today) # create new reports for those symbols have reports last trade date
    
    trades = Trade.objects.filter( tradeDate = today ) 
    
    for trade in trades:
        new_report = newReport(trade.symbol, today) # get report
                
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
        
        new_report.commission += trade.commission
        
        new_report.save() # save result
        
    getFees(today) # calculate fees
    getPNLs(today) # calculate PNLS
    getDailyReport(today) # get daily summary report
    # now delete marks lt today, we do not need them anymore
    Symbol.objects.filter( symbolDate__lt=today ).delete() 
    
    log.write( strftime("%Y-%m-%d %H:%M:%S", time.localtime()) )
    log.write("\tReports calculating done.")
    log.close()
    


# some help functions
def clearReports():
    time_pool = []
    dreports = DailyReport.objects.all()
    for dreport in dreports:
        time_pool.append(dreport.reportDate)
    
    for time in time_pool:
        reports = Report.objects.filter(reportDate=time)
        for report in reports:
            report.buys = 0 # update 
            report.sells = 0
            report.buyAve = 0.0 
            report.sellAve = 0.0
            report.SOD = 0
            report.grossPNL = 0.0
            report.unrealizedPNL = 0.0
            report.commission = 0.0
            report.secFees = 0.0
            report.clearanceFees = 0.0
            report.netPNL = 0.0
            report.LMV = 0.0
            report.SMV = 0.0
            report.EOD = 0
            report.save()
    
    dreports.delete()
    MonthlyReport.objects.all().delete()
    
    
            
            
            
            
