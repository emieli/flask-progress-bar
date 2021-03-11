from api_phpipam import phpipam
from time import sleep

from rq import get_current_job

def task_create_host(**kwargs):

    job = get_current_job()
    job.meta = {'message': "Job started", 'progress': 25}
    job.save_meta()
    # job.meta = {'message': "Job failed due to retarded reason"}
    # job.save_meta()
    # raise RuntimeError

    sleep(1)
    ipam = phpipam()
    if not ipam.token:
        raise Exception("Failed to connect to IPAM")

    sleep(1)
    host = ipam.get_address(**kwargs)    
    if host:
        return f"{host[0]['hostname']} already exists, no action."

    job.meta = {'message': "Hostname not found, creating", 'progress': 50}
    job.save_meta()

    sleep(1)
    host = ipam.create_address(subnet_id = 265, payload = {'hostname': kwargs['hostname']})    
    if host:
        return "success!"

    return