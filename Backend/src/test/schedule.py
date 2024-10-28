from apscheduler.schedulers.blocking import BlockingScheduler

def my_task():
    print("Task executed!")

scheduler = BlockingScheduler()
scheduler.add_job(my_task, 'interval', seconds=1)  # Run every hour

try:
    scheduler.start()  # Start the scheduler
except (KeyboardInterrupt, SystemExit):
    pass  # Handle exit gracefully
