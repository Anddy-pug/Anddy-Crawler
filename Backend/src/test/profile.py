from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Configure Selenium to reuse the profile where you're logged in
chrome_options = Options()
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--allow-insecure-localhost")

# Set your user data directory to the same profile you use for manual login
profile_path = "C:/Users/KKK/AppData/Local/Google/Chrome/User Data"
chrome_options.add_argument(f"user-data-dir={profile_path}")
chrome_options.add_argument("profile-directory=Profile 18")

# Initialize the Selenium WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Now, try visiting the website
driver.get("https://www.upwork.com")

# Selenium should open Chrome with your active session
