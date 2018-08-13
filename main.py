import pause
import datetime
from dateutil import parser
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

USERNAME = None
PASSWORD = None
if not USERNAME or not PASSWORD:
    raise Exception("Please provide a username and password")

# e.g. "https://www.nike.com/launch/t/air-jordan-12-retro-olive-canvas-metallic-gold/"
SHOE_URL = None
if not SHOE_URL:
    raise Exception("Please provide a shoe URL")

# e.g. "2018-08-14 7:00:00"
RELEASE_TIME = None
if not RELEASE_TIME:
    raise Exception("Please provide a release time")

# e.g. "10"
SHOE_SIZE = None
if not SHOE_SIZE:
    raise Exception("Please provide a shoe size")

# e.g. "/Users/alexschimpf/Desktop/snkrs_results.png"
SCREENSHOT_PATH = None
if not SCREENSHOT_PATH:
    raise Exception("Please provide a screenshot path")

url = "https://www.nike.com/us/en_us/"

# driver = webdriver.Chrome(executable_path="./bin/chromedriver_mac")
driver = webdriver.Firefox(executable_path="./bin/geckodriver_mac")
driver.maximize_window()
driver.set_page_load_timeout(2)

try:
    driver.get(url)
except TimeoutException:
    pass

print("Clicking login button")
WebDriverWait(driver, 100000, 0.1).until(
    EC.visibility_of_element_located((By.XPATH, "//li[@js-hook='exp-join-login']/button")))
driver.find_element_by_xpath("//li[@js-hook='exp-join-login']/button").click()

print("Entering username and password")
WebDriverWait(driver, 100000, 0.1).until(
    EC.visibility_of_element_located((By.XPATH, "//input[@name='emailAddress']")))
email_input = driver.find_element_by_xpath("//input[@name='emailAddress']")
email_input.clear()
email_input.send_keys(USERNAME)
password_input = driver.find_element_by_xpath("//input[@name='password']")
password_input.clear()
password_input.send_keys(PASSWORD)

print("Logging in")
driver.find_element_by_xpath("//input[@value='LOG IN']").click()
WebDriverWait(driver, 100000, 0.01).until(
    EC.visibility_of_element_located((By.XPATH, "//span[text()='My Account']")))

print("Waiting until release time")
release_time = parser.parse(RELEASE_TIME)
pause.until(release_time)

while True:
    print("Refreshing launch page")
    try:
        driver.get(SHOE_URL)
    except TimeoutException:
        pass

    try:
        WebDriverWait(driver, 0.5, 0.01).until(
            EC.visibility_of_element_located((By.XPATH, "//button[text()='ADD TO CART']")))
    except Exception:
        continue
    else:
        print("Shoe is available")
        pass

    try:
        print("Selecting shoe size")
        WebDriverWait(driver, 100000, 0.01).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "size-dropdown-button-css")))
        driver.find_element_by_class_name("size-dropdown-button-css").click()
        WebDriverWait(driver, 100000, 0.01).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "expanded")))
        driver.find_element_by_class_name("expanded").find_element_by_xpath(
            "//button[text()='{}']".format(SHOE_SIZE)).click()

        print("Adding shoe to cart")
        WebDriverWait(driver, 100000, 0.01).until(
            EC.visibility_of_element_located((By.XPATH, "//button[text()='ADD TO CART']")))
        driver.find_element_by_xpath("//button[text()='ADD TO CART']").click()

        print("Checking out")
        WebDriverWait(driver, 100000, 0.01).until(
            EC.visibility_of_element_located((By.XPATH, "//a[text()='Checkout']")))
        driver.find_element_by_xpath("//a[text()='Checkout']").click()

        print("Purchasing shoe")
        WebDriverWait(driver, 100000, 0.01).until(
            EC.visibility_of_element_located((By.XPATH, "//button[text()='Place Order']")))

        # --------------------------------------------------------------------------------------
        # CAUTION: Uncommenting the line below will make this script purchase the shoe!!!
        # --------------------------------------------------------------------------------------
        #
        # driver.find_element_by_xpath("//button[text()='Place Order']").click()
        #
    except Exception:
        continue
    else:
        break

print("Shoe purchased at: {}".format(str(datetime.datetime.now())))
print("Getting screenshot")
driver.save_screenshot(SCREENSHOT_PATH)
