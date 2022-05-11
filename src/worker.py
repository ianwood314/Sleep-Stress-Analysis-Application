from jobs import q, update_job_status
import hotqueue
import os
import time

redis_ip = os.environ.get('REDIS_IP')
q = hotqueue.HotQueue("Queue", host=redis_ip, port=6379, db=1)

@q.worker
def execute_job(jid):
    """
    Retrieve a job id from the task queue and execute the job.
    Monitors the job to completion and updates the database accordingly.
    """
    # fill in ...
    # the basic steps are:
    # 1) get job id from message and update job status to indicate that the job has started
    # 2) start the analysis job and monitor it to completion.
    # 3) update the job status to indicate that the job has finished.
    update_job_status(jid, "in progress")
    time.sleep(5)
    print(jid)
    update_job_status(jid, "complete")

execute_job()
