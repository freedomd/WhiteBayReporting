from celery import Celery
from celery import task
from celery.task import PeriodicTask
from reports.logic import *
from datetime import date
celery = Celery('tasks', broker='redis://localhost')

@celery.task
def add(x, y):
    print x + y
    return x + y

@celery.task
def get_report():
    today = date.today()
    if not getMarks(today): # get marks, create report
        # write to log in the future
        print "Cannot get mark file."
        return 
    if not getReport(today): # pre-calculated
        print "Cannot get trade file."
        return 
