from trades.models import Trade
from reports.models import Report, DailyReport, MonthlyReport
from datetime import date
import datetime
from django.db.models import Q

def newReport(symbol):
    today = date.today()
    delta = datetime.timedelta(days=1)
    yesterday = today - delta
    
    try:
        new_report = Report.objects.get(Q(symbol=symbol) & Q(reportDate__year=today.year) & 
                                        Q(reportDate__month=today.month) & Q(reportDate__day=today.day))
            
    except Report.DoesNotExist: # today's new does not exist
        try: # get yesterday's
            old_report = Report.objects.get(Q(symbol=symbol) & Q(reportDate__year=yesterday.year) & 
                                            Q(reportDate__month=yesterday.month) & Q(reportDate__day=yesterday.day))
            old_report.pk = None
            old_report.save() # clone a new one
            new_report = old_report  
            new_report.buys = 0 # update 
            new_report.sells = 0
            new_report.buyAve = 0.0 
            new_report.sellAve = 0.0
            new_report.SOD = new_report.EOD 
            new_report.mark = new_report.closing
                
        except Report.DoesNotExist: # yesterday's old does not exist
            new_report = Report()
            new_report.symbol = symbol
                
        new_report.reportDate = today
        new_report.save()
        
    return new_report
    

def getReport():
    today = date.today()
    
    trades = Trade.objects.filter(Q(tradeDate__year=today.year) & Q(tradeDate__month=today.month) & Q(tradeDate__day=today.day))

    for trade in trades:
        new_report = newReport(trade.symbol)
        
        # update report
        if trade.side == "B":
            total = new_report.buys * new_report.buyAve
            total += trade.quantity * trade.price # new total
            new_report.buys += trade.quantity # new buys
            new_report.buyAve = total / new_report.buys # new buy ave
            
        elif trade.side == "S" or trade.side == "SS":
            total = new_report.sells * new_report.sellAve
            total += trade.quantity * trade.price # new total
            new_report.sells += trade.quantity # new sells
            new_report.sellAve = total / new_report.sells # new sell ave
        
        else:
            print "Error: Invalid Side."
            continue
   
        new_report.save() # save result
    
    getPNLs(today) # calculate PNLS
    getDailyReport(today) # get daily summary report


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
        
        if SOD >= 0:
            total = buys * buyAve + mark * SOD
            buys += SOD
            buyAve = total / buys
        else:
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
            
            
            
            
