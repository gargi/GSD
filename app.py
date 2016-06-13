import redis
import json
import unicodedata
import metrics

from flask import Flask, url_for, request, jsonify

app = Flask(__name__)

redis_connection = None

# API endpoint for '/'
@app.route('/')
def api_root():
    return 'Welcome to the System Monitoring Service'

'''
This endpoint will return the current metrics (cpu usage, memory, disk usage and network)
in JSON Format
example: http://localhost:5000/current-metrics
'''
@app.route('/current-metrics')
def get_current_metrics():
    timestamp = request.args.get('timestamp')
    if(timestamp is None):
        curr_object = metrics.Metrics()
        return jsonify(curr_object.get_hardware_metrics()) # return JSON format of hardware_metrics


'''
This following endpoints will return the individual metrics such as
cpu usage, memory, disk usage or network
usage in JSON Format at the current time
example: http://localhost:5000/cpu/current-metrics
'''
@app.route('/cpu_usage/current-metrics')
def get_current_cpu():
    cpu_timestamp = request.args.get('timestamp')
    if(cpu_timestamp is None):
        curr_object = metrics.Metrics()
        return jsonify(curr_object.get_cpu_usage())

@app.route('/memory/current-metrics')
def get_current_memory():
    memory_timestamp = request.args.get('timestamp')
    if(memory_timestamp is None):
        curr_object = metrics.Metrics()
        return jsonify(curr_object.get_memory())

@app.route('/disk_usage/current-metrics')
def get_current_disk():
    disk_timestamp = request.args.get('timestamp')
    if(disk_timestamp is None):
        curr_object = metrics.Metrics()
        return jsonify(curr_object.get_disk_usage())

@app.route('/network_usage/current-metrics')
def get_current_network():
    network_timestamp = request.args.get('timestamp')
    if(network_timestamp is None):
        curr_object = metrics.Metrics()
        return jsonify(curr_object.get_network())

@app.route('/daily-average-metrics')
def get_daily_average():
    average_timestamp = request.args.get('timestamp')
    average_data = redis_connection.get((json.loads(average_timestamp)+"-average"))  # retrieves from redis server using timestamp as key
    if(average_data is None):
        return jsonify(None)
    return jsonify(json.loads(average_data))

'''
This endpoint will return the metrics(cpu usage, memory, disk usage and network)
at any given date in JSON Format
example: http://localhost:5000/daily-metrics?timestamp="13/06/2016"
If there is no metric stored at that time, it will return null
'''
@app.route('/daily-metrics')
def get_daily_metric():
    timestamp = request.args.get('timestamp')
    metrics = redis_connection.zrange(json.loads(timestamp), 0, -1, withscores=False) #retrieves daily metrics from the sorted set
    if (metrics is None):
        return jsonify(None)
    return jsonify({"count": len(metrics), "results": [json.loads(m) for m in metrics]})

'''
This endpoint will return the metrics(cpu usage, memory, disk usage and network)
at any given date and time in JSON Format
example: http://localhost:5000/past-metrics?timestamp="13/06/2016 15:27"
If there is no metric stored at that time, it will return null
'''
@app.route('/past-metrics')
def get_past_metric():
    timestamp = request.args.get('timestamp')
    past_data = redis_connection.get(json.loads(timestamp))  # retrieves from redis server using timestamp as key
    if(past_data is None):
        return jsonify(None)
    return jsonify(json.loads(past_data))

@app.route('/cpu_usage/past-metrics')
def get_past_cpu():
    timestamp = request.args.get('timestamp')
    past_data = redis_connection.get(json.loads(timestamp))
    if(past_data is None):
        return jsonify(None)
    past_data = json.loads(past_data)
    return jsonify(past_data['cpu_usage'])

@app.route('/memory/past-metrics')
def get_past_memory():
    timestamp = request.args.get('timestamp')
    past_data = redis_connection.get(json.loads(timestamp))
    if(past_data is None):
        return jsonify(None)
    past_data = json.loads(past_data)
    return jsonify(v['memory'])

@app.route('/disk_usage/past-metrics')
def get_past_disk_usage():
    timestamp = request.args.get('timestamp')
    past_data = redis_connection.get(json.loads(timestamp))
    if(past_data is None):
        return jsonify(None)
    past_data = json.loads(past_data)
    return jsonify(v['disk_usage'])

@app.route('/network_usage/past-metrics')
def get_past_network_usage():
    timestamp = request.args.get('timestamp')
    past_data = redis_connection.get(json.loads(timestamp))
    if(past_data is None):
        return jsonify(None)
    past_data = json.loads(past_data)
    return jsonify(v['network_usage'])

if __name__ == '__main__':
    if(redis_connection is None):
        redis_connection = redis.Redis("localhost")
    app.run()
