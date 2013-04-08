import os
from admins.models import Route
import csv

def loadRoutes(filepath):
    header = True
    file = open(filepath, 'rb')
    
    for row in csv.reader(file.read().splitlines(), delimiter='\t'):
        if not header:
            try:
                route = Route()
                route.seqNo = row[0]
                route.routeId = row[1]
                #route.effectiveFrom = row[2]
                #route.effectiveTo = row[3]
                route.flag = row[4]
                route.primaryExchange = row[5]
                route.isETF = row[6]
                route.priceFrom = row[7]
                route.priceTo = row[8]
                route.rebateCharge = row[9]
                route.feeType = row[10]
                route.description = row[11]
                #route.insertedBy = row[12]
                #route.insertedDate = row[13]
                #route.modifiedBy = row[14]
                #route.modifiedDate = row[15]
                route.save() # save into database

            except Exception, e:
                print str(e.message)
                continue
        else:
            header = False
            
    file.close()