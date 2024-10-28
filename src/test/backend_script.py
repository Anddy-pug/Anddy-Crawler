import time

def main():
    print("Script started...", flush=True)
    time.sleep(1)  # Simulate some initial processing time

    for i in range(1, 6):  # Simulate a process that runs for a while
        print(f"Processing step {i}...", flush=True)
        time.sleep(2)  # Simulate time-consuming task

    print("Script completed successfully!", flush=True)

if __name__ == "__main__":
    main()
