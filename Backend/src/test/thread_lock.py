import threading
import time

# Shared variable
job_status = False
lock = threading.Lock()

def modify_status():
    global job_status
    with lock:
        # Only this thread can execute this block at a time
        print("Setting job status to True")
        job_status = True
        time.sleep(5)  # Simulate some processing

def read_status():
    with lock:
        # Only this thread can execute this block at a time
        print(f"Current job status: {job_status}")

if __name__ == "__main__":
    # Create threads
    thread_modify = threading.Thread(target=modify_status)
    thread_read = threading.Thread(target=read_status)

    # Start the modify thread
    thread_modify.start()
    time.sleep(1)  # Ensure that the modify thread starts first

    # Start the read thread
    thread_read.start()

    # Wait for both threads to finish
    thread_modify.join()
    thread_read.join()
