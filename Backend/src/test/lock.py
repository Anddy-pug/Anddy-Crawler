import multiprocessing
import time

def modify_status(job_status):
    with job_status.get_lock():
        # Only this process can execute this block at a time
        print("Setting job status to True")
        job_status.value = True
        time.sleep(5)  # Simulate some processing

def read_status(job_status):
    with job_status.get_lock():
        # Only this process can execute this block at a time
        print(f"Current job status: {job_status.value}")

if __name__ == "__main__":
    job_status = multiprocessing.Value('b', False)

    process_modify = multiprocessing.Process(target=modify_status, args=(job_status,))
    process_read = multiprocessing.Process(target=read_status, args=(job_status,))

    process_modify.start()
    time.sleep(1)  # Ensure that the modify process starts first
    process_read.start()

    process_modify.join()
    process_read.join()
