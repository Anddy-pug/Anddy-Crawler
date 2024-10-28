import time
import threading

# Define a global event to control job execution
job_lock = threading.Event()
job_lock.set()  # Initially allow the job to run

def long_running_job():
    """Simulates a long-running job."""
    print("Job started.")
    # Simulate a long task (e.g., 10 seconds)
    time.sleep(10)
    print("Job finished.")

def schedule_job():
    """Schedules the job to run every 5 hours."""
    while True:
        if job_lock.is_set():
            job_lock.clear()  # Lock the job
            thread = threading.Thread(target=long_running_job)
            thread.start()
            thread.join()  # Wait for the job to finish
            job_lock.set()  # Release the lock after the job is done
        else:
            print("Job is still running. Waiting to schedule next job.")
        
        time.sleep(3)  # Wait for 5 hours

if __name__ == "__main__":
    schedule_job()
