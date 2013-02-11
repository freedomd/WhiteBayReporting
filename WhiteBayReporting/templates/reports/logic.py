from trades.models import Trade
from reports.models import Report
from datetime import date
import datetime
from django.db.models import Q

def getReport():
    today = date.today()
    delta = datetime.timedelta(days=1)
    yesterday = today - delta
    
    trades = Trade.objects.filter(Q(tradeDate__year=today.year) & Q(tradeDate__month=today.month) & Q(tradeDate__day=today.day))

    for trade in trades:
        try:
            new_report = Report.objects.get(Q(symbol=trade.symbol) & Q(reportDate__year=today.year) & 
                                            Q(reportDate__month=today.month) & Q(reportDate__day=today.day))
            
        except Report.DoesNotExist: # today's new does not exist
            try: # get yesterday's
                old_report = Report.objects.get(Q(symbol=trade.symbol) & Q(reportDate__year=yesterday.year) & 
                                                Q(reportDate__month=yesterday.month) & Q(reportDate__day=yesterday.day))
                old_report.pk = None
                old_report.save() # clone a new one
                new_report = old_report  
                new_report.SOD = new_report.EOD # update SOD
            except Report.DoesNotExist: # yesterday's old does not exist
                new_report = Report()
                new_report.symbol = trade.symbol
                
            new_report.reportDate = today
        
        # update report
        if trade.side == "B":
            total = new_report.buys * new_report.buyAve
            total += trade.quantity * trade.price # new total
            new_report.buys += trade.quantity # new buys
            new_report.buyAve = total / new_report.buys # new buy ave
            new_report.EOD = new_report.EOD + trade.quantity
            
        elif trade.side == "S":
            total = new_report.sells * new_report.sellAve
            total += trade.quantity * trade.price # new total
            new_report.sells += trade.quantity # new sells
            new_report.sellAve = total / new_report.sells # new sell ave
            new_report.EOD = new_report.EOD - trade.quantity
        
        new_report.save() # save result
    
    getPNLs(today) # calculate PNLS
    getTotal(today) # get summary date

# calcluate pnls for each report
def getPNLs(report_date):
    report_list = Report.objects.filter( Q(reportDate = report_date) )
    for report in report_list: 
        mark = report.mark # mark to market value
        #SOD = report.SOD
        buys = report.buys
        buyAve = report.buyAve
        sells = report.sells
        sellAve = report.sellAve
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
        unrealizedPNL = (mark - buyAve) * buys + (sellAve - mark) * sells
        report.unrealizedPNL = unrealizedPNL
        
        report.netPNL = grossPNL + unrealizedPNL - report.fees
        report.LMV = buys * mark
        report.SMV = -sells * mark
        
        report.save()
   
  
# get summary data of reports with a specific date
def getTotal(report_date):
    total = Report()
    total.symbol = "Total"
    report_list = Report.objects.filter( Q(reportDate = report_date) )
    for report in report_list:
        total.SOD += report.SOD
        total.buys += report.buys
        total.sells += report.sells
        total.grossPNL += report.grossPNL
        total.unrealizedPNL += report.unrealizedPNL
        total.fees += report.fees
        total.netPNL += report.netPNL
        total.LMV += report.LMV
        total.SMV += report.SMV
        total.EOD += report.EOD
    total.reportDate = report_date
    total.save()

            
            
            
            
