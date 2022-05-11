import uuid, os
import hotqueue
import redis
import json

redis_ip = os.environ.get('REDIS_IP')
rd = redis.Redis(host=redis_ip, port=6379, db=0)
q = hotqueue.HotQueue("queue", host=redis_ip, port=6379, db=1)
jdb = redis.Redis(host=redis_ip, port=6379, db=2, decode_responses=True)

def generate_jid():
    """
    Generate a pseudo-random identifier for a job.
    """
    return str(uuid.uuid4())

def _generate_job_key(jid):
    """
    Generate the redis key from the job id to be used when storing, retrieving or updating
    a job in the database.
    """
    return f'job.{jid}'

def instantiate_job(jid, status, start, end):
    """
    Create the job object description as a python dictionary. Requires the job id, status,
    start and end parameters.
    """
    if type(jid) == str:
        return {'jobinfo': {
                    'id': jid,
                    'status': status,
                    'start': start,
                    'end': end
                }
               }
    return {'jobinfo': {
                'id': jid.decode('utf-8'),
                'status': status.decode('utf-8'),
                'start': start.decode('utf-8'),
                'end': end.decode('utf-8')
            }
           }

def _save_job(job_key, job_dict):
    """Save a job object in the Redis database."""
    jdb.hset(job_key, mapping=job_dict)

def _queue_job(jid):
    """Add a job to the redis queue."""
    q.put(jid)

def add_job(jobpayload, start, end, status="submitted"):
    """Add a job to the redis queue."""
    jid = generate_jid()
    job_dict = instantiate_job(jid, status, start, end)
    job_dict.update(jobpayload)
    _save_job(_generate_job_key(jid), job_dict)
    _queue_job(jid)
    return job_dict

def get_job_by_id(jid):
    """Return job dictionary given jid"""
    return (jdb.hgetall(_generate_job_key(jid).encode('utf-8')))

def update_job_status(jid, status):
    """Update the status of job with job id `jid` to status `status`."""
    job = get_job_by_id(jid)
    if job:
        job['jobinfo']['status'] = status
        save_job(generate_job_key(jid), job)
    else:
        raise Exception()
