# setting_manager.py

import yaml
from typing import Any
import os

class ConfigError(Exception):
    """Custom exception for configuration errors."""
    pass

class ElasticsearchConfig:
    def __init__(self, config: dict):
        try:
            self.url = config['url']
            self.username = config['username']
            self.password = config['password']
            self.fingerprint = config['fingerprint']
            self.index = IndexConfig(config.get('index', {}))
        except KeyError as e:
            raise ConfigError(f"Missing Elasticsearch configuration key: {e}")

class IndexConfig:
    def __init__(self, config: dict):
        try:
            self.web_index = config['web_index']
            self.file_index = config['file_index']
        except KeyError as e:
            raise ConfigError(f"Missing Index configuration key: {e}")

class WebcrawlerConfig:
    def __init__(self, config: dict):
        try:
            self.type = config['type']
            self.login_url = config['login_url']
            self.username = config['username']
            self.password = config['password']
            self.username_field_id = config['username_field_id']
            self.password_field_id = config['password_field_id']
            self.submit_button_id = config['submit_button_id']
            self.base_url = config['base_url']
            self.not_url = config['not_url']
        except KeyError as e:
            raise ConfigError(f"Missing Webcrawler configuration key: {e}")

class FilecrawlerConfig:
    def __init__(self, config: dict):
        try:
            self.url = config['url']
        except KeyError as e:
            raise ConfigError(f"Missing Filecrawler configuration key: {e}")

class CrawlerConfig:
    def __init__(self, config: dict):
        try:
            self.webcrawler = WebcrawlerConfig(config['Webcrawler'])
            self.filecrawler = FilecrawlerConfig(config['Filecrawler'])
        except KeyError as e:
            raise ConfigError(f"Missing Crawler configuration key: {e}")

class EmbeddingAPIConfig:
    def __init__(self, config: dict):
        try:
            self.text_embedding = config['text_embedding']
            self.image_embedding = config['image_embedding']
        except KeyError as e:
            raise ConfigError(f"Missing Embedding API configuration key: {e}")

class EmbeddingConfig:
    def __init__(self, config: dict):
        try:
            self.url = config['url']
            self.API = EmbeddingAPIConfig(config['API'])
        except KeyError as e:
            raise ConfigError(f"Missing Embedding configuration key: {e}")

class SettingManager:
    def __init__(self, config_file: str):
        """
        Initialize the SettingManager with the given configuration file.
        
        :param config_file: Path to the YAML configuration file.
        """
        self.config = self._load_config(config_file)
        self.elasticsearch = ElasticsearchConfig(self.config.get('Elasticsearch', {}))
        self.crawler = CrawlerConfig(self.config.get('Crawler', {}))
        self.embedding = EmbeddingConfig(self.config.get('Embedding', {}))
    
    def _load_config(self, config_file: str) -> dict:
        """
        Load the YAML configuration file.
        
        :param config_file: Path to the YAML configuration file.
        :return: Dictionary representation of the YAML config.
        """
        try:
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise ConfigError(f"Configuration file '{config_file}' not found.")
        except yaml.YAMLError as exc:
            raise ConfigError(f"Error parsing YAML file: {exc}")

    # Optionally, add methods to reload or update configuration
    def reload_config(self):
        """Reload the configuration from the file."""
        self.config = self._load_config(self.config_file)
        # Re-initialize sub-configs
        self.elasticsearch = ElasticsearchConfig(self.config.get('Elasticsearch', {}))
        self.crawler = CrawlerConfig(self.config.get('Crawler', {}))
        self.embedding = EmbeddingConfig(self.config.get('Embedding', {}))
        
def save_setting(job_data, file_name, output_directory):
    # Make sure the directory exists
    os.makedirs(output_directory, exist_ok=True)

    # Define the YAML file path
    yaml_file = os.path.join(output_directory, file_name + '.yaml')

    # Save the job data to a YAML file in the specified directory
    with open(yaml_file, 'w') as file:
        yaml.dump(job_data, file, default_flow_style=False)

    print(f"Data has been saved to {yaml_file}")        
def delete_setting(job_data, file_name, output_directory):
    # Ensure job_data and file_name are provided
    if not job_data or not file_name:
        return {"error": "Invalid job data or file name."}, 400

    # Construct the full file path based on output_directory and file_name
    file_path = os.path.join(output_directory, f"{file_name}.yaml")  # Assuming the file is a JSON file

    # Check if the file exists
    if os.path.exists(file_path):
        try:
            # Attempt to delete the file
            os.remove(file_path)
            return {"message": f"Settings file '{file_name}' deleted successfully."}, 200
        except Exception as e:
            return {"error": f"Failed to delete file: {str(e)}"}, 500
    else:
        return {"error": f"File '{file_name}' not found."}, 404
    
    
def get_settings(directory):

    yaml_data = []

    # Ensure the directory exists before trying to list its contents
    if not os.path.exists(directory):
        print(f"Directory does not exist: {directory}")
        return yaml_data  # Return an empty list if the directory doesn't exist
    for filename in os.listdir(directory):
        if filename.endswith('.yaml'):
            file_path = os.path.join(directory, filename)
            with open(file_path, 'r') as file:
                try:
                    data = yaml.safe_load(file)
                    yaml_data.append({filename: data})  # Append filename and its content
                except Exception as e:
                    print(f"Error reading {filename}: {e}")
    return yaml_data

def load_yaml(file_path):
    with open(file_path, 'r') as file:
        try:
            data = yaml.safe_load(file)
            return data
        except yaml.YAMLError as e:
            print(f"Error loading YAML file: {e}")
            return None

def force_print(output):
    print(output, flush=True)

        
def get_duration(start, end):
    total_seconds = end - start

    # Convert to hours, minutes, and seconds
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)    

# Print or log the duration
    return f"Execution time: {int(hours)}h {int(minutes)}m {seconds:.2f}s"
    
def get_crawler_setting(name, type):
    if type == 'file':
        return load_yaml(os.path.abspath(os.path.dirname(__file__) + '/../../crawling_setting/file/' + name + '.yaml'))
    if type == 'web':
        return load_yaml(os.path.abspath(os.path.dirname(__file__) + '/../../crawling_setting/web/' + name + '.yaml'))
        
        
def get_elasticsearch_setting():
    return load_yaml(os.path.abspath(os.path.dirname(__file__) + '/../../crawling_setting/other/elasticsearch.yaml'))

def get_thumbnail_setting():
    return load_yaml(os.path.abspath(os.path.dirname(__file__) + '/../../crawling_setting/other/thumbnail.yaml'))

def get_embedding_setting():
    return load_yaml(os.path.abspath(os.path.dirname(__file__) + '/../../crawling_setting/other/embedding.yaml'))




