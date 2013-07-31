'''''
This logic file contains useful methods for importing data from a new account that does not exist in system.
'''''


import os
from admins.models import Firm, Account, Broker, FutureFeeGroup, FutureFeeRate, FutureMultiplier
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
# get multiplier for future and future option
def getMultiplierByDate(path, today):
    print "Getting multipliers..."
    filelist = os.listdir(path)
    filelist.sort()
    log = open(ERROR_LOG,"a") 
    
    for filename in filelist:
        if filename == ".DS_Store":
            continue
        filepath = os.path.join(path, filename)
        print filepath
        file = open(filepath, 'rb') 
        header = True
            
        #read the multiplier file
        for row in csv.reader(file.read().splitlines(), delimiter=','): 
            if not header:               
                try:      
                    symbol = row[38].strip()
                    expDate = str(row[36]).strip()
            
                    if expDate != "" and expDate != "0": # future option
                        #strike
                        strike = row[19]
                        if float(strike) == int(strike.split('.')[0]):
                            strike_str = strike.split('.')[0]
                        else:
                            strike_str = strike
    
                        symbol += " " + row[18].strip() + strike_str
                        #print symbol
    
                    multiplier = int(float(str(row[10]).strip()))
                    try:
                        new_symbol = Symbol.objects.get(Q(symbol=symbol) & Q(symbolDate=today))
                        continue
                    except Symbol.DoesNotExist:
                        new_symbol = Symbol.objects.create(symbol=symbol, symbolDate=today, multiplier=multiplier)
                except Exception, e:
                    print str(e.message)
                    log.write( strftime("%Y-%m-%d %H:%M:%S", time.localtime()) )
                    log.write( "\tGet multiplier of %s from %s failed: %s\n" % (symbol, filepath, str(e.message)) )
                    continue
            else:
                header = False
        file.close()
    log.close()
    
    print "Multipliers acquire finished"
    return


def getSupplement(path, mark_date, account):
    print "Getting supplement marks and calculating reports..."
    filelist = os.listdir(path)
    filelist.sort()
    
    #read all the mark files for mark_date
    for filename in filelist:
        if filename == ".DS_Store":
            continue
        print filename
        
        filepath = os.path.join(path, filename)
        if os.path.isdir(filepath) == True:
            getMultiplierByDate(filepath, mark_date)
            continue
        
        #print filepath
        file = open(filepath, 'rb')
        log = open(ERROR_LOG, "a")
        header = True
        
        #read one mark file
        for row in csv.reader(file.read().splitlines(), delimiter=','): # all marks in this file
            if not header:               
                try:      
                    if row == None or row == "" or len(row) == 0:
                        continue
                    #symbol
                    type = row[6].strip()
                    if type == "SCO" or type == "SPO": # stock option
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
                        if type == "SCO":
                            symbol += date_str + "C" + strike_str
                            #print symbol
                        elif type == "SPO":
                            symbol += date_str + "P" + strike_str
                            #print symbol
                    elif type == "FUTURE" or type == "FPO" or type == "FCO": # future
                        stock = row[5].split('.')[0]
                        if stock == "17": # temp use, build a map later
                            stock = "ZB"
                        if stock == "EW":
                            stock = "SC"
                        if stock == "W1":
                            stock = "1E"
                        if stock == "W4":
                            stock = "4E"
                        
                        time_str = row[5].split('.')[1]
                        year_symbol = time_str[1]
                        month_symbol = time_str[2:]
                        if month_symbol == "01":
                            m_symbol = "F"
                        elif month_symbol == "02":
                            m_symbol = "G"
                        elif month_symbol == "03":
                            m_symbol = "H"
                        elif month_symbol == "04":
                            m_symbol = "J"
                        elif month_symbol == "05":
                            m_symbol = "K"
                        elif month_symbol == "06":
                            m_symbol = "M"
                        elif month_symbol == "07":
                            m_symbol = "N"
                        elif month_symbol == "08":
                            m_symbol = "Q"
                        elif month_symbol == "09":
                            m_symbol = "U"
                        elif month_symbol == "10":
                            m_symbol = "V"
                        elif month_symbol == "11":
                            m_symbol = "X"
                        elif month_symbol == "12":
                            m_symbol = "Z"
                        
                        underlying = stock + m_symbol + year_symbol
                        if type == "FUTURE":
                            symbol = underlying
                        else: # future option                           
                            strike = row[9]
                            if float(strike) == int(strike.split('.')[0]):
                                strike_str = strike.split('.')[0]
                            else:
                                strike_str = strike                                                                              
                            
                            if type == "FCO":
                                symbol = underlying + " C" + strike_str
                            elif type == "FPO":
                                symbol = underlying + " P" + strike_str
                    else: # stock
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
        getReportByDate(mark_date, account)
    
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
            new_report.brokerCommission = 0.0
            new_report.futureCommission = 0.0
            new_report.exchangeFees = 0.0
            new_report.nfaFees = 0.0
            new_report.secFees = 0.0
            new_report.baseMoney = 0.0
            new_report.netPNL = 0.0
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
        if "UNM" not in account:
            mainAccount = account[:5]
        else:
            mainAccount = account[:8]
        new_report = Report.objects.get(Q(account=mainAccount) & Q(symbol=symbol) & Q(reportDate=today))
            
    except Report.DoesNotExist: # today's new does not exist  
        new_report = Report()
        new_report.account = mainAccount
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
    trades = Trade.objects.filter(Q(tradeDate=today) & Q(account__icontains=account))
    for trade in trades:
        try:
            
            # dividend
            if "DIVIDEND" in trade.description:
                new_report = newReport(trade.account, trade.symbol, trade.tradeDate)
                if (new_report.pendingShare != 0 and "DSTP" in trade.description ) or \
                    (new_report.pendingCash != 0.0 and "DIVP" in trade.description):
                    if "PENDING ALERT" not in trade.description:
                        trade.description = "PENDING ALERT: " + trade.description
                if (trade.quantity != 0 and "DSTP" not in trade.description) or \
                    (trade.baseMoney != 0.0 and "DIVP" not in trade.description):
                    if "SETTLED" not in trade.description:
                        trade.description = "SETTLED: " + trade.description
                trade.save()
                RollTrade.objects.create(account=trade.account, symbol=trade.symbol, securityType = trade.securityType,
                                         side=trade.side, quantity=trade.quantity, baseMoney = trade.baseMoney, 
                                         tradeDate=trade.tradeDate, description = trade.description)
                continue
            
                if "JOURNAL" in trade.description :
                    new_report = newReport(trade.account, trade.symbol, trade.tradeDate)
                    if "SETTLED" not in trade.description:
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
            
            # future
            if trade.securityType == "FUTURE" and "UNM" in trade.account:
                try: 
                    futureSymbol = trade.symbol[0:len(trade.symbol)-2]
                    multiplier = FutureMultiplier.objects.get(Q(symbol=futureSymbol)).multiplier
                except FutureMultiplier.DoesNotExist:
                    try:
                        symbol_mark = Symbol.objects.get(Q(symbol=trade.symbol) & Q(symbolDate=trade.tradeDate)) 
                        multiplier = symbol_mark.multiplier
                    except Symbol.DoesNotExist:                    
                        multiplier = 1
                rPrice = trade.price * multiplier
                realPrice = round(rPrice, 2)
                price = realPrice / multiplier
                price = round(price, 6)
                
                try:
                    rtrade = RollTrade.objects.get(Q(account=trade.account) & Q(symbol=trade.symbol) & 
                                                   Q(side=trade.side) & Q(price=price) &
                                                   Q(tradeDate=trade.tradeDate))
                    
                    rtrade.quantity += trade.quantity
                    rtrade.save()
                except RollTrade.DoesNotExist:
                    RollTrade.objects.create(account=trade.account, symbol=trade.symbol, securityType = trade.securityType,
                                         side=trade.side, price=price, quantity=trade.quantity, 
                                         baseMoney = trade.baseMoney, ecnFees=trade.ecnFees, route=trade.route,
                                         destination=trade.destination, broker = trade.broker, liqFlag=trade.liqFlag,
                                         tradeDate=trade.tradeDate, description = trade.description)                    
                continue
                
            # do not roll the trades with Route "BAML", "INSTINET", "ITGI", and exercised trades
            if trade.route == "BAML" or trade.route == "INSTINET" or trade.route == "ITGI" or \
            trade.route == "CMZ" or trade.route == "": 
                if trade.description == "EXERCISE":
                    if trade.symbol == "ARP":
                        price = trade.price * 10
                    else:
                        price = trade.price
                else:
                    price = trade.price
                 
                RollTrade.objects.create(account=trade.account, symbol=trade.symbol, securityType = trade.securityType,
                                         side=trade.side, price=price, quantity=trade.quantity, 
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
    
    return RollTrade.objects.filter(Q(tradeDate=today) & Q(account__icontains=account))

# For exercised or assigned option, the execution price is the average
def getExecutionPrice(account, symbol, tradeDate):
    log = open(ERROR_LOG, "a")
    
    try:
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
    except Exception, e: # old report does not exist
        price = 0.0
        print str(e.message)
        log.write( strftime("%Y-%m-%d %H:%M:%S", time.localtime()) )
        log.write("\tGet execution price of %s in account %s failed: %s\n" % (symbol, account, str(e.message)))
    
    log.close()
    return price

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
    log = open(ERROR_LOG, "a")
    report_list = Report.objects.filter( Q(reportDate = report_date) & Q(account=account) )
    
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
        
        # check multiplier
        try:    
            futureSymbol = symbol[0:len(symbol)-2]
            multiplier = FutureMultiplier.objects.get(Q(symbol=futureSymbol)).multiplier
        except FutureMultiplier.DoesNotExist:
            multiplier = symbol_mark.multiplier
        
        # discard useless report
        if SOD == 0 and buys == 0 and sells == 0 and report.todayCash == 0 and report.todayShare == 0 and \
            report.commission == 0 and report.baseMoney == 0:

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
        
        # realized PNL  
        realizedPNL = common * (sellAve - buyAve)
        if len(symbol.split(' ')) > 1 and "00" in symbol and report.futureCommission == 0.0:
            realizedPNL = realizedPNL * 100 #option
        elif report.futureCommission != 0.0:
            realizedPNL = realizedPNL * multiplier # future
        report.realizedPNL = realizedPNL 
        
        # left shares
        buys -= common
        sells -= common
        unrealizedPNL = (closing - buyAve) * buys + (sellAve - closing) * sells
        if len(symbol.split(' ')) > 1 and "00" in symbol and report.futureCommission == 0.0:
            unrealizedPNL = unrealizedPNL * 100 #option
        elif report.futureCommission != 0.0:
            unrealizedPNL = unrealizedPNL * multiplier
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
            print "Share:"
            print report.account, report.symbol, shareDiffer
        # cash dividend
        if report.pendingCash != report.todayCash:
            cashDiffer = report.todayCash - report.pendingCash
            report.pendingCash = report.todayCash
            report.todayCash = 0.0
            report.netPNL += cashDiffer
            print "Cash:"
            print report.account, report.symbol, cashDiffer
        # check if clear the dividend
        if report.shareClearFlag == True:
            report.pendingShare = 0
            report.todayShare = 0
            report.shareClearFlag = False
        if report.cashClearFlag == True:
            report.pendingCash = 0.0
            report.todayCash = 0.0
            report.cashClearFlag = False
        # even if all the same, also clear today's record
        report.todayCash = 0.0
        report.todayShare = 0
            
        # unrealizedPNL
        report.unrealizedPNL = unrealizedPNL
        # net PNL
        report.netPNL += report.realizedPNL + report.unrealizedPNL# - report.secFees - report.accruedSecFees - report.ecnFees - report.commission
        
        # LMV and SMV
        if EOD >=0:
            if len(symbol.split(' ')) > 1 and "00" in symbol and report.futureCommission == 0.0:
                report.LMV = EOD * closing * 100 #option
            elif report.futureCommission != 0.0:
                report.LMV = EOD * closing * multiplier # future
            else:
                report.LMV = EOD * closing
            report.SMV = 0
        else:
            report.LMV = 0
            if len(symbol.split(' ')) > 1 and "00" in symbol and report.futureCommission == 0.0:
                report.SMV = EOD * closing * 100 #option
            elif report.futureCommission != 0.0:
                report.SMV = EOD * closing * multiplier # future
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
        daily_report.realizedPNL += report.realizedPNL
        daily_report.unrealizedPNL += report.unrealizedPNL
        daily_report.secFees += report.secFees
        daily_report.accruedSecFees += report.accruedSecFees
        daily_report.clearanceFees += report.clearanceFees
        daily_report.brokerCommission += report.brokerCommission
        daily_report.futureCommission += report.futureCommission
        daily_report.exchangeFees += report.exchangeFees
        daily_report.nfaFees += report.nfaFees
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
    try:
        account = Account.objects.get(account=daily_report.account)
        account.realizedPNL += daily_report.realizedPNL
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
            account.realizedPNL += report.realizedPNL
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
        monthly_report.realizedPNL += daily_report.realizedPNL
        monthly_report.unrealizedPNL += daily_report.unrealizedPNL
        monthly_report.secFees += daily_report.secFees
        monthly_report.accruedSecFees += daily_report.accruedSecFees
        monthly_report.clearanceFees += daily_report.clearanceFees
        monthly_report.brokerCommission += daily_report.brokerCommission
        monthly_report.futureCommission += daily_report.futureCommission
        monthly_report.exchangeFees += daily_report.exchangeFees
        monthly_report.nfaFees += daily_report.nfaFees
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
            monthly_report.realizedPNL += dr.realizedPNL
            monthly_report.unrealizedPNL += dr.unrealizedPNL
            monthly_report.secFees += dr.secFees
            monthly_report.accruedSecFees += dr.accruedSecFees
            monthly_report.clearanceFees += dr.clearanceFees
            monthly_report.brokerCommission += dr.brokerCommission
            monthly_report.futureCommission += dr.futureCommission
            monthly_report.exchangeFees += dr.exchangeFees
            monthly_report.nfaFees += dr.nfaFees
            monthly_report.commission += dr.commission
            monthly_report.ecnFees += dr.ecnFees
            monthly_report.netPNL += dr.netPNL
        monthly_report.save()
        
        
def getReportByDate(today, account):
    log = open(ERROR_LOG, "a")
    
    refreshReports(today, account) # create new reports for those symbols have reports last trade date
    
    rollTrades = getRollTrades(today, account)
    
    print "finish rolling " + str(len(rollTrades))
    
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
        
        # if the trade is a cash in
        if "JOURNAL" in rtrade.description:
            if "LIEU" in rtrade.description:
                new_report.todayCash -= rtrade.baseMoney
                new_report.cashClearFlag = True
            elif "JE" in rtrade.description:
                new_report.todayShare += rtrade.quantity
                new_report.shareClearFlag = True
            new_report.save()
            continue
        
        # if the trade is future exchange fee
        if "FUTURE EXCHANGE FEE" in rtrade.description:
            if 'BUY' in rtrade.side:
                new_report.exchangeFees += rtrade.baseMoney
                new_report.commission += rtrade.baseMoney
            else:
                new_report.exchangeFees -= rtrade.baseMoney
                new_report.commission -= rtrade.baseMoney
            new_report.save()
            continue
         
        elif "EXPIRED FUTURE OPTION" in rtrade.description: # expired future option
            if 'BUY' in rtrade.side:
                price = new_report.mark
                new_report.baseMoney -= rtrade.quantity * price
                new_report.EOD -= rtrade.quantity
            else:
                price = new_report.mark
                new_report.baseMoney += rtrade.quantity * price
                new_report.EOD += rtrade.quantity
            new_report.save()
            continue
        
        if "COMBINATION OPTION CASH" in rtrade.description:
            if 'BUY' in rtrade.side:
                new_report.baseMoney -= rtrade.baseMoney
            else:
                new_report.baseMoney += rtrade.baseMoney
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
        if "BUY" not in rtrade.side and rtrade.securityType != "FUTURE" and rtrade.securityType != "FUTOPTION" \
            and rtrade.description != "ASSIGNED OPTION" and rtrade.description != "EXERCISED OPTION":
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
            
            
        if rtrade.securityType != "FUTURE" and rtrade.securityType != "FUTOPTION":
            ## clearance fee
            clearance = rtrade.quantity * 0.0001 # TODO: make this argument as a member of firm
            clearance = round(clearance, 2)            
            if clearance > 3.00:
                clearance = 3.00
            elif clearance < 0.01:
                clearance = 0.01

            futureCommission = 0.0
            exchangeFees = 0.0
            nfaFees = 0.0
        else: ## future fees
            # future commission
            futureCommission = 0.05 * rtrade.quantity
            # future clearing fee, exchange fee
            try:
                futureSymbol = rtrade.symbol[0:len(rtrade.symbol) - 2]
                try:
                    if "UNM" in rtrade.account:
                        report_account = rtrade.account[:8]
                    else:
                        report_account = rtrade.account[:5]
                    groupObj = FutureFeeGroup.objects.get(Q(symbol=futureSymbol) & Q(account=report_account))
                    group = groupObj.group
                except FutureFeeGroup.DoesNotExist:
                        # default
                        if "UNM" in rtrade.account:
                            group = "UNMFeeRate"
                        else:
                            group = "LowerFeeRate"
                
                future = FutureFeeRate.objects.get(Q(symbol = futureSymbol) & Q(group = group))
                clearance = future.clearingFeeRate * rtrade.quantity
                exchangeFees = future.exchangeFeeRate * rtrade.quantity
                nfaFees = future.nfaFeeRate * rtrade.quantity
            except:
                clearance = 0.0
                exchangeFees = 0.0
                nfaFees = 0.0
                
        ## update report
        new_report.clearanceFees += clearance
        new_report.brokerCommission += brokerCommission
        new_report.futureCommission += futureCommission
        new_report.exchangeFees += exchangeFees
        new_report.nfaFees += nfaFees
        new_report.commission += clearance + brokerCommission + futureCommission + exchangeFees + nfaFees
        # for the specific contract broker, we calculate the accrued Sec Fees other than secFees
        if rtrade.broker == "FBCO" or rtrade.broker == "UBS" or rtrade.broker == "BARC":
            new_report.accruedSecFees += secFees
        else:
            new_report.secFees += secFees
        new_report.ecnFees += ecnFees
        new_report.save()            
    
    # delete the rolltrades
#     if today > date(2012, 11, 20):
#         rollTrades.delete()
    
    #getPNLs(today)
    getDailyReport(today, account)
    
    # now delete marks lt today, we do not need them anymore
    Symbol.objects.filter( symbolDate__lt=today ).delete() 
    
    # we may want to delete the security primary exchange info after calculation
    #Security.objects.filter( secDate__lt = today ).delete()
        
    log.write( strftime("%Y-%m-%d %H:%M:%S", time.localtime()) )
    log.write("\tReports calculating done.\n")
    log.close()
            
            
