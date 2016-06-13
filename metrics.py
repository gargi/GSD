import psutil
import redis
import json
import datetime

from time import strftime

class Metrics(object):

    redis_connection = None

    def __init__(self):
        self.setup_redis();
        self.hardware_metrics = {}
        self.hardware_metrics['cpu_usage'] = self.get_cpu_usage()
        self.hardware_metrics['memory'] = self.get_memory()
        self.hardware_metrics['disk_usage'] = self.get_disk_usage()
        self.hardware_metrics['network_usage'] = self.get_network()

    '''
    This function will store the performance metrics in the Redis server
    with the timestamp in the format of %d/%m/%Y %H:%M as the key.
    It will return the metrics to the current_metrics API call
    '''

    def get_hardware_metrics(self):
        self.redis_connection.set(self.get_timestamp(),  json.dumps(self.hardware_metrics, ensure_ascii=False))
        return self.hardware_metrics

    '''
    This function will store the performance metrics in the Redis server
    with the timestamp in the format of %d/%m/%Y %H:%M as the key at
    every minute
    '''
    def get_minute_metrics(self):
        self.redis_connection.set(self.get_timestamp(),  json.dumps(self.hardware_metrics, ensure_ascii=False))
    '''
     This function will store the performance metrics in the Redis server with
     the date as the key in the format of %d/%m/%Y as a sorted set at every hour.
     In this sorted set the keys are arranged by their score which is the hour
     of the day. I have used 24 hour clock.
    '''
    def get_hour_metrics(self):
        self.redis_connection.zadd(self.get_date(), json.dumps(self.hardware_metrics, ensure_ascii=False), datetime.datetime.now().hour)
        self.set_day_aggregate()
    '''
    This function will store the average in the system every hour.
    This can then be used for retrieving the average of the day.
    '''
    def set_day_aggregate(self):
        metrics = self.redis_connection.zrange(self.get_date(), 0, -1, withscores=False)
        cpu_sum = {}
        memory_sum = {}
        disk_usage_sum = {}
        network_usage_sum = {}
        for metric in metrics:
            tmp_metric = json.loads(metric)
            for k,v in tmp_metric['cpu_usage'].items():
                if (k not in cpu_sum):
                    cpu_sum[k] = v
                else:
                    cpu_sum[k] = cpu_sum[k] + v
            for k,v in tmp_metric['memory'].items():
                if (k not in memory_sum):
                    memory_sum[k] = v
                else:
                    memory_sum[k] = memory_sum[k] + v

            for k,v in tmp_metric['disk_usage'].items():
                if (k not in disk_usage_sum):
                    disk_usage_sum[k] = v
                else:
                    disk_usage_sum[k] = disk_usage_sum[k] + v

            for k,v in tmp_metric['network_usage'].items():
                if (k not in network_usage_sum):
                    network_usage_sum[k] = v
                else:
                    network_usage_sum[k] = network_usage_sum[k] + v

        cpu_usage = {}
        memory_usage = {}
        network_usage = {}
        disk_usage = {}
        for k,v in cpu_sum.items():
            cpu_usage[k] = v/len(metrics)

        for k,v in memory_sum.items():
            memory_usage[k] = v/len(metrics)

        for k,v in network_usage_sum.items():
            network_usage[k] = v/len(metrics)

        for k,v in disk_usage_sum.items():
            disk_usage[k] = v/len(metrics)

        self.average_metrics = {}
        self.average_metrics['average_cpu_usage'] = cpu_usage
        self.average_metrics['average_memory'] = memory_usage
        self.average_metrics['average_disk_usage'] = disk_usage
        self.average_metrics['average_network_usage'] = network_usage

        self.redis_connection.set(self.get_date()+"-average",  json.dumps(self.average_metrics, ensure_ascii=False))

    # This function establishes redis connection
    def setup_redis(self):
        if(self.redis_connection is None):
            self.redis_connection = redis.Redis("localhost")

    '''
    This function will return the date which is used as the key for
    sorted set in the get_hour_metrics function
    '''
    def get_date(self):
        date = strftime("%d/%m/%Y")
        return date

    '''
    This function will return the date and time which is used as the key
    for sorted set in the get_minute_metrics function
    '''
    def get_timestamp(self):
        timestamp = strftime("%d/%m/%Y %H:%M")
        return timestamp

    # This function will return the cpu usage
    def get_cpu_usage(self):
        cpu_usage = {}
        cpu_time_metrics = psutil.cpu_times()
        cpu_usage['user'] = cpu_time_metrics.user
        cpu_usage['system'] = cpu_time_metrics.system
        cpu_usage['idle'] = cpu_time_metrics.idle
        cpu_usage['percent'] = psutil.cpu_percent(interval=1)
        cpu_usage['count'] = psutil.cpu_count()
        return cpu_usage

    # This function will return the virtual and swap memory
    def get_memory(self):
        memory = {}
        virtual_memory_metrics = psutil.virtual_memory()
        memory['virtual_total'] = virtual_memory_metrics.total
        memory['virtual_used'] = virtual_memory_metrics.used
        memory['virtual_free'] = virtual_memory_metrics.free
        swap_memory_metrics = psutil.swap_memory()
        memory['swap_total'] = swap_memory_metrics.total
        memory['swap_used'] = swap_memory_metrics.used
        memory['swap_free'] = swap_memory_metrics.free
        return memory

    # This function will return the disk used, total and free
    def get_disk_usage(self):
        disk_usage = {}
        disk_usage_metrics = psutil.disk_usage('/')
        disk_usage['total'] = disk_usage_metrics.total
        disk_usage['used'] = disk_usage_metrics.used
        disk_usage['free'] = disk_usage_metrics.free
        return disk_usage

    '''
    This function will return the bytes sent, received and packets
    send and received in the network
    '''
    def get_network(self):
        network_usage = {}
        network_usage_metrics = psutil.net_io_counters()
        network_usage['bytes_sent'] = network_usage_metrics.bytes_sent
        network_usage['bytes_received'] = network_usage_metrics.bytes_recv
        network_usage['packets_sent'] = network_usage_metrics.packets_sent
        network_usage['packets_received'] = network_usage_metrics.packets_recv
        return network_usage
