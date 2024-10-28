from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time


# Set up Chrome options to ignore SSL certificate errors (if needed)
chrome_options = Options()
chrome_options.add_argument('--ignore-certificate-errors')

# Set up the WebDriver
service = Service(executable_path=r'G:\driver\129.0.6668.89\chromedriver-win32\chromedriver.exe')
driver = webdriver.Chrome(service=service, options=chrome_options)
wait = WebDriverWait(driver, 10)



driver.get("https://192.168.140.254:33001/login")
username_input = wait.until(EC.element_to_be_clickable((By.ID, "user")))
username_input.clear()  # Clear any pre-filled text
username_input.send_keys("pug0620")

# Wait until the password input field is visible and interactable
password_input = wait.until(EC.element_to_be_clickable((By.ID, "password")))
password_input.clear()
password_input.send_keys("pug0620")

login_button = driver.find_element(By.CSS_SELECTOR, "button.button-vue.button-vue--icon-and-text.button-vue--vue-primary.button-vue--wide")
login_button.click()
time.sleep(3)  # Adjust if necessary

try:
    # Replace this URL with the page where the elements are located
    driver.get('https://192.168.140.254:33001/apps/files/files/5286?dir=/Templates')  # Change to the actual page URL

    # Wait for the page to fully load
    time.sleep(3)  # Adjust if necessary

    # Get the page source after the page is fully loaded
    page_source = driver.page_source

    # Create a BeautifulSoup object
    soup = BeautifulSoup(page_source, 'html.parser')

    # Find all elements with the class 'files-list__row-name-text'
    file_elements = soup.find_all('td', class_='files-list__row-name')

    # Loop through each element and extract the image URL and file name
    for file_element in file_elements:
        # Extract the image URL from the <img> tag
        img_tag = file_element.find('img')
        if img_tag and img_tag.has_attr('src'):
            image_url = img_tag['src']
        else:
            image_url = None  # In case no image exists

        # Extract the file name and extension (with error handling)
        name_tag = file_element.find('span', class_='files-list__row-name-')
        extension_tag = file_element.find('span', class_='files-list__row-name-ext')

        # Check if the tags exist before accessing their text
        if name_tag and extension_tag:
            name = name_tag.get_text()
            extension = extension_tag.get_text()
            file_name = f"{name}{extension}"
        else:
            file_name = "Unknown file name"

        # Print the result
        print(f"File Name: {file_name}, Image URL: {image_url}")

finally:
    # Close the browser after the task
    driver.quit()
