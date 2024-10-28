from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(parent_dir)
from embedding.embedding import *
from search_engine.elasticsearch_connector import *
from parser.text_parser import *

# Replace these variables with your own
openproject_url = "https://192.168.140.254:33005/login"  # Replace with your OpenProject URL
username = "pug0620"                                      # Replace with your OpenProject username
password = "pug0620"                                      # Replace with your OpenProject password

# Set up Chrome options to ignore SSL certificate errors
chrome_options = Options()
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--allow-insecure-localhost')  # Optional, allows localhost access

# Set up the WebDriver using WebDriver Manager
# service = Service(ChromeDriverManager().install())
service = Service(executable_path=r'G:\driver\129.0.6668.89\chromedriver-win32\chromedriver.exe')
driver = webdriver.Chrome(service=service, options=chrome_options)

# Initialize WebDriverWait with a timeout of 10 seconds
wait = WebDriverWait(driver, 10)

try:
    # Navigate to the OpenProject login page
    driver.get(openproject_url)
    
    # sign_in_link = driver.find_element(By.CLASS_NAME, "op-app-menu--item-dropdown-indicator")
    # sign_in_link.click()
    
    # sign_in_link = driver.find_element(By.XPATH, "//a[@title='Sign in' and @href='/login']")
    # sign_in_link.click()
    
    # sign_in_link = driver.find_element(By.LINK_TEXT, "Sign in")
    # sign_in_link.click()

    
    # sign_in_link = driver.find_element(By.CSS_SELECTOR, "a.op-app-menu--item-action[title='Sign in']")
    # sign_in_link.click()

    sign_in_link = driver.find_element(By.PARTIAL_LINK_TEXT, "Sign in")
    sign_in_link.click()


    
    

    
    # Wait until the username input field is visible and interactable
    username_input = wait.until(EC.element_to_be_clickable((By.ID, "username-pulldown")))
    username_input.clear()  # Clear any pre-filled text
    username_input.send_keys(username)

    # Wait until the password input field is visible and interactable
    password_input = wait.until(EC.element_to_be_clickable((By.ID, "password-pulldown")))
    password_input.clear()
    password_input.send_keys(password)

    sign_in_button = driver.find_element(By.ID, "login-pulldown")
    sign_in_button.click()
    driver.get("https://192.168.140.254:33005/work_packages?query_props=%7B%22c%22%3A%5B%22id%22%2C%22type%22%2C%22subject%22%2C%22status%22%2C%22startDate%22%2C%22dueDate%22%2C%22duration%22%5D%2C%22hi%22%3Afalse%2C%22g%22%3A%22%22%2C%22t%22%3A%22createdAt%3Adesc%22%2C%22f%22%3A%5B%7B%22n%22%3A%22dueDate%22%2C%22o%22%3A%22%3Ct-%22%2C%22v%22%3A%5B%221%22%5D%7D%2C%7B%22n%22%3A%22status%22%2C%22o%22%3A%22o%22%2C%22v%22%3A%5B%5D%7D%5D%7D")
    time.sleep(1)
    WebDriverWait(driver, 10).until(
        lambda x: x.execute_script("return document.readyState === 'complete'")
    )
    page_source = driver.page_source
    soup = BeautifulSoup(driver.find_element('tag name', 'body').get_attribute('innerText'), "html.parser")
    content = soup.get_text()
    content = content.replace('\n', ' ').replace('\t', ' ')
    content = clean_text(content)
    # Use BeautifulSoup to filter and clean the content



    # Replace newlines and tabs with spaces for better formatting
    filtered_content = content.replace('\n', ' ').replace('\t', ' ').strip()
    print("!!!" + filtered_content)
    # Save the filtered content to a text file
    # with open('filtered_work_packages_page.txt', 'w', encoding='utf-8') as file:
    #     file.write(filtered_content)
    # Wait until the login button is clickable
    # sign_in_button = driver.find_element(By.XPATH, "//input[@type='submit' and @name='login' and @value='Sign in']")
    # sign_in_button.click()

    # Optionally, wait until a specific element on the dashboard is present to confirm successful login
    # Example:
    # dashboard_element = wait.until(EC.presence_of_element_located((By.ID, "dashboard")))
    # print("Logged in successfully!")

    # For demonstration, we'll just print a success message after clicking login
    print("Login button clicked successfully!")

finally:
    # Optionally, wait for a few seconds to observe the result before closing
    # time.sleep(5)  # Adjust as necessary
    # Close the driver after the task
    driver.quit()
