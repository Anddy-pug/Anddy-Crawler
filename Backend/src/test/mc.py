import time
import psutil
import os
from multiprocessing import Process

available_cpus = os.cpu_count()

print(f"Available CPU cores: {available_cpus}")

def process_one():
    """Simulates a long-running process."""
    print("Process One: Starting.")
    time.sleep(10)  # Simulate a long task
    print("Process One: Finished.")

def process_two():
    """Simulates another long-running process."""
    print("Process Two: Starting.")
    time.sleep(8)  # Simulate a long task
    print("Process Two: Finished.")

if __name__ == "__main__":
    # Create two processes
    p1 = Process(target=process_one)
    p2 = Process(target=process_two)

    # Start the processes
    p1.start()
    p2.start()

    # Set CPU affinity
    p1_pid = p1.pid
    p2_pid = p2.pid
    
    # Allocate cores (e.g., p1 on CPU 0 and 1, p2 on CPU 2 and 3)
    p1_affinity = {0, 1, 4, 5, 6, 7}  # Process One will use CPU 0 and CPU 1
    p2_affinity = {2, 3, 8, 9, 10, 11}  # Process Two will use CPU 2 and CPU 3

    # Set CPU affinity for the processes
    p1_cpu_affinity = psutil.Process(p1_pid)
    p2_cpu_affinity = psutil.Process(p2_pid)

    p1_cpu_affinity.cpu_affinity(p1_affinity)
    p2_cpu_affinity.cpu_affinity(p2_affinity)

    # Wait for the processes to finish
    p1.join()
    p2.join()

    print("Both processes have finished.")
