from flask_socketio import SocketIO, emit
from threading import Thread, Lock, Event
import os
import subprocess
import time
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sys
import multiprocessing
from datetime import datetime
from setting.setting_manager import *
import logging


# current_dir = os.path.dirname(os.path.abspath(__file__))
# parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
# sys.path.append(parent_dir)
job_lock = Lock()
job_lock_file = Lock()


background_thread_file = None
background_thread_web = None

file_threads = {}
file_threads_list = {}
web_threads = {}
web_threads_list = {}
logger_list = {}
web_console = {}
stop_events = {}


app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing (CORS)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins='*')


# Global variable to hold process output
console_log = []
file_log = []
web_log = []

# When the client connects, send the current log and continue sending new logs
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    username = request.args.get('username')
    print(f'Client connected: {request.sid} with username: {username}')
    # Send the previous console log to the newly connected client
    # if username == "file":    
    #     for line in file_log:
    #         socketio.emit('file_console_output', line)
    # elif username == "web":
    #     for line in web_log:
    #         socketio.emit('web_console_output', line)
    
    socketio.emit('job_status', web_threads_list)
    

        
@socketio.on('start_file_process')
def handle_start_file_process(data):
    name = data['username']
    start_background_process('file', name)
    emit('process_started', {'message': 'File Crawling Process has been started.'})
    
    
@socketio.on('start_web_process')
def handle_start_web_process(data):
    name = data['username']
    start_background_process('web', name)
    emit('process_started', {'message': 'Web Crawling Process has been started.'})  
      
@socketio.on('stop_process')
def handle_stop_web_process(data):
    name = data['username']
    stop_background_process(name)
    emit('process_started', {'message': 'Web Crawling Process has been started.'})


def stop_background_process(name):
    global background_thread_file
    stop_events[name].set()
    if name in web_threads:
        web_threads[name].join()
        del web_threads[name]
        # del web_console[name]
    if name in file_threads:
        file_threads[name].join()
        del file_threads[name]
    del web_threads_list[name]
    background_thread_file = None

def run_file_crawling(name):
    
    web_console[name] = []
    
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../src/crawler_file/monitor.py')
    process = subprocess.Popen(
        ['python', config_path, '--crawler_name', name, '--crawler_type', 'file'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding='utf-8'  # Specify the encoding
    )
    
    try:    

        while not stop_events[name].is_set():
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())  # Print the output to the server console
                file_log.append(output.strip())  # Save the output in the log
                web_console[name].append(output.strip())  # Save the output in the log
                logger_list[name].info(output.strip())
                socketio.emit(name, output.strip())  # Send to connected clients
            
    finally:
        # Ensure that the process is terminated when stopping
        if process.poll() is None:  # If process is still running
            process.terminate()  # Send SIGTERM to the process
            try:
                process.wait(timeout=5)  # Wait for process to exit gracefully
            except subprocess.TimeoutExpired:
                process.kill()  # Force kill if it doesn't terminate in time
            print(f"Process for {name} terminated")
            
            
    del stop_events[name]
    print('Process finished')

def web_process(name):
    
    config_path = ''
    output = "web_crawling: " + name + " is started: " + datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %H:%M:%S")
    web_console[name].append(output.strip())
    socketio.emit(name, output.strip())
    print(output.strip())
    
    crawler_setting = get_crawler_setting(name, 'web')
    web_type = crawler_setting['webContentsType']
    directory = './'
    match web_type:
        case "Static Web Contents":
            directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../src/crawler_web/static/school/school_spider/school_spider/')
            command = ['scrapy', 'crawl', 'react_spider', '-a', 'myconfig=' + name]
        case "Dynamic Web Contents":
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../src/crawler_web/dynamic/dynamic_web_crawler.py')
            command = ['python', config_path, '--crawler_name', name, '--crawler_type', 'web']
            # return "Weekend"
        case "NextCloud":
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../src/crawler_web/dynamic/nextcloud.py')
            command = ['python', config_path, '--crawler_name', name, '--crawler_type', 'web']
        case "OpenProject":
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../src/crawler_web/dynamic/openproject.py')
            command = ['python', config_path, '--crawler_name', name, '--crawler_type', 'web']
    
    
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding='utf-8',  # Specify the encoding
        cwd=directory  # Optional: Set the working directory
    )
    
    try:
    
        while not stop_events[name].is_set():
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())  # Print the output to the server console
                web_console[name].append(output.strip())  # Save the output in the log
                logger_list[name].info(output.strip())
                socketio.emit(name, output.strip())  # Send to connected clients            
                
        print('Process finished')
    
    finally:
        # Ensure that the process is terminated when stopping
        if process.poll() is None:  # If process is still running
            process.terminate()  # Send SIGTERM to the process
            try:
                process.wait(timeout=5)  # Wait for process to exit gracefully
            except subprocess.TimeoutExpired:
                process.kill()  # Force kill if it doesn't terminate in time
            print(f"Process for {name} terminated")
            
            
    output = "web_crawling: " + name + " is finished: " + datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %H:%M:%S")
    web_console[name].append(output.strip())
    # socketio.emit('web_console_output_' + name, output.strip())
    socketio.emit(name, output.strip())
    print(output.strip())


def run_web_crawling(name):
    web_console[name] = []
    crawler_setting = get_crawler_setting(name, 'web')
    interval_time = crawler_setting['crawlingTime']
    while not stop_events[name].is_set():
        with job_lock:
            web_console[name] = []    
            start_time = time.perf_counter()
            # Ensure thread-safe access
            web_process(name)
            end_time = time.perf_counter()
            web_console[name].append(get_duration(start_time, end_time))
        if stop_events[name].is_set():
            break
        time.sleep(int(interval_time))
    del stop_events[name]
    print(name + " is finished")

def create_logger(name):
    # Generate a timestamped log file name
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')  # Format: YYYYMMDD_HHMMSS
    log_file_name = f'{name}_{timestamp}.log'  # Create log file name

    # Create a logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)  # Set log level

    # Create a file handler
    file_handler = logging.FileHandler('logs/' + log_file_name)
    file_handler.setLevel(logging.INFO)  # Set level for file handler

    # Create a formatter and set it for the handler
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Add the file handler to the logger
    logger.addHandler(file_handler)

    return logger

def start_background_process(type, job = "default_job"):
    
    stop_event = Event()  # Create a separate stop event for each thread
    stop_events[job] = (stop_event)   # Store the stop event
    
    logger_list[job] = create_logger(job)

    
    global background_thread_file, background_thread_web
    if type == 'file' and background_thread_file is None:
        
        if job not in file_threads:
            thread = Thread(target=run_file_crawling, args=(job,))
            background_thread_file = thread
            file_threads[job] = thread
            web_threads_list[job] = ""
            thread.daemon = True  # Optional: ensures thread exits when main program does
            thread.start()
        
        # background_thread_file = Thread(target=run_file_crawling)
        # background_thread_file.daemon = True  # Optional: ensures thread exits when main program does
        # background_thread_file.start()
    elif type == 'web':
        if job not in web_threads:
            thread = Thread(target=run_web_crawling, args=(job,))
            web_threads[job] = thread
            web_threads_list[job] = ""
            thread.daemon = True  # Optional: ensures thread exits when main program does
            thread.start()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/set_job', methods=['POST'])
def set_job():
    data = request.get_json()  # Get JSON data from request
    base_output_directory = './crawling_setting/'  # Change this to your base directory

    # Determine the output directory based on crawlingType
    if data['crawlingType'] == 'File Crawling':
        output_directory = os.path.join(base_output_directory, 'file')
    elif data['crawlingType'] == 'Web Crawling':
        output_directory = os.path.join(base_output_directory, 'web')
    else:
        output_directory = os.path.join(base_output_directory, 'other')  # Fallback directory
    
    save_setting(data, data['jobName'], output_directory)
    # Sending a response back to the frontend
    return jsonify({"message": "Form submitted successfully!"})

# curl -X POST http://localhost:5000/submit -H "Content-Type: application/json" -d "{\"name\": \"John Doe\", \"email\": \"johndoe@example.com\"}"


@app.route('/get_jobs', methods=['GET'])
def get_yaml_data():
    
    absolute_directory_web = os.path.abspath('./crawling_setting/web')
    absolute_directory_file = os.path.abspath('./crawling_setting/file')
    
    try:
        # Get YAML files from both web and file directories
        web_data = get_settings(absolute_directory_web)
        file_data = get_settings(absolute_directory_file)
        
        # Combine both lists
        combined_data = {
            "web_files": web_data,
            "file_files": file_data
        }
        
        return jsonify(combined_data), 200  # Return combined data as JSON
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/get_console', methods=['GET'])
def get_console():
    
    name = request.args.get('job_name')
    
    response_data = {}
    
    response_data[name] = web_console[name]
    
    return jsonify(response_data)


@app.route('/set_setting', methods=['POST'])
def set_setting():
    data = request.get_json()  # Get JSON data from request
    base_output_directory = './crawling_setting/'  # Change this to your base directory

    # Determine the output directory based on crawlingType
    output_directory = os.path.join(base_output_directory, 'other')  # Fallback directory
    
    if 'thumbnail_url' in data:
        filename = "thumbnail"
    if 'elasticsearch_url' in data:
        filename = "elasticsearch"
    if 'textembedding_url' in data:
        filename = "embedding"
    
    save_setting(data, filename, output_directory)
    # Sending a response back to the frontend
    return jsonify({"message": "Form submitted successfully!"})

@app.route('/get_setting', methods=['GET'])
def get_setting():
    
    absolute_directory_other = os.path.abspath('./crawling_setting/other')
    
    try:
        # Get YAML files from both web and file directories
        other_data = get_settings(absolute_directory_other)
        
        # Combine both lists
        combined_data = {
            "other_files": other_data
        }
        
        return jsonify(combined_data), 200  # Return combined data as JSON
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/delete_job', methods=['DELETE'])
def delete_job():
    
    try:
        # Get the job details from the request body
        data = request.get_json()
        job_name = data.get('job_name')
        job_type = data.get('job_type')

        absolute_directory_web = os.path.abspath('./crawling_setting/web/')
        absolute_directory_file = os.path.abspath('./crawling_setting/file/')

        if job_type == 'Web Crawling':
            delete_setting(data, job_name, absolute_directory_web)
            return jsonify({"message": f"Job '{job_name}' of type '{job_type}' deleted successfully"}), 200
        elif job_type == 'File Crawling':
            delete_setting(data, job_name, absolute_directory_file)
            return jsonify({"message": f"Job '{job_name}' of type '{job_type}' deleted successfully"}), 200
        else:
            return jsonify({"error": "Invalid job type"}), 400

    except Exception as e:
        # Handle any errors during the process
        return jsonify({"error": str(e)}), 400
    
@app.route('/get_logs', methods=['GET'])
def get_logs():
    log_data = {}
    LOG_DIRECTORY = os.path.dirname(os.path.abspath(__file__)) + '\\logs'
    for filename in os.listdir(LOG_DIRECTORY):
        if filename.endswith('.log'):  # Adjust the file extension as needed
            file_path = os.path.join(LOG_DIRECTORY, filename)

            # Read the contents of the log file
            with open(file_path, 'r') as log_file:
                content = log_file.read()
                log_data[filename] = content  # Store content with filename as key

    # Return log data as JSON
    return jsonify(log_data)



if __name__ == '__main__':
    # get_yaml_data()
    # Start the background process when the server starts
    
    thumnail_setting = get_thumbnail_setting()
    
    thumnail_url = thumnail_setting['thumbnail_url']
    
    command = ['python', '-m', 'http.server', '4444', '--directory', thumnail_url]
    
    
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding='utf-8',  # Specify the encoding
    )
    
    

    
    # start_background_process()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, use_reloader=False)
    
    