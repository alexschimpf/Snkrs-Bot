import os
import sys
import six
import pause
import argparse
import logging.config
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

NIKE_HOME_URL = "https://www.nike.com/us/en_us/"
LOGGER = logging.getLogger()


def run(driver, username, password, url, shoe_size, login_time=None, release_time=None,
        page_load_timeout=None, screenshot_path=None, html_path=None, select_payment=False, purchase=False,
        num_retries=None):
    driver.maximize_window()
    driver.set_page_load_timeout(page_load_timeout)

    if login_time:
        LOGGER.info("Waiting until login time: " + login_time)
        pause.until(date_parser.parse(login_time))

    try:
        login(driver=driver, username=username, password=password)
    except Exception as e:
        LOGGER.exception("Failed to login: " + str(e))
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
                select_shoe_size(driver=driver, shoe_size=shoe_size)
            except Exception as e:
                # If we fail to select shoe size, try to buy anyway
                LOGGER.exception("Failed to select shoe size: " + str(e))

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

    driver.quit()


def login(driver, username, password):
    try:
        LOGGER.info("Requesting page: " + NIKE_HOME_URL)
        driver.get(NIKE_HOME_URL)
    except TimeoutException:
        LOGGER.info("Page load timed out but continuing anyway")

    LOGGER.info("Waiting for login button to become clickable")
    wait_until_clickable(driver=driver, xpath="//li[@js-hook='exp-join-login']/button")

    LOGGER.info("Clicking login button")
    driver.find_element_by_xpath("//li[@js-hook='exp-join-login']/button").click()

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
    driver.find_element_by_xpath("//input[@value='LOG IN']").click()
    wait_until_visible(driver=driver, xpath="//span[text()='My Account']")

    LOGGER.info("Successfully logged in")


def select_shoe_size(driver, shoe_size):
    LOGGER.info("Waiting for size dropdown button to become clickable")
    wait_until_clickable(driver, class_name="size-dropdown-button-css", duration=10)

    LOGGER.info("Clicking size dropdown button")
    driver.find_element_by_class_name("size-dropdown-button-css").click()

    LOGGER.info("Waiting for size dropdown to appear")
    wait_until_visible(driver, class_name="expanded", duration=10)

    LOGGER.info("Selecting size from dropdown")
    driver.find_element_by_class_name("expanded").find_element_by_xpath(
        "//button[text()='{}']".format(shoe_size)).click()


def click_buy_button(driver):
    xpath = "//button[@data-qa='feed-buy-cta']"

    LOGGER.info("Waiting for buy button to become clickable")
    wait_until_clickable(driver, xpath=xpath, duration=10)

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
    args = parser.parse_args()

    driver = None
    if args.driver_type == "firefox":
        options = webdriver.FirefoxOptions()
        if args.headless:
            options.add_argument("--headless")
        if sys.platform == "darwin":
            executable_path = "./bin/geckodriver_mac"
        elif "linux" in sys.platform:
            executable_path = "./bin/geckodriver_linux"
        else:
            raise Exception("Unsupported operating system. Please add your own Selenium driver for it.")
        driver = webdriver.Firefox(executable_path=executable_path, firefox_options=options, log_path=os.devnull)
    elif args.driver_type == "chrome":
        options = webdriver.ChromeOptions()
        if args.headless:
            options.add_argument("headless")
        if sys.platform == "darwin":
            executable_path = "./bin/chromedriver_mac"
        elif "linux" in sys.platform:
            executable_path = "./bin/chromedriver_linux"
        else:
            raise Exception("Unsupported operating system. Please add your own Selenium driver for it.")
        driver = webdriver.Chrome(executable_path=executable_path, chrome_options=options)

    run(driver=driver, username=args.username, password=args.password, url=args.url, shoe_size=args.shoe_size,
        login_time=args.login_time, release_time=args.release_time, page_load_timeout=args.page_load_timeout,
        screenshot_path=args.screenshot_path, html_path=args.html_path, select_payment=args.select_payment,
        purchase=args.purchase, num_retries=args.num_retries)
