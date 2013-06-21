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


# save data into database
def getSecurities(filepath, today):
    header = True
    file = open(filepath, 'rb')
    
    for row in csv.reader(file.read().splitlines(), delimiter=','):
        if not header:
            try:           
                sec = Security()
                sec.symbol = row[0].strip()
                #sec.name = row[1].strip()
                sec.market = row[2].strip()
                sec.secDate = today
                sec.save() # save into database
            except Exception, e:
                print sec.symbol
                print str(e.message)
                continue
        else:
            header = False
            
    file.close()    
    
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
                        if len(year) == 4:
                            year = year[2:]
                        date_str = year + month + day
                        
                        #strike
                        strike = float(row[9])
                        strike_str = str(int(strike * 1000))
                        while (len(strike_str) < 8):
                            strike_str = "0" + strike_str
                        
                        
                        symbol = row[5].strip() 
                        while len(symbol) < 6:
                            symbol += " "
                        symbol += date_str + "C" + strike_str
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
                        if len(year) == 4:
                            year = year[2:]
                        date_str = year + month + day
                        
                        #strike
                        strike = float(row[9])
                        strike_str = str(int(strike * 1000))
                        while (len(strike_str) < 8):
                            strike_str = "0" + strike_str
                        
                        symbol = row[5].strip() 
                        while len(symbol) < 6:
                            symbol += " "
                        symbol += date_str + "P" + strike_str
                        #print symbol
                    else:     
                        symbol = row[5].strip()
                        #print symbol
                    if symbol == "" or symbol == None:
                        continue
                        
                    closing = float(row[17])
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
                if len(date_str[2]) == 2:
                    year = "20" + date_str[2]
                else:
                    year = date_str[2]
                mark_date = date(int(year), int(date_str[0]), int(date_str[1]))
                
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
            new_report.baseMoney = 0.0
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

# For exercised or assigned option, the execution price is the average
def getExecutionPrice(account, symbol, tradeDate):
    
    new_report = newReport(account, symbol, tradeDate)
    # check if SOD is zero
    quantity = new_report.SOD
    total = new_report.SOD * new_report.mark
    
    if quantity == 0:
        ## not correct implemented yet
        # check if there is trade on tradeDate
        trade_list = Trade.objects.filter(Q(account = account) & Q(tradeDate = tradeDate)
                                          & Q(symbol = symbol) & ~Q(description__icontains = "OPTION"))
        #print new_report.account + ", " + new_report.symbol
        # calculate the average price
        for t in trade_list:
            #print "in list " + t.side + ", " + str(t.price) + ", " + str(t.quantity) + t.executionId
            
            # to be modified
            if "BUY" in t.side:
                quantity += t.quantity
                total += t.quantity * t.price
     
    price = total / quantity
    
    return price
            

def getRollTrades(today):
    trades = Trade.objects.filter(tradeDate=today)
    for trade in trades:
        try:
            
            # dividend
            if "DIVIDEND" in trade.description:
                new_report = newReport(trade.account, trade.symbol, trade.tradeDate)
                if (new_report.pendingShare != 0 and "DSTP" in trade.description ) or \
                    (new_report.pendingCash != 0.0 and "DIVP" in trade.description):
                    trade.description = "PENDING ALEART: " + trade.description
                if (trade.quantity != 0 and "DSTP" not in trade.description) or \
                    (trade.baseMoney != 0.0 and "DIVP" not in trade.description):
                    trade.description = "SETTLED: " + trade.description
                trade.save()
                RollTrade.objects.create(account=trade.account, symbol=trade.symbol, securityType = trade.securityType,
                                         side=trade.side, quantity=trade.quantity, baseMoney = trade.baseMoney, 
                                         tradeDate=trade.tradeDate, description = trade.description)
                continue
            
            # exercised option
            if trade.description == "ASSIGNED OPTION" or trade.description == "EXERCISED OPTION":
                if trade.price == 0.0:
                    trade.price = getExecutionPrice(trade.account, trade.symbol, trade.tradeDate)                
                    trade.save()
                # do not roll the option exercised and assigned trade
                RollTrade.objects.create(account=trade.account, symbol=trade.symbol, securityType = trade.securityType,
                                         side=trade.side, price=trade.price, quantity=trade.quantity, 
                                         baseMoney = trade.baseMoney, route=trade.route, destination=trade.destination,
                                         liqFlag=trade.liqFlag, tradeDate=trade.tradeDate, description = trade.description)
                continue
            
            # transferred from exercised option pnl, calculate the base money, clear the quantity
            elif "PNL" in trade.description:
                if trade.quantity != 0:
                    symb = trade.description.split(":")[1]
                    price = getExecutionPrice(trade.account, symb, trade.tradeDate)
                    quantity = trade.quantity
                    trade.baseMoney = price * quantity
                    #print symb + ", " + str(price) + ", " + str(quantity) + ", " + str(trade.baseMoney)
                    trade.quantity = 0
                    trade.save()
                # do not roll the option transferred trade
                RollTrade.objects.create(account=trade.account, symbol=trade.symbol, securityType = trade.securityType,
                                         side=trade.side, price=trade.price, quantity=trade.quantity, baseMoney = trade.baseMoney,
                                         route=trade.route, destination=trade.destination, liqFlag=trade.liqFlag,
                                         tradeDate=trade.tradeDate, description = trade.description)
                continue
                
            # do not roll the trades with Route "BAML", "INSTINET", "ITGI", and exercised trades
            if trade.route == "BAML" or trade.route == "INSTINET" or trade.route == "ITGI" or trade.route == "":
                RollTrade.objects.create(account=trade.account, symbol=trade.symbol, securityType = trade.securityType,
                                         side=trade.side, price=trade.price, quantity=trade.quantity, 
                                         baseMoney = trade.baseMoney, ecnFees=trade.ecnFees, route=trade.route,
                                         destination=trade.destination, broker = trade.broker, liqFlag=trade.liqFlag,
                                         tradeDate=trade.tradeDate, description = trade.description)
                
                continue
            
            # for Route "RAVEN", roll the trades with same account, symbol, and side
            elif trade.route == "RAVEN":
                rtrade = RollTrade.objects.get(Q(account=trade.account) & Q(symbol=trade.symbol) & Q(side=trade.side) &
                                               Q(tradeDate=trade.tradeDate))
                
                total = (rtrade.quantity * rtrade.price) + (trade.quantity * trade.price)
                rtrade.quantity += trade.quantity
                rtrade.price = total / rtrade.quantity
                rtrade.ecnFees += trade.ecnFees
                rtrade.save()
            
            
            # for Route "WBPT"                
            else:
                rtrade = RollTrade.objects.get(Q(account=trade.account) & Q(symbol=trade.symbol) & 
                                           Q(side=trade.side) & Q(price=trade.price) & 
                                           Q(route=trade.route) & Q(destination=trade.destination) &    
                                           Q(tradeDate=trade.tradeDate))
                rtrade.quantity += trade.quantity 
                rtrade.ecnFees += trade.ecnFees           
                rtrade.save()
        except RollTrade.DoesNotExist:
            RollTrade.objects.create(account=trade.account, symbol=trade.symbol, securityType = trade.securityType,
                                     side=trade.side, price=trade.price, quantity=trade.quantity, baseMoney = trade.baseMoney,
                                     ecnFees=trade.ecnFees, route=trade.route, destination=trade.destination,
                                     broker = trade.broker, liqFlag=trade.liqFlag, tradeDate=trade.tradeDate,
                                     description = trade.description)
    
    return RollTrade.objects.filter(tradeDate=today)

# get the report of each symbol in an account of each day
def getReportByDate(today):
    log = open(ERROR_LOG, "a")
    
    refreshReports(today) # create new reports for those symbols have reports last trade date
    
    # after 2012-11-20, should do roll up the trades
    if today <= date(2012, 11, 20):
        rollTrades = Trade.objects.filter(tradeDate = today)
    else:
        rollTrades = getRollTrades(today)
    
    print "finish rolling trades, trades: " + str(len(Trade.objects.filter(tradeDate=today))) + ", rolltrades: " + str(len(RollTrade.objects.filter(tradeDate=today)))
    for rtrade in rollTrades:
        new_report = newReport(rtrade.account, rtrade.symbol, today)
        #print new_report.account + ", " + new_report.symbol
        
        if today <= date(2012, 11, 20): # for rollTrades, did this in getRollTrades() method
            #exercised option
            if rtrade.description == "ASSIGNED OPTION" or rtrade.description == "EXERCISED OPTION":
                rtrade.price = new_report.mark
                rtrade.save()
            # transferred from exercised option pnl, calculate the base money, clear the quantity
            elif "PNL" in rtrade.description:
                symb = rtrade.description.split(":")[1]
                new_report = newReport(rtrade.account, symb, today)
                price = new_report.mark
                quantity = rtrade.quantity
                rtrade.baseMoney = price * quantity
                rtrade.quantity = 0
                rtrade.save()
                
        # if the trade is dividend
        if "DIVIDEND" in rtrade.description:
            # cash dividend
            if "CASH" in rtrade.description:
                new_report.todayCash -= rtrade.baseMoney
                if "DIVP" not in rtrade.description:
                    new_report.cashClearFlag = True
            # stock dividend
            elif "STOCK" in rtrade.description:
                new_report.todayShare += rtrade.quantity
                if "DSTP" not in rtrade.description:
                    new_report.shareClearFlag = True
            new_report.save()
            continue
            
        # if the trade is an option transferred pnl
        if rtrade.price == 0.00 and rtrade.quantity == 0:
            # if no buy or sell on that day, then we cannot add the pnl into average
            # calculate it separately
            if 'BUY' in rtrade.side:
                #print "in buy: " + rtrade.account + " " + new_report.symbol + ", " + str(new_report.baseMoney) + ", " + str(rtrade.baseMoney)
                total = new_report.buys * new_report.buyAve
                total += rtrade.baseMoney # add the base money into the total
                if new_report.buys != 0 and new_report.sells != 0:
                    new_report.buyAve = total / new_report.buys
                new_report.baseMoney -= rtrade.baseMoney
                #print str(new_report.baseMoney)
            else:
                #print "in sell: " + rtrade.account + " "  + new_report.symbol + ", " + str(new_report.baseMoney) + ", " + str(rtrade.baseMoney)
                total = new_report.sells * new_report.sellAve
                total += rtrade.baseMoney
                if new_report.buys != 0 and new_report.sells != 0:
                    new_report.sellAve = total / new_report.sells
                new_report.baseMoney += rtrade.baseMoney
                #print str(new_report.baseMoney)
            new_report.save()
            continue
        
        # normal trades 
        # buy and sell
        if 'BUY' in rtrade.side:
            total = new_report.buys * new_report.buyAve
            total += rtrade.quantity * rtrade.price # new total
            new_report.buys += rtrade.quantity # new buys
            new_report.buyAve = total / new_report.buys # new buy ave
                
        elif 'SEL' in rtrade.side or rtrade.side == "SS":
            total = new_report.sells * new_report.sellAve
            total += rtrade.quantity * rtrade.price # new total
            new_report.sells += rtrade.quantity # new sells
            new_report.sellAve = total / new_report.sells # new sell ave
                
        else:
            print "Error: Invalid Side."
            continue
            
            
        #Fees
        firm = Firm.objects.all()[0]
        if today < date(2013, 5, 28):
            secRate = firm.secFee  
        else:
            secRate = 0.00001740
        
        #no ecn fees for transfer
        if rtrade.liqFlag == "" and rtrade.route == "" and rtrade.destination == "":
            #brockerCommission = 0.0
            ecnFees = 0.0
        else:
            # already calculated
            ecnFees = rtrade.ecnFees
           
        ## sec fees
        if "BUY" not in rtrade.side and rtrade.description != "ASSIGNED OPTION" and rtrade.description != "EXERCISED OPTION":
            #print rtrade.account + ", " + rtrade.symbol + ", " + str(rtrade.price) + ", " + str(rtrade.quantity)            
            if len(rtrade.symbol.split(' ')) > 1 and "00" in rtrade.symbol: # option
                secFees = rtrade.price * rtrade.quantity * 100 * secRate
            else:
                secFees = rtrade.price * rtrade.quantity * secRate
            rsecFees = round(secFees, 2)
                    
            #print "sec: " + str(secFees) + ", rsec: " + str(rsecFees)
            if secFees > rsecFees:
                secFees = rsecFees + 0.01
            else:
                secFees = rsecFees
            #print "after sec: " + str(secFees)
        else:
            secFees = 0
        
        ## broker commission
        try:
            broker = Broker.objects.get(Q(brokerNumber=rtrade.broker) & Q(securityType=rtrade.securityType))
            brokerCommission = rtrade.quantity * broker.commissionRate
        except Broker.DoesNotExist:
            brokerCommission = 0.0
            
        ## clearance fee
        clearance = rtrade.quantity * 0.0001 # TODO: make this argument as a member of firm
        clearance = round(clearance, 2)            
        if clearance > 3.00:
            clearance = 3.00
        elif clearance < 0.01:
            clearance = 0.01
                
        ## update report
        new_report.clearanceFees += clearance
        new_report.brokerCommission += brokerCommission
        new_report.commission += clearance + brokerCommission
        # for the specific contract broker, we calculate the accrued Sec Fees other than secFees
        if rtrade.route == "WBPT" and (rtrade.destination == "FBCO" or rtrade.destination == "UBS"):
            new_report.accruedSecFees += secFees
        else:
            new_report.secFees += secFees
        new_report.ecnFees += ecnFees
        new_report.save()            
    
    # delete the rolltrades
#     if today > date(2012, 11, 20):
#         rollTrades.delete()
    
    #getPNLs(today)
    getDailyReport(today)
    
    # now delete marks lt today, we do not need them anymore
    Symbol.objects.filter( symbolDate__lt=today ).delete() 
    
    # we may want to delete the security primary exchange info after calculation
    #Security.objects.filter( secDate__lt = today ).delete()
        
    log.write( strftime("%Y-%m-%d %H:%M:%S", time.localtime()) )
    log.write("\tReports calculating done.\n")
    log.close()

# get Ecn fees for one trade
def getECNFees(symbol, tradeDate, destination, liqFlag, price, quantity):
    ## ecn fees
    ecnFees = 0.0
    try:
        # use the underlying symbol for options
        if len(symbol.split(' ')) > 1 and "00" in symbol:
            underlyingSymbol = symbol.split(" ")[0]
        else:
            underlyingSymbol = symbol
        security = Security.objects.get(Q(symbol=underlyingSymbol) & Q(secDate=tradeDate))
        market = security.market
        if market == "NYSE":
            t_tape = "A"
        elif market == "AMEX" or market == "ARCA":
            t_tape = "B"
        else: 
            t_tape = "C"
        routes = Route.objects.filter(Q(routeId=destination) 
                                   & Q(flag=liqFlag) 
                                   & (Q(tape=t_tape) | Q(tape="ALL")))
        
        # check each route's price period, feeType
        for route in routes:
            lowPrice = route.priceFrom
            highPrice = route.priceTo
            if price > lowPrice and price <= highPrice:
                if route.feeType == "FLAT PER SHARE" or route.feeType == "FLAT PER CONTRACT":
                    ecnFees = route.rebateCharge * quantity
                elif route.feeType == "BASIS POINTS":
                    ecnFees = route.rebateCharge * 0.0001 * quantity * price
                else:
                    ecnFees = 0.0
            else:
                continue
    except Security.DoesNotExist, Route.DoesNotExist:
        ecnFees = 0.0
        
    return ecnFees  

# get summary data of reports with a specific date
def getDailyReport(report_date):
    log = open(ERROR_LOG, "a")
    report_list = Report.objects.filter( Q(reportDate = report_date) )
    print "in daily report"
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
            #print report.symbol + ", " + report.closing
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
        if len(symbol.split(' ')) > 1 and "00" in symbol:
            grossPNL = grossPNL * 100 #option
        report.grossPNL = grossPNL 
        
        # left shares
        buys -= common
        sells -= common
        unrealizedPNL = (closing - buyAve) * buys + (sellAve - closing) * sells
        if len(symbol.split(' ')) > 1 and "00" in symbol:
            unrealizedPNL = unrealizedPNL * 100 #option
        # if no buys or sells on that day, calculate the base money separately
        # else, the base money is already applied in average price
        if report.buys == 0 or report.sells == 0:
            unrealizedPNL += report.baseMoney   
        
        # dividend
        # stock dividend
        if report.pendingShare != report.todayShare:
            shareDiffer = report.todayShare - report.pendingShare
            report.pendingShare = report.todayShare
            report.todayShare = 0
            unrealizedPNL += shareDiffer * report.closing
            EOD += shareDiffer
        # cash dividend
        if report.pendingCash != report.todayCash:
            cashDiffer = report.todayCash - report.pendingCash
            report.pendingCash = report.todayCash
            report.todayCash = 0.0
            report.netPNL += cashDiffer
        # check if clear the dividend
        if report.shareClearFlag == True:
            report.pendingShare = 0
            report.todayShare = 0
            report.shareClearFlag = False
        if report.cashClearFlag == True:
            report.pendingCash = 0.0
            report.todayCash = 0.0
            report.cashClearFlag = False
            
        # unrealizedPNL
        report.unrealizedPNL = unrealizedPNL
        # net PNL
        report.netPNL = report.grossPNL + report.unrealizedPNL# - report.secFees - report.accruedSecFees - report.ecnFees - report.commission
        
        # LMV and SMV
        if EOD >=0:
            if len(symbol.split(' ')) > 1 and "00" in symbol:
                report.LMV = EOD * closing * 100 #option
            else:
                report.LMV = EOD * closing
            report.SMV = 0
        else:
            report.LMV = 0
            if len(symbol.split(' ')) > 1 and "00" in symbol:
                report.SMV = EOD * closing * 100 #option
            else:
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
        daily_report.accruedSecFees += report.accruedSecFees
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
        account.accruedSecFees += daily_report.accruedSecFees
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
            account.accruedSecFees += report.accruedSecFees
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
        monthly_report.accruedSecFees += daily_report.accruedSecFees
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
            monthly_report.accruedSecFees += dr.accruedSecFees
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
                trade.quantity = int(row[4])
                trade.price = float(row[5])
                trade.route = row[6]
                trade.destination = row[7]
                trade.liqFlag = row[9]
                trade.tradeDate = today
                trade.executionId = row[11]
                trade.ecnFees = getECNFees(trade.symbol, trade.tradeDate, 
                                           trade.destination, trade.liqFlag, 
                                           trade.price, trade.quantity)
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
    #i = 0
    for filename in filelist: # each file represent one day
        if filename == ".DS_Store":
            continue
        filepath = os.path.join(path, filename)
        print filepath
        file = open(filepath, 'rb')
        header = True
        for row in csv.reader(file.read().splitlines(), delimiter=','): # all marks in this file
            if not header:
                try:
#                     i += 1
#                     if i % 1000 == 0:
#                         print i
                    
                    date_str = row[10].split("/")
                    if len(date_str[2]) == 2:
                        year = "20" + date_str[2]
                    else:
                        year = date_str[2]
                    today = date(int(year), int(date_str[0]), int(date_str[1]))
                    
                    trade = Trade()
                    trade.account = row[0]
                    #symbol
                    if row[2] == "OPT" and row[6] == "BAML":
                        symbol_str = row[1].split(" ")
                        symb = symbol_str[0]
                        while len(symb) < 6:
                            symb += " "
                        info = symbol_str[1]
                        front = info[0:7]
                        end = info[7:]
                        while len(end) < 8:
                            end = "0" + end
                        trade.symbol = symb + front + end
                    else:
                        trade.symbol = row[1].strip()
                    trade.securityType = row[2]
                    trade.side = row[3]
                    trade.quantity = int(row[4])
                    trade.price = float(row[5])
                    trade.route = row[6]
                    trade.destination = row[7]
                    trade.liqFlag = row[9]
                    trade.tradeDate = today
                    trade.executionId = row[11]
                    trade.ecnFees = getECNFees(trade.symbol, trade.tradeDate, 
                                               trade.destination, trade.liqFlag, 
                                               trade.price, trade.quantity)
                    
                    # broker
                    if trade.route == "INSTINET":
                        trade.broker = "INCA"
                    elif trade.route == "WBPT":
                        if trade.destination == "BARCAP":
                            trade.broker = "BARC"
                        elif trade.destination == "FBCO":
                            trade.broker = "FBCO"
                        elif trade.destination == "UBS":
                            trade.broker = "UBSS"
                    elif trade.route == "ITGI" and trade.securityType == "SEC":
                        trade.broker = "ITGI"
                    
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
                    if row[16] == "#": #cancel order
                        continue
                    
                    date_str = row[5]
                    today = date(int(date_str[0:4]), int(date_str[4:6]), int(date_str[6:]))
                    #print today
                    
                    trade = Trade()
                    trade.account = row[2]
                    trade.symbol = row[8].strip()
                    sec = row[4]
                    if sec == "OPTION":
                        trade.securityType = "OPT"
                    else:
                        trade.securityType = "SEC"
                    
                    side = row[19]
                    if side == "SELL":
                        trade.side = "SEL"
                    elif side == "SELL OPEN":
                        trade.side = "SS"
                    else:
                        trade.side = "BUY"
                        
                    trade.quantity = int(row[20].split('.')[0].replace(',',''))
                    trade.price = float(row[21])
                    trade.tradeDate = today
                    trade.description = "TRANSFER"
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

# import the option exercise and expire records as trades
def getOptionsAsTradesByDir(path):
    print "Getting option exercise record from files..."
    filelist = os.listdir(path)
    filelist.sort()
    log = open(ERROR_LOG, "a")
    
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
                    date_str = row[6].split('/')
                    if len(date_str[2]) == 2:
                        year = "20" + date_str[2]
                    else:
                        year = date_str[2]
                    today = date(int(year), int(date_str[0]), int(date_str[1]))
                    #print today
                    
                    trade = Trade()
                    trade.account = row[3] + row[4]
                    trade.symbol = row[9].strip()
                    
                    #print trade.account + ", " + trade.symbol
                    sec = row[8]
                    if sec == "SSU":
                        trade.securityType = "SEC"                       
                    else:
                        trade.securityType = "OPT"
                    
                    side = row[12]
                    if side.strip() == "S":
                        trade.side = "SEL"
                    else:
                        trade.side = "BUY"
                    
                    trade.quantity = int(row[17])
                    trade.tradeDate = today
                    
                    if sec == "SSU": #stock
                        trade.price = float(row[18])
                        trade.description = "EXERCISE"
                    else: #option
                        action = row[11]
                        trade.price = 0.00
                        if action == "Expired":
                            trade.description = "EXPIRED OPTION"
                        elif action == "Exercise":
                            trade.description = "EXERCISED OPTION"
                            
                            # add the option's pnl into the underlying equity
                            underlyingTrade = Trade()
                            underlyingTrade.account = trade.account
                            underlyingTrade.symbol = trade.symbol.split(" ")[0]
                            underlyingTrade.securityType = "SEC"
                            underlyingTrade.side = "BUY"
                            underlyingTrade.quantity = trade.quantity * 100 # Temporarily stored, will be cleared in getRollTrade
                            underlyingTrade.baseMoney = 0.00 # will be calculated in getRollTrade
                            underlyingTrade.tradeDate = today
                            underlyingTrade.description = "TRANSFER PNL FROM EXERCISED OPTION:" + trade.symbol
                            underlyingTrade.save()
                        else: #assign
                            trade.description = "ASSIGNED OPTION"
                            
                            # add the option's pnl into the underlying equity
                            underlyingTrade = Trade()
                            underlyingTrade.account = trade.account
                            underlyingTrade.symbol = trade.symbol.split(" ")[0]
                            underlyingTrade.securityType = "SEC"
                            underlyingTrade.side = "SEL"
                            underlyingTrade.quantity = trade.quantity * 100 # Temporarily stored, will be cleared in getRollTrade
                            underlyingTrade.baseMoney = 0.00 # will be calculated in getRollTrade
                            underlyingTrade.tradeDate = today
                            underlyingTrade.description = "TRANSFER PNL FROM ASSIGNED OPTION:" + trade.symbol
                            underlyingTrade.save()
                            
                    trade.save() # save into database
                        
                        
                except Exception, e:
                    print str(e.message)
                    log.write( strftime("%Y-%m-%d %H:%M:%S", time.localtime()) )
                    log.write( "\tGet trade %s from option file %s failed: %s\n" % (trade.symbol, filename, str(e.message)) )
                    continue
            else:
                header = False
        file.close()    
    log.close()
    print "Done"
    return True

# import the broker commission rate
def getBrokerCommission(path):
    print "Getting Broker Commission from files..."
    filelist = os.listdir(path)
    filelist.sort()
    log = open(ERROR_LOG, "a")
    
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
                    new_broker = Broker()
                    new_broker.brokerNumber = row[0].strip()
                    new_broker.securityType = row[1].strip()
                    new_broker.commissionRate = float(row[2])
                    new_broker.save()
                        
                except Exception, e:
                    print str(e.message)
                    log.write( strftime("%Y-%m-%d %H:%M:%S", time.localtime()) )
                    log.write( "\tGet broker commission %s from mark file %s failed: %s\n" % (new_broker.brokerNumber, filename, str(e.message)) )
                    continue
            else:
                header = False
        file.close()    
    log.close()
    print "Done"
    return True       

def getDividendByDir(path):
    print "Getting dividend record from files..."
    filelist = os.listdir(path)
    filelist.sort()
    log = open(ERROR_LOG, "a")
    
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
                    date_str = row[2].split('/')
                    if len(date_str[2]) == 2:
                        year = "20" + date_str[2]
                    else:
                        year = date_str[2]
                    today = date(int(year), int(date_str[0]), int(date_str[1]))
                    #print today
                    
                    trade = Trade()
                    trade.symbol = row[18].strip()
                    if trade.symbol == None or trade.symbol == "":
                        continue
                    
                    entryType = row[16].strip()
                    if entryType != "DV":
                        continue
                    
                    # currently, we only handle DV
                    trade.account = row[4]
                    
                    #print trade.account + ", " + trade.symbol
                    sec = row[5]
                    if sec == "1":
                        trade.securityType = "SEC"
                    elif sec == "2":
                        trade.securityType = "OPT"
                    elif sec == "3":
                        trade.securityType = "BOND"
                    
                    side = row[11]
                    if side == "B":
                        trade.side = "BUY"
                    else:
                        trade.side = "SEL"
                    
                    trade.description = row[15].strip()
                    if trade.description == "DIVP" or trade.description == "DIV" or \
                        trade.description == "MDIV" or trade.description == "RCP" or \
                        trade.description == "FDV" or trade.description == "FTD":
                        trade.description = "CASH DIVIDEND, " + trade.description
                        trade.baseMoney = float(row[14])
                    elif trade.description == "DSTP" or trade.description == "DST":
                        trade.description = "STOCK DIVIDEND, " + trade.description
                        trade.quantity = int(row[12])
                        
                    trade.tradeDate = today    
                    trade.save() # save into database
                        
                except Exception, e:
                    print str(e.message)
                    log.write( strftime("%Y-%m-%d %H:%M:%S", time.localtime()) )
                    log.write( "\tGet dividend %s from mark file %s failed: %s\n" % (trade.symbol, filename, str(e.message)) )
                    continue
            else:
                header = False
        file.close()    
    log.close()
    print "Done"
    return True

# import the mark file before the first day, set up the positions
def setupReport(path):  
    print "Getting mark record from files..."
    filelist = os.listdir(path)
    filelist.sort()
    log = open(ERROR_LOG, "a")
    
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
                    #date_str = row[6].split('/')
                    ## for trading data start from 5/20, we import the mark file on 5/17 to setup
                    today = date(2013, 5, 17)
                    #print today
                    
                    new_report = Report()
                    new_report.account = row[2]
                    
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
                        if len(year) == 4:
                            year = year[2:]
                        date_str = year + month + day
                        
                        #strike
                        strike = float(row[9])
                        strike_str = str(int(strike * 1000))
                        while (len(strike_str) < 8):
                            strike_str = "0" + strike_str
                        
                        
                        symbol = row[5].strip() 
                        while len(symbol) < 6:
                            symbol += " "
                        symbol += date_str + "C" + strike_str
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
                        if len(year) == 4:
                            year = year[2:]
                        date_str = year + month + day
                        
                        #strike
                        strike = float(row[9])
                        strike_str = str(int(strike * 1000))
                        while (len(strike_str) < 8):
                            strike_str = "0" + strike_str
                        
                        symbol = row[5].strip() 
                        while len(symbol) < 6:
                            symbol += " "
                        symbol += date_str + "P" + strike_str
                        #print symbol
                    elif type == "SSU":     
                        symbol = row[5].strip()
                    else:
                        continue
                    
                    #print symbol
                    if symbol == "" or symbol == None:
                        continue
                        
                    position = int(row[16])
                    closing = float(row[17])
                    
                    new_report.symbol = symbol
                    new_report.closing = closing
                    new_report.EOD = position
                    new_report.reportDate = today
                    
                    new_report.save()
                        
                except Exception, e:
                    print str(e.message)
                    log.write( strftime("%Y-%m-%d %H:%M:%S", time.localtime()) )
                    log.write( "\tGet symbol %s from mark file %s failed: %s\n" % (new_report.symbol, filename, str(e.message)) )
                    continue
            else:
                header = False
        file.close()    
    log.close()
    print "Done"
    return True   
