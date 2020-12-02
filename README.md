# PLEASE READ!


This is a Selenium bot for buying a given sneaker from the Nike Snkrs website ON RELEASE DAY.
   It will not work for sneakers that are past their release day (or later in the release day).
   `Please note that this script was written with the US site in mind, so Nike sites for other countries will likely cause problems.`
   This is because the purchase page changes to where the buy button redirects to a seperate checkout page (as opposed to a direct buy popup during release).
It is a commandline script written solely in python. `Please run with python 3.7.`
There are 6 selenium drivers in the bin directory for both Chrome and Firefox on Linux, MacOS, and Winows. `The drivers for other operating systems need to be installed from the instructions below.`
I have found the Firefox driver for MacOS works best.

Ideally, some pieces (or all?) of this could be replaced with direct Nike API requests instead of Selenium. However, I've found that Nike APIs are not very straightforward.


# Getting started

There are a few requirements to run the bot. First, you'll need to install `Python 3.7` or greater. The instructions below show you how to do this in several operating systems

Next, we have provided the web drivers for MacOS, Linux, and Windows, but if they're not there, or you want something more up-to-date than the included drivers, you'll need to download them yourself with the instructions below

Finally, the program is run from the terminal (command line), so you should familiarize yourself with running python programs from the terminal [here](https://realpython.com/run-python-scripts/)

## Downloading python


This needs to be Python version `3.7` or up

MacOS
   * From Python's official website [here](https://www.python.org/downloads/mac-osx/)
   * If you have [brew](https://brew.sh) installed, you can just run the coommand `brew install python3`

Linux
   * From Python's official website [here](https://www.python.org/downloads/source/)
   * Using the package manager for your system. With Ubuntu, this command is `sudo apt install python3-dev`

Windows
   * From Python's official website [here](https://www.python.org/downloads/windows/)
   * If you have the [Chocolatey package manager](https://chocolatey.org/) installed, you can run `choco install python`

1. The selenium webdrivers for your chosen browser


## Installing the web drivers

* The drivers for most browsers can be found on selenium's site [here](https://www.selenium.dev/documentation/en/getting_started_with_webdriver/browsers/), although at the moment, only Firefox and Chrome are supported

* NOTE: There are already webdrivers for Chrome and Firefox, for MacOS, Linux, and Windows, which will be loaded if no other webdriver is specified manually

# Usage

1. Make sure that you have done all the Pre-installation requirements in the `Getting Started` section above

1. Clone this repository's source code
   1. If you have git installed, this can be done as easily as `git clone https://github.com/alexschimpf/Snkrs-Bot`
   1. Otherwise, download the zipped source code and unzip it

1. Navigate to the project's code
   * `cd path/to/downloaded/project`

1. Install all the Python dependencies by running
  * `pip install -r requirements.txt`

1. Run the bot
   * Replace all the fields in the command below with the options that you want, and any of the configuration options listed below
   ```bash
   python3 main.py --username myemail@gmail.com --password abc123 --url <your-shoes-url> --shoe-size 6 --driver-type chrome
   ```

# Configuration options

Here is a list and description of the different arguments to use for the script:

<b>--username</b>
* Username for login

<b>--password</b>
* Password for login

<b>--url</b>
* URL for desired shoe
* Size parameter can also be passed in (for example: https://www.nike.com/launch/t/kobe-5-protro-bruce-lee?size=11). In this case, `--shoe-size` and `--shoe-type` will be ignored
* DO NOT pass in size parameter with url on releases with "Additional Size Ranges" (i.e. children's shoes on same page) as it can lead to unexpected results

<b>--shoe-size</b>
* Self-explanatory

<b>--shoe-type</b>
* Men's (M), Women's (W), Youth (Y) or Child (C)
* For special releases (i.e. Air Presto), can pass in XXS, XS, S, M, L or XL. You do not need to pass in shoe size

<b>--cvv</b>
* Card Verification Value for your stored credit card
* May not be needed in some cases (for example, if you have previously purchased a release with a stored credit card)

<b>--shipping-option</b>
* STANDARD, TWO_DAY or NEXT_DAY

<b>--shipping-address</b>
* If given, the bot will attempt to add a new shipping address in some scenarios
* In some cases, checkout will not proceed without adding a new shipping address. If you are unsure, include it
* Must be in this format: '{"first_name":"John", "last_name":"Doe", "address":"1313 Mockingbird Lane", "apt":"", "city":"Long Beach", "state":"CA", "zip_code":"90712", "phone_number":"9999999999"}'

<b>--login-time</b>
* If given, the bot will pause until a specific time before it logs in (can be any datetime format)

<b>--release-time</b>
* If given, the bot will pause until a specific time before it purchase the sneaker (can be any datetime format)

<b>--screenshot-path</b>
* If given, the bot will take a screenshot of the page after purchasing and save it at the given file path (may be useful for debugging)

<b>--html-path</b>
* If given, the bot will take the page source after purchasing and save it at the given file path (may be useful for debugging)

<b>--page-load-timeout</b>
* This is used to limit the page load time (in seconds), which can be useful when the page is still loading, but the UI is nevertheless useable. This is pretty much a necessity as I've noticed Nike's pages hang all the time. I'd recommend using 1-3 seconds for this.

<b>--driver-type</b>
* Should be 'firefox' or 'chrome' (the OS will be determined for you)
* Defaults to `Firefox` if nothing is specified

<b>--webdriver-path</b>
* If specified, will use the specified driver instead of the defaults
* NOTE: The driver should match the browser specified in the `--driver-type` option (defaults to Firefox)

<b>--headless</b>
* This will run the driver in headless mode, which should make the bot quicker

<b>--select-payment</b>
* If you already have your payment options pre-saved on your Nike account, DO NOT use this. If for some reason you don't have it pre-saved (even though it will cost the bot more time) the bot will select the first payment option it finds.

<b>--purchase</b>
* If this argument is given, the bot WILL attempt to purchase the shoe so USE WITH CAUTION!

<b>--num-retries</b>
* If the bot fails for some reason, it will retry any number of times or until successful

<b>--dont-quit</b>
* Prevent browser from closing. Please note, if you are passing the `--purchase` parameter, it may be necessary to pass this parameter in
