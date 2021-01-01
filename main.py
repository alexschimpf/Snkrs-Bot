import os
import sys
import six
import pause
import argparse
import logging.config
import re
import time
import random
from selenium import webdriver
from dateutil import parser as date_parser
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC


logging.config.dictConfig({
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s [PID %(process)d] [Thread %(thread)d] [%(levelname)s] [%(name)s] %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "default",
            "stream": "ext://sys.stdout"
        }
    },
    "root": {
        "level": "INFO",
        "handlers": [
            "console"
        ]
    }
})

NIKE_HOME_URL = "https://www.nike.com/login"
LOGGER = logging.getLogger()



def run(driver, shoe_type, username, password, url, shoe_size, login_time=None, release_time=None,
        page_load_timeout=None, screenshot_path=None, html_path=None, select_payment=False, purchase=False,
        num_retries=None, dont_quit=False):
    driver.maximize_window()
    driver.set_page_load_timeout(page_load_timeout)

    if login_time:
        LOGGER.info("Waiting until login time: " + login_time)
        pause.until(date_parser.parse(login_time))

    skip_retry_login = True
    try:
        login(driver=driver, username=username, password=password)
    except TimeoutException:
        LOGGER.info("Failed to login due to timeout. Retrying...")
        skip_retry_login = False
    except Exception as e:
        LOGGER.exception("Failed to login: " + str(e))
        six.reraise(Exception, e, sys.exc_info()[2])

    if skip_retry_login is False:   
        try:
            retry_login(driver=driver, username=username, password=password)
        except Exception as e:
            LOGGER.exception("Failed to retry login: " + str(e))
            six.reraise(Exception, e, sys.exc_info()[2])
            
    if release_time:
        LOGGER.info("Waiting until release time: " + release_time)
        pause.until(date_parser.parse(release_time))

    num_retries_attempted = 0
    while True:
        try:
            try:
                LOGGER.info("Requesting page: " + url)
                driver.get(url)
            except TimeoutException:
                LOGGER.info("Page load timed out but continuing anyway")
            
            try:
                select_shoe_size(driver=driver, shoe_size=shoe_size, shoe_type=shoe_type)
            except Exception as e:
                # Try refreshing page since you can't click Buy button without selecting size
                LOGGER.exception("Failed to select shoe size: " + str(e))
                continue

            try:
                click_buy_button(driver=driver)
            except Exception as e:
                LOGGER.exception("Failed to click buy button: " + str(e))
                six.reraise(Exception, e, sys.exc_info()[2])

            if select_payment:
                try:
                    select_payment_option(driver=driver)
                except Exception as e:
                    LOGGER.exception("Failed to select payment option: " + str(e))
                    six.reraise(Exception, e, sys.exc_info()[2])

                try:
                    click_save_button(driver=driver)
                except Exception as e:
                    LOGGER.exception("Failed to click save button: " + str(e))
                    six.reraise(Exception, e, sys.exc_info()[2])

            if purchase:
                try:
                    click_submit_button(driver=driver)
                except Exception as e:
                    LOGGER.exception("Failed to click submit button: " + str(e))
                    six.reraise(Exception, e, sys.exc_info()[2])

            LOGGER.info("Purchased shoe")
            break
        except Exception:
            if num_retries and num_retries_attempted < num_retries:
                num_retries_attempted += 1
                continue
            else:
                break

    if screenshot_path:
        LOGGER.info("Saving screenshot")
        driver.save_screenshot(screenshot_path)

    if html_path:
        LOGGER.info("Saving HTML source")
        with open(html_path, "w") as f:
            f.write(driver.page_source)

    if dont_quit:
        LOGGER.info("Preventing driver quit...")
        input("Press Enter to quit...")
    
    driver.quit()


def login(driver, username, password):
    try:
        LOGGER.info("Requesting page: " + NIKE_HOME_URL)
        driver.get(NIKE_HOME_URL)
    except TimeoutException:
        LOGGER.info("Page load timed out but continuing anyway")

    LOGGER.info("Waiting for login fields to become visible")
    wait_until_visible(driver=driver, xpath="//input[@name='emailAddress']")

    LOGGER.info("Entering username and password")
    email_input = driver.find_element_by_xpath("//input[@name='emailAddress']")
    email_input.clear()
    email_input.send_keys(username)
    
    password_input = driver.find_element_by_xpath("//input[@name='password']")
    password_input.clear()
    password_input.send_keys(password)

    LOGGER.info("Logging in")
    driver.find_element_by_xpath("//input[@value='SIGN IN']").click()
    
    wait_until_visible(driver=driver, xpath="//a[@data-path='myAccount:greeting']", duration=5)
    
    LOGGER.info("Successfully logged in")

def retry_login(driver, username, password):
    num_retries_attempted = 0
    num_retries = 5
    while True:
        try:            
            # Xpath to error dialog button
            xpath = "/html/body/div[2]/div[3]/div[3]/div/div[2]/input"
            wait_until_visible(driver=driver, xpath=xpath, duration=5)
            driver.find_element_by_xpath(xpath).click()
        
            password_input = driver.find_element_by_xpath("//input[@name='password']")
            password_input.clear()
            password_input.send_keys(password)

            LOGGER.info("Logging in")
            
            try:
                driver.find_element_by_xpath("//input[@value='SIGN IN']").click()
            except Exception as e:
                if num_retries_attempted < num_retries:
                    num_retries_attempted += 1
                    continue
                else:
                    LOGGER.info("Too many login attempts. Please restart app.")
                    break
                                
            if num_retries_attempted < num_retries:
                num_retries_attempted += 1
                continue
            else:
                LOGGER.info("Too many login attempts. Please restart app.")
                break
        except Exception as e:
            LOGGER.exception("Error dialog did not load, proceed. Error: " + str(e))
            break

    wait_until_visible(driver=driver, xpath="//a[@data-path='myAccount:greeting']")
    
    LOGGER.info("Successfully logged in")
    
def select_shoe_size(driver, shoe_size, shoe_type):
    LOGGER.info("Waiting for size dropdown to appear")
    wait_until_visible(driver, class_name="size-grid-button", duration=10)

    LOGGER.info("Selecting size from dropdown")

    # Get first element found text
    size_text = driver.find_element_by_xpath("//li[@data-qa='size-available']/button").text
            
    # Determine if size only displaying or size type + size
    if re.search("[a-zA-Z]", size_text):      
        if shoe_type in ("Y", "C"):
            shoe_size_type = shoe_size + shoe_type
        else:
            shoe_size_type = shoe_type + " " + shoe_size
     
        driver.find_element_by_xpath("//li[@data-qa='size-available']").find_element_by_xpath(
            "//button[text()[contains(.,'"+shoe_size_type+"')]]").click()
    
    else:
        driver.find_element_by_xpath("//li[@data-qa='size-available']").find_element_by_xpath(
            "//button[text()='{}']".format(shoe_size)).click()


def click_buy_button(driver):
    xpath = "//button[@data-qa='feed-buy-cta']"
    class_name = "photo-component"

    LOGGER.info("Waiting for buy button to become clickable")
    wait_until_clickable(driver, xpath=xpath, duration=10)
    
    element = driver.find_element_by_class_name(class_name)
    driver.execute_script("arguments[0].scrollIntoView(true);" + "window.scrollBy(0,-100);", element)

    LOGGER.info("Clicking buy button")
    driver.find_element_by_xpath(xpath).click()


def select_payment_option(driver):
    xpath = "//input[@data-qa='payment-radio']"

    LOGGER.info("Waiting for payment checkbox to become clickable")
    wait_until_clickable(driver, xpath=xpath, duration=10)

    LOGGER.info("Checking payment checkbox")
    driver.find_element_by_xpath(xpath).click()


def click_save_button(driver):
    xpath = "//button[text()='Save &amp; Continue']"

    LOGGER.info("Waiting for save button to become clickable")
    wait_until_clickable(driver, xpath=xpath, duration=10)

    LOGGER.info("Clicking save button")
    driver.find_element_by_xpath(xpath).click()


def click_submit_button(driver):
    xpath = "//button[text()='Submit Order']"

    LOGGER.info("Waiting for submit button to become clickable")
    wait_until_clickable(driver, xpath=xpath, duration=10)

    LOGGER.info("Clicking submit button")
    driver.find_element_by_xpath(xpath).click()


def wait_until_clickable(driver, xpath=None, class_name=None, duration=10000, frequency=0.01):
    if xpath:
        WebDriverWait(driver, duration, frequency).until(EC.element_to_be_clickable((By.XPATH, xpath)))
    elif class_name:
        WebDriverWait(driver, duration, frequency).until(EC.element_to_be_clickable((By.CLASS_NAME, class_name)))


def wait_until_visible(driver, xpath=None, class_name=None, duration=10000, frequency=0.01):
    if xpath:
        WebDriverWait(driver, duration, frequency).until(EC.visibility_of_element_located((By.XPATH, xpath)))
    elif class_name:
        WebDriverWait(driver, duration, frequency).until(EC.visibility_of_element_located((By.CLASS_NAME, class_name)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--url", required=True)
    parser.add_argument("--shoe-size", required=True)
    parser.add_argument("--login-time", default=None)
    parser.add_argument("--release-time", default=None)
    parser.add_argument("--screenshot-path", default=None)
    parser.add_argument("--html-path", default=None)
    parser.add_argument("--page-load-timeout", type=int, default=2)
    parser.add_argument("--driver-type", default="firefox", choices=("firefox", "chrome"))
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--select-payment", action="store_true")
    parser.add_argument("--purchase", action="store_true")
    parser.add_argument("--num-retries", type=int, default=1)
    parser.add_argument("--dont-quit", action="store_true")
    parser.add_argument("--shoe-type", default="M", choices=("M", "F", "W", "Y", "C"))
    parser.add_argument("--webdriver-path", required=False, default=None)
    args = parser.parse_args()

    driver = None

    if args.driver_type == "firefox":
        options = webdriver.FirefoxOptions()
        if args.headless:
            options.add_argument("--headless")
        if args.webdriver_path != None:
            executable_path = args.webdriver_path
        elif sys.platform == "darwin":
            executable_path = "./bin/geckodriver_mac"
        elif "linux" in sys.platform:
            executable_path = "./bin/geckodriver_linux"
        elif "win32" in sys.platform:
            executable_path = "./bin/geckodriver_win32.exe"
        else:
            raise Exception("Drivers for installed operating system not found. Try specifying the path to the drivers with the --webdriver-path option")
        driver = webdriver.Firefox(executable_path=executable_path, firefox_options=options, log_path=os.devnull)
    elif args.driver_type == "chrome":
        options = webdriver.ChromeOptions()
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        if args.headless:
            options.add_argument("headless")
        if args.webdriver_path != None:
            executable_path = args.webdriver_path
        elif sys.platform == "darwin":
            executable_path = "./bin/chromedriver_mac"
        elif "linux" in sys.platform:
            executable_path = "./bin/chromedriver_linux"
        elif "win32" in sys.platform:
            executable_path = "./bin/chromedriver_win32.exe"
        else:
            raise Exception("Drivers for installed operating system not found. Try specifying the path to the drivers with the --webdriver-path option")
        driver = webdriver.Chrome(executable_path=executable_path, chrome_options=options)
    else:
        raise Exception("Specified web browser not supported, only Firefox and Chrome are supported at this point")

    shoe_type = args.shoe_type
        
    run(driver=driver, shoe_type=shoe_type, username=args.username, password=args.password, url=args.url, shoe_size=args.shoe_size,
        login_time=args.login_time, release_time=args.release_time, page_load_timeout=args.page_load_timeout,
        screenshot_path=args.screenshot_path, html_path=args.html_path, select_payment=args.select_payment,
        purchase=args.purchase, num_retries=args.num_retries, dont_quit=args.dont_quit)
