from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("user-data-dir=/path/to/your/chrome/profile")  # Specify the path to your profile

# Create a new instance of the Chrome driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Open a website
driver.get("https://upwork.com")

# Perform your crawling operations
print(driver.title)  # Print the title of the page

# Close the browser
driver.quit()