from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run headless Chrome to avoid opening a window
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

# Path to your ChromeDriver
service = Service('/path/to/chromedriver')

# Initialize the WebDriver
driver = webdriver.Chrome(service=service, options=chrome_options)

# Function to get website content
def get_website_content(url):
    try:
        # Open the webpage
        driver.get(url)

        # Wait for the page to load completely
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )

        # Get page source
        page_source = driver.page_source

        # Assert presence of CSS files
        css_files = driver.find_elements(By.XPATH, "//link[@rel='stylesheet']")
        assert len(css_files) > 0, "No CSS files found!"

        # Assert presence of JS files
        js_files = driver.find_elements(By.XPATH, "//script[@src]")
        assert len(js_files) > 0, "No JS files found!"

        # Assert presence of other resources (e.g., images)
        img_files = driver.find_elements(By.TAG_NAME, 'img')
        assert len(img_files) > 0, "No image resources found!"

        # Print out the resources found
        print("CSS Files:")
        for css in css_files:
            print(css.get_attribute('href'))

        print("\nJS Files:")
        for js in js_files:
            print(js.get_attribute('src'))

        print("\nImage Resources:")
        for img in img_files:
            print(img.get_attribute('src'))

    except AssertionError as e:
        print(f"Assertion Error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the browser
        driver.quit()

# Example usage
get_website_content('https://example.com')
