import os
import sys
import six
import pause
import requests
import argparse
import logging.config
from selenium import webdriver
from dateutil import parser as date_parser
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC

"""

This is an experimental script which attempts at utilizing some Nike APIs.

Current implementation:
    1. Login with Selenium
    2. Using the driver's stored cookies, make a Nike API request to add the desired item to your cart
    3. Load the checkout page and place an order
    
Not sure if this will be any faster than the other script...

"""


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
NIKE_CHECKOUT_URL = "https://www.nike.com/checkout"
NIKE_CART_API_URL = "https://secure-store.nike.com/us/services/jcartService"
LOGGER = logging.getLogger()


def run(driver, username, password, product_id, sku_id, shoe_size, login_time=None, release_time=None,
        page_load_timeout=None, screenshot_path=None, purchase=False, num_retries=None):
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
                LOGGER.info("Adding item to cart")
                add_item_to_cart(driver=driver, product_id=product_id, sku_id=sku_id, size=shoe_size)
            except Exception as e:
                LOGGER.exception("Failed to add item to cart " + str(e))
                six.reraise(Exception, e, sys.exc_info()[2])

            try:
                LOGGER.info("Requesting page: " + NIKE_CHECKOUT_URL)
                driver.get(NIKE_CHECKOUT_URL)
            except TimeoutException:
                LOGGER.info("Page load timed out but continuing anyway")

            if purchase:
                try:
                    click_place_order_button(driver=driver)
                except Exception as e:
                    LOGGER.exception("Failed to click place order button: " + str(e))
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


def click_place_order_button(driver):
    xpath = "//button[text()='Place Order']"

    LOGGER.info("Waiting for place order button to become clickable")
    wait_until_clickable(driver, xpath=xpath, duration=10)

    LOGGER.info("Clicking place order button")
    driver.find_element_by_xpath(xpath).click()


def add_item_to_cart(driver, product_id, sku_id, size):
    cookies = driver.get_cookies()
    params = {
        "action": "addItem",
        "lang_locale": "en_US",
        "catalogId": "1",
        "productId": product_id,
        "qty": "1",
        "price": "",
        "skuAndSize": "{}:{}".format(sku_id, size),
        "rt": "json",
        "view": "3",
        "skuId": sku_id,
        "displaySize": "10"
    }
    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
        "origin": "https://www.nike.com",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "accept": "*/*",
        "scheme": "https"
    }
    response = requests.get(url=NIKE_CART_API_URL,
                            params=params, headers=headers, cookies=cookies)
    if response.status_code != 200:
        raise Exception("Request to add item to cart failed (code {}): {}".format(
            response.status_code, response.text))


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
    parser.add_argument("--product-id", required=True)
    parser.add_argument("--sku-id", required=True)
    parser.add_argument("--shoe-size", required=True)
    parser.add_argument("--login-time", default=None)
    parser.add_argument("--release-time", default=None)
    parser.add_argument("--screenshot-path", default=None)
    parser.add_argument("--page-load-timeout", type=int, default=2)
    parser.add_argument("--driver-type", default="firefox", choices=("firefox", "chrome"))
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--purchase", action="store_true")
    parser.add_argument("--num-retries", type=int, default=1)
    args = parser.parse_args()

    driver = None
    if args.driver_type == "firefox":
        options = webdriver.FirefoxOptions()
        if args.headless:
            options.add_argument("--headless")
        executable_path = None
        if sys.platform == "darwin":
            executable_path = "./bin/geckodriver_mac"
        elif "linux" in sys.platform:
            executable_path = "./bin/geckodriver_linux"
        driver = webdriver.Firefox(executable_path=executable_path, firefox_options=options, log_path=os.devnull)
    elif args.driver_type == "chrome":
        options = webdriver.ChromeOptions()
        if args.headless:
            options.add_argument("headless")
        executable_path = None
        if sys.platform == "darwin":
            executable_path = "./bin/chromedriver_mac"
        elif "linux" in sys.platform:
            executable_path = "./bin/chromedriver_linux"
        driver = webdriver.Chrome(executable_path=executable_path, chrome_options=options)

    run(driver=driver, username=args.username, password=args.password, product_id=args.product_id,
        sku_id=args.sku_id, shoe_size=args.shoe_size, login_time=args.login_time, release_time=args.release_time,
        page_load_timeout=args.page_load_timeout, screenshot_path=args.screenshot_path,
        purchase=args.purchase, num_retries=args.num_retries)
