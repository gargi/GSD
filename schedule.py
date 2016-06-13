import metrics
import logging
import time

reload(metrics)

from apscheduler.schedulers.blocking import BlockingScheduler

logging.basicConfig()

sched = BlockingScheduler()
'''
This function stores the performance metrics in the redis server every minute
 with the timestamp as the key and the hardware_metrics as the value
'''
@sched.scheduled_job('interval', minutes = 1)
def minute_job():
    print('Performance metrics are stored')
    metrics.Metrics().get_minute_metrics()

'''
This function stores the performance metrics in the redis server every hour
with the date as the key and the hardware_metrics as the value.
These keys are sorted from the beginning of the day till the end
'''
@sched.scheduled_job('interval', minutes = 60)
def hour_job():
    print('Hourly performance metrics are stored')
    metrics.Metrics().set_day_aggregate()
    metrics.Metrics().get_hour_metrics()

'''
KeyboardInterrupt will stop the monitoring Service
'''
try:
    sched.start()
except (KeyboardInterrupt):
    logging.debug('Got SIGTERM! Terminating...')
