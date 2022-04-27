q = HotQueue("some_queue", host="<Redis_IP>", port=6379, db=1)

@q.worker
def do_work(item):
    # do something with item...

do_work()
