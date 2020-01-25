from multiprocessing import Process
from datetime import date, timedelta
import time
from redis import Redis


channels = [
    'New York',
    'Bucharest',
    'Berlin',
    'Barcelona',
    'Paris',
    'London',
    'Frankfurt',
    'Amsterdam'
]


def pub(myredis):
    end_date = date(2019, 6, 10)
    current_date = date.today()
    delta = end_date - current_date
    for i in range(delta.days):
        departure_date = current_date + timedelta(days=i)
        for channel in channels:
            myredis.publish(channel, departure_date.strftime('%d/%m/%Y'))
            # time.sleep(5)


def default_sub(myredis, name):
    pubsub = myredis.pubsub()
    pubsub.subscribe([name])
    for item in pubsub.listen():
        print('Finding flights from {} on {}'.format(name, item['data']))


def start_automation_server():
    myredis = Redis(host='redis', port=6379)
    # while True:
    #     Process(target=pub, args=(myredis,)).start()
        # Process(target=default_sub, args=(myredis, 'New York')).start()
        # Process(target=default_sub, args=(myredis, 'Barcelona')).start()
        # Process(target=default_sub, args=(myredis, 'Berlin')).start()
        # Process(target=default_sub, args=(myredis, 'London')).start()
        # Process(target=default_sub, args=(myredis, 'Paris')).start()
        # Process(target=default_sub, args=(myredis, 'Frankfurt')).start()
        # Process(target=default_sub, args=(myredis, 'Amsterdam')).start()