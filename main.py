import os
import sys
import six
import pause
import argparse
import logging.config
import re
import time
import random
import json
from selenium import webdriver
from dateutil import parser as date_parser
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
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
SUBMIT_BUTTON_XPATH = "/html/body/div[2]/div/div/div[2]/div/div/div/div/div[2]/div/div/div[3]/div/div/div[6]/button"
LOGGER = logging.getLogger()

def run(driver, shoe_type, username, password, url, shoe_size, shipping_option, login_time=None, release_time=None,
        shipping_address=None, page_load_timeout=None, screenshot_path=None, html_path=None, select_payment=False, purchase=False,
        num_retries=None, dont_quit=False, cvv=None):
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

    skip_add_address = False
    skip_select_shipping = False
    skip_payment = False
    num_retries_attempted = 0
    while True:
        try:
            try:
                LOGGER.info("Requesting page: " + url)
                driver.get(url)
            except TimeoutException:
                LOGGER.info("Page load timed out but continuing anyway")
            
            try:
                skip_size_selection = False
                substring = "size="
                if substring in url:
                    skip_size_selection = True
                select_shoe_size(driver=driver, shoe_size=shoe_size, shoe_type=shoe_type, skip_size_selection=skip_size_selection)
            except Exception as e:
                # Try refreshing page since you can't click Buy button without selecting size (except if size parameter passed in)
                LOGGER.exception("Failed to select shoe size: " + str(e))
                continue
                
            try:
                click_buy_button(driver=driver)
            except Exception as e:
                LOGGER.exception("Failed to click buy button: " + str(e))                                
                six.reraise(Exception, e, sys.exc_info()[2])
                
            skip_add_address, skip_select_shipping, skip_payment = poll_checkout_phase_one(driver=driver)
                    
            if skip_add_address is False and shipping_address:
                try:
                    click_add_new_address_button(driver=driver)
                except Exception as e:
                    LOGGER.exception("Failed to click Add New Address button: " + str(e))
                    six.reraise(Exception, e, sys.exc_info()[2])
                              
                try:                    
                    input_address(driver=driver, shipping_address=shipping_address)
                except Exception as e:
                    LOGGER.exception("Failed to select address: " + str(e))
                    six.reraise(Exception, e, sys.exc_info()[2])
            
                try:
                    click_save_button(driver=driver)
                except Exception as e:
                    LOGGER.exception("Failed to click save button: " + str(e))
                    six.reraise(Exception, e, sys.exc_info()[2])
            
            if skip_select_shipping is False:
                try:
                    select_shipping_option(driver=driver, shipping_option=shipping_option)                    
                except Exception as e:
                    LOGGER.exception("Failed to select shipping option: " + str(e))
                    six.reraise(Exception, e, sys.exc_info()[2])

                try:
                    click_save_button(driver=driver)
                except StaleElementReferenceException:
                    LOGGER.info("Failed to click save button (StaleElementReferenceException). Retrying once...")
                    try:
                        click_save_button(driver=driver, check_disabled=False)
                    except Exception as e:
                        LOGGER.exception("Failed to click save button: " + str(e))
                        six.reraise(Exception, e, sys.exc_info()[2])
                except Exception as e:
                    LOGGER.exception("Failed to click save button: " + str(e))
                    six.reraise(Exception, e, sys.exc_info()[2])
                
                skip_payment = poll_checkout_phase_two(driver=driver)
                                                 
            if skip_payment is False:
                if select_payment:
                    try:
                        select_payment_option(driver=driver)
                    except Exception as e:
                        LOGGER.exception("Failed to select payment option: " + str(e))
                        six.reraise(Exception, e, sys.exc_info()[2])
                           
                if cvv:
                    try:
                        input_cvv(driver=driver, cvv=cvv)
                    except Exception as e:
                        LOGGER.exception("Failed to input cvv: " + str(e))
                        six.reraise(Exception, e, sys.exc_info()[2])
                
                try:
                    # Use explicit xpath since iframe from cvv causes issues with normal xpath
                    xpath = "/html/body/div[2]/div/div/div[2]/div/div/div/div/div[2]/div/div/div[2]/div/span/span[1]/div/button"
                    click_save_button(driver=driver, xpath_o=xpath)                    
                except Exception as e:
                    LOGGER.exception("Failed to click save button: " + str(e))
                    six.reraise(Exception, e, sys.exc_info()[2])

            if purchase:
                try:
                    # Use explicit xpath since iframe from cvv causes issues with normal xpath                    
                    xpath = SUBMIT_BUTTON_XPATH
                    click_submit_button(driver=driver, xpath_o=xpath)
                except Exception as e:
                    LOGGER.exception("Failed to click submit button: " + str(e))
                    six.reraise(Exception, e, sys.exc_info()[2])

            LOGGER.info("Purchased shoe")
            break
        except Exception:
            if num_retries and num_retries_attempted < num_retries:
                num_retries_attempted += 1
                skip_add_address = False
                skip_select_shipping = False
                skip_payment = False
                continue
            else:
                LOGGER.info("Purchase failed")
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
    
def select_shoe_size(driver, shoe_size, shoe_type, skip_size_selection):
    LOGGER.info("Waiting for size dropdown to appear")

    wait_until_visible(driver, class_name="size-grid-button", duration=10)

    if skip_size_selection:
        LOGGER.info("Skipping size selection...")
    else:
        LOGGER.info("Selecting size from dropdown")
    
        # Get first element found text
        size_text = driver.find_element_by_xpath("//li[@data-qa='size-available']/button").text
        
    
        special_shoe_type = False
        # Determine if size only displaying or size type + size
        if re.search("[a-zA-Z]", size_text):
    
            if shoe_type in ("Y", "C"):
                shoe_size_type = shoe_size + shoe_type
            elif shoe_size is None and shoe_type in ("XXS", "XS", "S", "M", "L", "XL"):
                shoe_size_type = shoe_type
                special_shoe_type = True  
            else:
                shoe_size_type = shoe_type + " " + shoe_size
     
            LOGGER.info("Shoe size/type=" + shoe_size_type)
            
            if special_shoe_type:
                driver.find_element_by_xpath("//li[@data-qa='size-available']").find_element_by_xpath(
                    "//button[text()='{}']".format(shoe_size_type)).click()
            else:
                driver.find_element_by_xpath("//li[@data-qa='size-available']").find_element_by_xpath(
                    "//button[text()[contains(.,'"+shoe_size_type+"')]]").click()
                
        else:
        
            driver.find_element_by_xpath("//li[@data-qa='size-available']").find_element_by_xpath(
                "//button[text()='{}']".format(shoe_size)).click()


def click_buy_button(driver):
    xpath = "//button[@data-qa='feed-buy-cta']"
    
    LOGGER.info("Waiting for buy button to become present")
    element = wait_until_present(driver, xpath=xpath, duration=10) 
    
    LOGGER.info("Clicking buy button")
    driver.execute_script("arguments[0].click();", element)


def select_payment_option(driver):
    xpath = "//input[@data-qa='payment-radio']"

    LOGGER.info("Waiting for payment checkbox to become clickable")
    wait_until_clickable(driver, xpath=xpath, duration=10)

    LOGGER.info("Checking payment checkbox")
    driver.find_element_by_xpath(xpath).click()
    
def input_address(driver, shipping_address):
    LOGGER.info("Inputting address")
    LOGGER.info("First Name=" + shipping_address["first_name"])
    LOGGER.info("Last Name=" + shipping_address["last_name"])
    LOGGER.info("Address=" + shipping_address["address"])
    LOGGER.info("Apt=" + shipping_address["apt"])
    LOGGER.info("City=" + shipping_address["city"])
    LOGGER.info("State=" + shipping_address["state"])
    LOGGER.info("Zip Code=" + shipping_address["zip_code"])
    LOGGER.info("Phone Number=" + shipping_address["phone_number"])
    
    first_name = shipping_address["first_name"]
    last_name = shipping_address["last_name"]
    address = shipping_address["address"]
    apt = shipping_address["apt"]
    city = shipping_address["city"]
    st = shipping_address["state"]
    zip_code = shipping_address["zip_code"]
    phone_number = shipping_address["phone_number"]
        
    xpath = "//input[@data-qa='first-name-shipping']"

    LOGGER.info("Waiting for shipping options become visible")
    wait_until_visible(driver, xpath=xpath, duration=10)
    
    sa_input = driver.find_element_by_id("first-name-shipping")
    sa_input.clear()
    sa_input.send_keys(first_name)
    
    sa_input = driver.find_element_by_id("last-name-shipping")
    sa_input.clear()
    sa_input.send_keys(last_name)
    
    sa_input = driver.find_element_by_id("shipping-address-1")
    sa_input.clear()
    sa_input.send_keys(address)
    
    sa_input = driver.find_element_by_id("shipping-address-2")
    sa_input.clear()
    sa_input.send_keys(apt)
    
    sa_input = driver.find_element_by_id("city")
    sa_input.clear()
    sa_input.send_keys(city)
    
    sa_input = driver.find_element_by_id("state")
    sa_input.clear()
    sa_input.send_keys(st)
    
    sa_input = driver.find_element_by_id("zipcode")
    sa_input.clear()
    sa_input.send_keys(zip_code)
    
    sa_input = driver.find_element_by_id("phone-number")
    sa_input.clear()
    sa_input.send_keys(phone_number)
       
def select_shipping_option(driver, shipping_option):
    LOGGER.info("Selecting shipping")
    if shipping_option!="STANDARD":
        element = wait_until_present(driver, el_id=shipping_option, duration=10) 
        driver.execute_script("arguments[0].click();", element)
           
def input_cvv(driver, cvv):    
    xpath = "//div[@data-qa='payment-section']"

    LOGGER.info("Waiting for payment section to become visible")
    wait_until_visible(driver, xpath=xpath, duration=10)
    
    LOGGER.info("Waiting for cvv to become visible")
    
    WebDriverWait(driver, 10, 0.01).until(EC.frame_to_be_available_and_switch_to_it(driver.find_element_by_css_selector("iframe[title='creditCardIframeForm']")))
    
    idName = "cvNumber"
    wait_until_visible(driver, el_id=idName)
    cvv_input = driver.find_element_by_id("cvNumber")
    cvv_input.clear()
    cvv_input.send_keys(cvv)

    driver.switch_to.parent_frame()
       
def click_save_button(driver, xpath_o=None, check_disabled=True):
    if xpath_o:
        xpath = xpath_o
    else:
        xpath = "//button[text()='Save & Continue']"

    LOGGER.info("Waiting for save button class to become visible")
    
    element = wait_until_present(driver, xpath=xpath, duration=10)
    
    if check_disabled:
        wait = WebDriverWait(driver, 10, 0.01)
        wait.until(lambda d: 'disabled' not in element.get_attribute('class'))

    wait_until_clickable(driver, xpath=xpath, duration=10)

    LOGGER.info("Clicking save button")
    driver.find_element_by_xpath(xpath).click()
        
def click_add_new_address_button(driver):
    xpath = "//button[text()='Add New Address']"

    LOGGER.info("Waiting for Add New Address button to become clickable")
    wait_until_clickable(driver, xpath=xpath, duration=10)

    LOGGER.info("Clicking Add New Address button")
    driver.find_element_by_xpath(xpath).click()
    
def check_add_new_address_button(driver):
    xpath = "//button[text()='Add New Address']"

    LOGGER.info("Waiting for Add New Address button to become clickable")
    wait_until_clickable(driver, xpath=xpath, duration=.2)
    
def check_shipping(driver):
    xpath = "//span[@data-qa='shipping-method-date']"

    LOGGER.info("Waiting for shipping options become visible")
    wait_until_visible(driver, xpath=xpath, duration=.2)
    
def check_payment(driver):
    xpath = "//div[@data-qa='payment-section']"

    LOGGER.info("Waiting for payment section to become visible")
    wait_until_visible(driver, xpath=xpath, duration=.2)
    
def check_submit_button(driver, xpath_o=None):
    if xpath_o:
        xpath = xpath_o
    else:
        xpath = "//button[text()='Submit Order']"

    LOGGER.info("Waiting for submit button to become clickable")
    wait_until_clickable(driver, xpath=xpath, duration=.2)

def click_submit_button(driver, xpath_o=None):
    if xpath_o:
        xpath = xpath_o
    else:
        xpath = "//button[text()='Submit Order']"

    element = wait_until_present(driver, xpath=xpath, duration=10)
    wait = WebDriverWait(driver, 10, 0.01)
    wait.until(lambda d: 'disabled' not in element.get_attribute('class'))
    
    LOGGER.info("Waiting for submit button to become clickable")
    wait_until_clickable(driver, xpath=xpath, duration=10)

    LOGGER.info("Clicking submit button")
    driver.find_element_by_xpath(xpath).click()

def poll_checkout_phase_one(driver):
    #Loop to determine which element appears first
    #Limit this loop as "Verify Phone Number" dialog may appear
    checkout_num_retries_attempted = 0
    checkout_num_retries = 25
    skip_add_address = False
    skip_select_shipping = False
    skip_payment = False
    while True:
        try:
            check_add_new_address_button(driver=driver)
            LOGGER.info("New Address button appeared!")
            break
        except Exception as e:
            LOGGER.exception("Failed visibility check for Add New Address button: " + str(e))
            
        try:
            check_shipping(driver=driver)
            LOGGER.info("Shipping options appeared!")
            skip_add_address = True
            break
        except Exception as e:
            LOGGER.exception("Failed visibility check for Shipping options: " + str(e))
            
        try:
            check_payment(driver=driver)
            LOGGER.info("Payment appeared!")
            skip_add_address = True
            skip_select_shipping = True
            break
        except Exception as e:
            LOGGER.exception("Failed visibility check for Payment: " + str(e))
        
        try:
            xpath = SUBMIT_BUTTON_XPATH
            check_submit_button(driver=driver, xpath_o=xpath)
            LOGGER.info("Submit Button appeared!")
            skip_add_address = True
            skip_select_shipping = True
            skip_payment = True
            break
        except Exception as e:
            LOGGER.exception("Failed visibility check for Submit Button: " + str(e))
            
        if checkout_num_retries_attempted < checkout_num_retries:
            checkout_num_retries_attempted += 1
            continue
        else:
            LOGGER.info("Too many iterations through checkout element check. Terminating check...")
            break
            
        return skip_add_address, skip_select_shipping, skip_payment
        
def poll_checkout_phase_two(driver):
    #Loop again to determine which element appears first
    # as we don't know which will appear next
    checkout_num_retries_attempted = 0
    checkout_num_retries = 25
    skip_payment = False
    while True:
                            
        try:
            check_payment(driver=driver)
            LOGGER.info("Payment appeared!")
            break
        except Exception as e:
            LOGGER.exception("Failed visibility check #2 for Payment: " + str(e))
    
        try:
            xpath = SUBMIT_BUTTON_XPATH
            check_submit_button(driver=driver, xpath_o=xpath)
            LOGGER.info("Submit Button appeared!")
            skip_payment = True
            break
        except Exception as e:
            LOGGER.exception("Failed visibility check #2 for Submit Button: " + str(e))
        
        if checkout_num_retries_attempted < checkout_num_retries:
            checkout_num_retries_attempted += 1
            continue
        else:
            LOGGER.info("Too many iterations through checkout element check #2. Terminating check...")
            break
        
        return skip_payment

def wait_until_clickable(driver, xpath=None, class_name=None, el_id=None, duration=10000, frequency=0.01):
    if xpath:
        WebDriverWait(driver, duration, frequency).until(EC.element_to_be_clickable((By.XPATH, xpath)))
    elif class_name:
        WebDriverWait(driver, duration, frequency).until(EC.element_to_be_clickable((By.CLASS_NAME, class_name)))
    elif el_id:
        WebDriverWait(driver, duration, frequency).until(EC.element_to_be_clickable((By.ID, el_id)))


def wait_until_visible(driver, xpath=None, class_name=None, el_id=None, duration=10000, frequency=0.01):
    if xpath:
        WebDriverWait(driver, duration, frequency).until(EC.visibility_of_element_located((By.XPATH, xpath)))
    elif class_name:
        WebDriverWait(driver, duration, frequency).until(EC.visibility_of_element_located((By.CLASS_NAME, class_name)))
    elif el_id:
        WebDriverWait(driver, duration, frequency).until(EC.visibility_of_element_located((By.ID, el_id)))
        
def wait_until_present(driver, xpath=None, class_name=None, el_id=None, duration=10000, frequency=0.01):
    if xpath:
        return WebDriverWait(driver, duration, frequency).until(EC.presence_of_element_located((By.XPATH, xpath)))
    elif class_name:
        return WebDriverWait(driver, duration, frequency).until(EC.presence_of_element_located((By.CLASS_NAME, class_name)))
    elif el_id:
        return WebDriverWait(driver, duration, frequency).until(EC.presence_of_element_located((By.ID, el_id)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--url", required=True)
    parser.add_argument("--shoe-size", default=None)
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
    parser.add_argument("--shoe-type", default="M", choices=("M", "W", "Y", "C", "XXS", "XS", "S", "L", "XL"))
    parser.add_argument("--shipping-option", default="STANDARD", choices=("STANDARD", "TWO_DAY", "NEXT_DAY"))
    parser.add_argument("--cvv", default=None)
    parser.add_argument("--shipping-address", default=None)
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
    shoe_size = args.shoe_size
    
    if shoe_size is None and shoe_type in ("Y", "C", "W"):
    	raise Exception("Shoe size parameter must be passed in with your shoe type " + shoe_type + ".")
    
    if args.shipping_address: 
        shipping_address=json.loads(args.shipping_address)
    else:
        shipping_address=None
    
    run(driver=driver, shoe_type=shoe_type, username=args.username, password=args.password, url=args.url, shoe_size=args.shoe_size, shipping_option=args.shipping_option,
        login_time=args.login_time, release_time=args.release_time, shipping_address=shipping_address, page_load_timeout=args.page_load_timeout,
        screenshot_path=args.screenshot_path, html_path=args.html_path, select_payment=args.select_payment,
        purchase=args.purchase, num_retries=args.num_retries, dont_quit=args.dont_quit, cvv=args.cvv)
