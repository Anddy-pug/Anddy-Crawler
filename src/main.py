# src/main.py

from setting.setting_manager import SettingManager, ConfigError
from crawler_web.dynamic.dynamic_web_crawler import WebCrawler
# from crawler_web.dynamic.openproject import WebCrawler_openproject
import subprocess
import os
from apscheduler.schedulers.blocking import BlockingScheduler

def main():
    try:
        # Initialize the SettingManager with the path to your config file
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../config.yaml')

        settings = SettingManager(config_path)
        
        # Access Elasticsearch settings
        es_url = settings.elasticsearch.url
        es_username = settings.elasticsearch.username
        es_password = settings.elasticsearch.password
        es_fingerprint = settings.elasticsearch.fingerprint
        es_web_index = settings.elasticsearch.index.web_index
        es_file_index = settings.elasticsearch.index.file_index
        
        
        # Access Crawler settings
        crawler_type = settings.crawler.webcrawler.type
        crawler_login_url = settings.crawler.webcrawler.login_url
        crawler_username = settings.crawler.webcrawler.username
        crawler_password = settings.crawler.webcrawler.password
        username_field_id = settings.crawler.webcrawler.username_field_id
        password_field_id = settings.crawler.webcrawler.password_field_id
        submit_button_id = settings.crawler.webcrawler.submit_button_id
        base_url = settings.crawler.webcrawler.base_url
        not_url = settings.crawler.webcrawler.not_url
        
        print("\nCrawler Type:", crawler_type)
        print("Webcrawler Login URL:", crawler_login_url)
        print("Webcrawler Username:", crawler_username)
        print("Webcrawler Password:", crawler_password)
        print("Username Field ID:", username_field_id)
        print("Password Field ID:", password_field_id)
        print("Submit Button ID:", submit_button_id)
        print("Base URL:", base_url)
        
        #Initialize and start the WebCrawler
        testrail_crawler = WebCrawler(
            elasticsearch_url=es_url,
            elasticsearch_username=es_username,
            elasticsearch_password=es_password,
            elasticsearch_fingerprint=es_fingerprint,
            index_name=es_web_index,
            # index_name="es_web_index",
            login_url=crawler_login_url,
            target_username=crawler_username,
            target_password=crawler_password,
            username_field_id=username_field_id,
            password_field_id=password_field_id,
            submit_button_id=submit_button_id,
            base_url=base_url,
            not_url=not_url
        )


        # openproject_crawler = WebCrawler_openproject(
        #     elasticsearch_url=es_url,
        #     elasticsearch_username=es_username,
        #     elasticsearch_password=es_password,
        #     elasticsearch_fingerprint=es_fingerprint,
        #     index_name="openproject",
        #     login_url="https://192.168.140.254:33005/login",
        #     target_username="pug0620",
        #     target_password="pug0620",
        #     username_field_id="username",
        #     password_field_id="password",
        #     submit_button_id="login",
        #     base_url="https://192.168.140.254:33005/projects",
        #     not_url="logout"
        # )
        



        # crawler.start_crawling()


        scheduler = BlockingScheduler()
        scheduler.add_job(testrail_crawler.start_crawling(), 'interval', hours=5)  # Run every hour
        # scheduler.add_job(openproject_crawler.start_crawling(), 'interval', hours=5)  # Run every hour

        try:
            scheduler.start()  # Start the scheduler
        except (KeyboardInterrupt, SystemExit):
            pass  # Handle exit gracefully

        # subprocess.run(["scrapy", "crawl", "react_spider"], cwd="./crawler_web/static/school/school_spider")
        
    except ConfigError as e:
        print(f"Configuration Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
