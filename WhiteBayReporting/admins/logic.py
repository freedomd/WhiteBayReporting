import os
from admins.models import Route
import csv

def loadRoutes(filepath):
    header = True
    file = open(filepath, 'rb')
    
    for row in csv.reader(file.read().splitlines(), delimiter=','):
        if not header:
            try:
                route = Route()
                route.seqNo = row[0]
                route.routeId = row[1]
                #route.effectiveFrom = row[2]
                #route.effectiveTo = row[3]
                route.flag = row[4]
                primary = row[5]
                route.primaryExchange = primary
                if primary == "NYSE":
                    route.tape = "A"
                elif primary == "AMEX" or primary == "ARCA":
                    route.tape = "B"
                elif primary == "ALL":
                    route.tape = "ALL"
                else:
                    route.tape = "C"
                route.isETF = row[6]
                route.priceFrom = row[7]
                route.priceTo = row[8]
                route.rebateCharge = row[9]
                route.feeType = row[10]
                #route.description = row[11]
                #route.insertedBy = row[12]
                #route.insertedDate = row[13]
                #route.modifiedBy = row[14]
                #route.modifiedDate = row[15]
                route.save() # save into database

            except Exception, e:
                print route.seqNo + ", " + route.routeId
                print str(e.message)
                continue
        else:
            header = False
            
    file.close()