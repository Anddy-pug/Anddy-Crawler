from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# Replace these variables with your own
openproject_url = "https://192.168.140.254:33001/login"  # Replace with your OpenProject URL
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
    driver.get("https://192.168.140.254:33001/login")
    
    # sign_in_link = driver.find_element(By.CLASS_NAME, "op-app-menu--item-dropdown-indicator")
    # sign_in_link.click()
    
    # sign_in_link = driver.find_element(By.XPATH, "//a[@title='Sign in' and @href='/login']")
    # sign_in_link.click()
    
    # sign_in_link = driver.find_element(By.LINK_TEXT, "Sign in")
    # sign_in_link.click()

    
    # sign_in_link = driver.find_element(By.CSS_SELECTOR, "a.op-app-menu--item-action[title='Sign in']")
    # sign_in_link.click()

    # sign_in_link = driver.find_element(By.PARTIAL_LINK_TEXT, "Sign in")
    # sign_in_link.click()

    # Wait until the username input field is visible and interactable
    username_input = wait.until(EC.element_to_be_clickable((By.ID, "user")))
    username_input.clear()  # Clear any pre-filled text
    username_input.send_keys(username)

    # Wait until the password input field is visible and interactable
    password_input = wait.until(EC.element_to_be_clickable((By.ID, "password")))
    password_input.clear()
    password_input.send_keys(password)

    login_button = driver.find_element(By.CSS_SELECTOR, "button.button-vue.button-vue--icon-and-text.button-vue--vue-primary.button-vue--wide")
    login_button.click()

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
    time.sleep(5)  # Adjust as necessary
    # Close the driver after the task
    driver.quit()
