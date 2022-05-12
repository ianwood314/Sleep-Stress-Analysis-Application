from hotqueue import HotQueue
import json
import os
import redis
import matplotlib.pyplot as plt
import subprocess
from jobs import q, rd, jdb, update_job_status, img_db
import time

@q.worker
def execute_job(jid):
    print('executing job...')
    update_job_status(jid, 'in progress')

    jdb.hset(f'job.{jid}', 'status', 'finished')

execute_job()
