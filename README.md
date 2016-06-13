### PinDrop GSD

Requirements :
* Python 2.7
* pip 8.1.2
* pip install virtualenv (To avoid dependency issues with existing packages)
* Redis

The following command will install required packages
```
pip install -r Requirements.txt
```

Instructions:
1. First start redis server by the following command:
```
/usr/bin/redis-server
/usr/bin/redis-cli
```
2. Run schedule.py
```
python schedule.py
```
This script will store the performance metrics in the Redis database every minute with the timestamp(date and time in the format of %d/%m/%Y %H:%M) as the key and performance metrics as the value. These can be then retreived from the database using API endpoints.
It will also store the performance metrics with date as the key and hour as the score in a sorted set. This is used to retrieve all the metrics of a particular date in sorted order.
It also stores the average metrics in the database every hour. This is used for calculating the average of the day.
This can be stopped by ctrl+c.

3. Run app.py
```
python app.py
```
This will start my application which is at localhost:5000. This can be used to retrieve metrics at various points in time.

#### Explanation

I am used Redis which is "NoSQL" key-value data store as my database as it provides fast storage, retrieval and on disk persistence.
I have stored the following performance metrics with timestamp as the key:
CPU -
1. user
2. System
3. idle
4. percent
5. Count

Memory -
1. Total virtual memory
2. Used virtual memory
3. Available virtual memory
4. Total swap memory
5. Used swap memory
6. Available swap memory

Disk -
1. Total disk space
2. Used disk space
3. Available disk space

Network -
1. Bytes sent
2. Bytes received
3. Packets sent
4. Packets received

#### API Endpoints explained

1. By using http://localhost:5000/current-metrics the current state of the machine in retreived in the JSON format.
For example:
````
{
  "cpu_usage": {
    "count": 4,
    "idle": 1257240.97,
    "percent": 5.5,
    "system": 62127.1,
    "user": 105789.17
  },
  "disk_usage": {
    "free": 364984438784,
    "total": 499088621568,
    "used": 133842038784
  },
  "memory": {
    "swap_free": 1398013952,
    "swap_total": 2147483648,
    "swap_used": 749469696,
    "virtual_free": 106319872,
    "virtual_total": 8589934592,
    "virtual_used": 5388840960
  },
  "network_usage": {
    "bytes_received": 13701580464,
    "bytes_sent": 1207014140,
    "packets_received": 12296836,
    "packets_sent": 8520305
  }
}
```

2. The state of the machine can be retrieved from a point of time in the past by specifying the date and time in the format of %d/%m/%Y %H:%M. For example:
http://localhost:5000/past-metrics?timestamp="13/06/2016 18:06"
```
{
  "cpu_usage": {
    "count": 4,
    "idle": 1258006.18,
    "percent": 5.0,
    "system": 62165.83,
    "user": 105851.3
  },
  "disk_usage": {
    "free": 364985602048,
    "total": 499088621568,
    "used": 133840875520
  },
  "memory": {
    "swap_free": 1326186496,
    "swap_total": 2147483648,
    "swap_used": 821297152,
    "virtual_free": 168284160,
    "virtual_total": 8589934592,
    "virtual_used": 5487947776
  },
  "network_usage": {
    "bytes_received": 13701802604,
    "bytes_sent": 1207099734,
    "packets_received": 12297875,
    "packets_sent": 8521096
  }
}
```

#### Bonus API Points
1. I have added an API endpoint which can be used to view average metrics of a day. This can be obtained by entering the date as a string in the timestamp field of the query. For example:
http://localhost:5000/daily-average-metrics?timestamp="13/06/2016"
```
{
  "average_cpu_usage": {
    "count": 4,
    "idle": 1271170.6666666667,
    "percent": 2.033333333333333,
    "system": 62661.299999999996,
    "user": 106881.81
  },
  "average_disk_usage": {
    "free": 364981652138,
    "total": 499088621568,
    "used": 133844825429
  },
  "average_memory": {
    "swap_free": 833093632,
    "swap_total": 2147483648,
    "swap_used": 1314390016,
    "virtual_free": 95364437,
    "virtual_total": 8589934592,
    "virtual_used": 5962519893
  },
  "average_network_usage": {
    "bytes_received": 13706497696,
    "bytes_sent": 1208545998,
    "packets_received": 12313463,
    "packets_sent": 8532646
  }
}
```
1. I have added API points which can be used to view individual metrics such as CPU usage, Disk Usage, Network or Memory at the current time or at some time in the past.
Example is as follows:
http://localhost:5000/cpu_usage/past-metrics?timestamp="13/06/2016 18:06"
```
{
  "count": 4,
  "idle": 1258006.18,
  "percent": 5.0,
  "system": 62165.83,
  "user": 105851.3
}
```

http://localhost:5000/disk_usage/current-metrics
```
{
  "free": 364991029248,
  "total": 499088621568,
  "used": 133835448320
}
```

2. I have added API points to view a summary of the performance metrics for an entire day.This API would present the metrics in sorted form according to the hour. These can be retrived by entering the date as a string for the timestamp.
For example:
http://localhost:5000/daily-metrics?timestamp="13/06/2016"
```
{
  "count": 3,
  "results": [
    {
      "cpu_usage": {
        "count": 4,
        "idle": 1271132.16,
        "percent": 1.2,
        "system": 62660.81,
        "user": 106880.82
      },
      "disk_usage": {
        "free": 364985417728,
        "total": 499088621568,
        "used": 133841059840
      },
      "memory": {
        "swap_free": 833093632,
        "swap_total": 2147483648,
        "swap_used": 1314390016,
        "virtual_free": 132849664,
        "virtual_total": 8589934592,
        "virtual_used": 5915197440
      },
      "network_usage": {
        "bytes_received": 13706490940,
        "bytes_sent": 1208539315,
        "packets_received": 12313417,
        "packets_sent": 8532602
      }
    },
    {
      "cpu_usage": {
        "count": 4,
        "idle": 1271171.24,
        "percent": 1.2,
        "system": 62661.31,
        "user": 106881.23
      },
      "disk_usage": {
        "free": 364979769344,
        "total": 499088621568,
        "used": 133846708224
      },
      "memory": {
        "swap_free": 833093632,
        "swap_total": 2147483648,
        "swap_used": 1314390016,
        "virtual_free": 92917760,
        "virtual_total": 8589934592,
        "virtual_used": 5964640256
      },
      "network_usage": {
        "bytes_received": 13706497563,
        "bytes_sent": 1208545874,
        "packets_received": 12313464,
        "packets_sent": 8532648
      }
    },
    {
      "cpu_usage": {
        "count": 4,
        "idle": 1271208.6,
        "percent": 3.7,
        "system": 62661.78,
        "user": 106883.38
      },
      "disk_usage": {
        "free": 364979769344,
        "total": 499088621568,
        "used": 133846708224
      },
      "memory": {
        "swap_free": 833093632,
        "swap_total": 2147483648,
        "swap_used": 1314390016,
        "virtual_free": 60325888,
        "virtual_total": 8589934592,
        "virtual_used": 6007721984
      },
      "network_usage": {
        "bytes_received": 13706504586,
        "bytes_sent": 1208552807,
        "packets_received": 12313508,
        "packets_sent": 8532690
      }
    }
  ]
}
```
