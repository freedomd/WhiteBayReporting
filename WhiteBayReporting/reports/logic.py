import os
from trades.models import Trade
from reports.models import Report, DailyReport, MonthlyReport
from datetime import date
import datetime
from django.db.models import Q
import paramiko
import csv
from settings import DATASOURCE, DATASOURCE_USERNAME, DATASOURCE_PASSWORD
from settings import TRADE_PATH, MARK_PATH, TEMP_PATH
from settings import TRADE_FILE_NAME, MARK_FILE_NAME


#############################################
# get data files
def getMarkFile(file_date):
    # create ssh tunnel to read files from ssh server
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=DATASOURCE, username=DATASOURCE_USERNAME, password=DATASOURCE_PASSWORD)
    ftp = ssh.open_sftp() 
    try:
#        filename = MARK_FILE_NAME + file_date.strftime('%Y%m%d') + ".CSV"
        filename = "WSB858TJ.CST425PO_20130215.CSV"
        filepath = MARK_PATH + filename
        temppath = TEMP_PATH + filename
        ftp.get(filepath, temppath) 
        return temppath # return file path
            
    except Exception, e:
        print str(e.message)
        return None

def getTradeFile(file_date):
    # create ssh tunnel to read files from ssh server
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=DATASOURCE, username=DATASOURCE_USERNAME, password=DATASOURCE_PASSWORD)
    ftp = ssh.open_sftp() 
    try:
#        today = date.today()
#        filename = TRADE_FILE_NAME + file_date.strftime('%Y_%m_%d') + ".csv"
        filename = "WBPT_LiquidEOD_2013_02_15.csv"
        filepath = TRADE_PATH + filename
        temppath = TEMP_PATH + filename
        ftp.get(filepath, temppath) 
        return temppath # return file path
            
    except Exception, e:
        print str(e.message)
        return None
    
#############################################
# save data into database

# this is a test function
def getTrades(filepath):
    header = True
    file = open(filepath, 'rb')
    today = date.today()
    
    for row in csv.reader(file.read().splitlines(), delimiter=','):
        if not header:
            try:
                trade = Trade()
                trade.account = row[0]
                trade.symbol = row[1]
                trade.side = row[3]
                trade.quantity = row[4]
                trade.price = row[5]
                trade.tradeDate = today
                trade.executionId = row[11]
                trade.save() # save into database
            except Exception, e:
                print str(e.message)
                continue
        else:
            header = False

def getMarks(today):
    
    filepath = getMarkFile(today)
    if filepath == None:
        return False
    print "Getting marks..."
#    filepath = './temp/WSB858TJ.CST425PO_20130217.CSV'
    
    file = open(filepath, 'rb')
    for row in csv.reader(file.read().splitlines(), delimiter=','):
        try:
            symbol = row[19].strip()
            if symbol != "" or symbol != None:
                new_report = newReport(symbol, today) # create new report for today
                new_report.closing = float(row[12])
                new_report.save()
            else:
                continue
        except Exception, e:
            #print str(e.message)
            continue
    
    #os.remove(filepath) # remove temporary file
    print "Done"
    return True


def newReport(symbol, today):
#    today = date.today()
#    delta = datetime.timedelta(days=1)
#    yesterday = today - delta
    
    try:
        new_report = Report.objects.get(Q(symbol=symbol) & Q(reportDate__year=today.year) & 
                                        Q(reportDate__month=today.month) & Q(reportDate__day=today.day))
            
    except Report.DoesNotExist: # today's new does not exist
        try: # get latest report of this symbol
#            old_report = Report.objects.get(Q(symbol=symbol) & Q(reportDate__year=yesterday.year) & 
#                                            Q(reportDate__month=yesterday.month) & Q(reportDate__day=yesterday.day))
            old_report = Report.objects.filter( symbol=symbol ).order_by("-reportDate")[0]
            old_report.pk = None
            old_report.save() # clone a new one
            new_report = old_report  
            new_report.buys = 0 # update 
            new_report.sells = 0
            new_report.buyAve = 0.0 
            new_report.sellAve = 0.0
            new_report.SOD = new_report.EOD 
            new_report.mark = new_report.closing
                
        except: # old report does not exist
            new_report = Report()
            new_report.symbol = symbol
                
        new_report.reportDate = today
        new_report.save()
        
    return new_report
    

def getReport(today):
    
    filepath = getTradeFile(today)
    if filepath == None:
        return False
    print "Getting reports..."
#    filepath = './temp/WBPT_LiquidEOD_2013_02_15.csv'
    file = open(filepath, 'rb')
    header = True
    for row in csv.reader(file.read().splitlines(), delimiter=','):
        if not header:
            try:
                trade = Trade()
                trade.account = row[0]
                trade.symbol = row[1]
                trade.side = row[3]
                trade.quantity = int(row[4])
                trade.price = float(row[5])
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
                continue
        else:
            header = False
    
    print "Done"
    print "Calculating PNLS and summary reports..."
    getPNLs(today) # calculate PNLS
    getDailyReport(today) # get daily summary report
    print "Done"
    #os.remove(filepath) # remove temporary file
    return True


###########################################################
# calcluate pnls for each report
def getPNLs(report_date):
    report_list = Report.objects.filter( Q(reportDate = report_date) )
    for report in report_list: 
        mark = report.mark # mark to market value
        closing = report.closing # closing price today
        SOD = report.SOD # start of day
        buys = report.buys
        buyAve = report.buyAve
        sells = report.sells
        sellAve = report.sellAve
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
            
        if common == 0: # no trades on this report
            report.delete()
            continue
            
        # gross PNL    
        grossPNL = common * (sellAve - buyAve)
        report.grossPNL = grossPNL
        
        # left shares
        buys -= common
        sells -= common
        unrealizedPNL = (closing - buyAve) * buys + (sellAve - closing) * sells
        report.unrealizedPNL = unrealizedPNL
        
        # net PNL
        report.netPNL = grossPNL + unrealizedPNL - report.fees
        
        # LMV and SMV
        if EOD >=0:
            report.LMV = EOD * closing
            report.SMV = 0
        else:
            report.LMV = 0
            report.SMV = EOD * closing
        
        report.EOD = EOD   
        report.save()
   
  
# get summary data of reports with a specific date
def getDailyReport(report_date):
    daily_report = DailyReport()
    report_list = Report.objects.filter( Q(reportDate = report_date) )
    for report in report_list:
        daily_report.SOD += report.SOD
        daily_report.buys += report.buys
        daily_report.sells += report.sells
        daily_report.grossPNL += report.grossPNL
        daily_report.unrealizedPNL += report.unrealizedPNL
        daily_report.fees += report.fees
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
    today = date.today()
    try:
        monthly_report = MonthlyReport.objects.get(Q(reportDate__year = year) & Q(reportDate__month = month))
    except MonthlyReport.DoesNotExist:
        monthly_report = MonthlyReport(reportDate = today) # create a new for this month
    
    monthly_report.buys += daily_report.buys
    monthly_report.sells += daily_report.sells
    monthly_report.grossPNL += daily_report.grossPNL
    monthly_report.unrealizedPNL += daily_report.unrealizedPNL
    monthly_report.fees += daily_report.fees
    monthly_report.netPNL += daily_report.netPNL
    monthly_report.LMV += daily_report.LMV
    monthly_report.SMV += daily_report.SMV
    
    monthly_report.save()
            
            
            
            
