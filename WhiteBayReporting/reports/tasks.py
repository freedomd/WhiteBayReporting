from celery import Celery
from celery import task
from celery.task import PeriodicTask
from reports.logic import *
celery = Celery('tasks', broker='redis://localhost')

@celery.task
def add(x, y):
    print x + y
    return x + y

@celery.task
def get_report():
    getMarks()
    getReport() # pre-calculated
