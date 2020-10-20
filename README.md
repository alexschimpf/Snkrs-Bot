# PLEASE READ!
---

This is a Selenium bot for buying a given sneaker from the Nike Snkrs website ON RELEASE DAY. 
   It will not work for sneakers that are past their release day (or later in the release day). 
   `Please note that this script was written with the US site in mind, so Nike sites for other countries will likely cause problems.`
   This is because the purchase page changes to where the buy button redirects to a seperate checkout page (as opposed to a direct buy popup during release).
It is a commandline script written solely in python. `Please run with python 3.7.`
There are 4 selenium drivers in the bin directory for both Chrome and Firefox on both Linux and MacOS. `I have not added the drivers for Windows.`
I have found the Firefox driver for MacOS works best.

Ideally, some pieces (or all?) of this could be replaced with direct Nike API requests instead of Selenium. However, I've found that Nike APIs are not very straightforward. 

Before running, make sure to install the requirements by running: `pip install -r requirements.txt`

Here is a list and description of the different arguments to use for the script:

<b>--username</b>
* Username for login

<b>--password</b>
* Password for login

<b>--url</b>
* URL for desired shoe

<b>--shoe-size</b>
* Self-explanatory

<b>--shoe-type</b>
* Men's (M), Women's (W), Youth (Y) or Child (C)

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

<b>--headless</b>
* This will run the driver in headless mode, which should make the bot quicker

<b>--select-payment</b>
* If you already have your payment options pre-saved on your Nike account, DO NOT use this. If for some reason you don't have it pre-saved (even though it will cost the bot more time) the bot will select the first payment option it finds.

<b>--purchase</b>
* If this argument is given, the bot WILL attempt to purchase the shoe so USE WITH CAUTION!

<b>--num-retries</b>
* If the bot fails for some reason, it will retry any number of times or until successful

<b>--dont-quit</b>
* Prevent window from closing (not headless mode). Useful if you wish to continue checkout process manually after Buy button is clicked

    
<br><br><br>
## Usage (Mac Only)
---
There are a few requirements to run the bot. First, you'll need to install [Python](https://www.python.org/downloads/) 3.7 or greater. The instructions below show you how to do this easily with [Brew](https://brew.sh/) but visiting Pythons website and downloading is an option but we're not providing instruction on how to do that. Next, if you decide to not use the drivers included with this repository, you'll need to download them yourself [here](https://www.selenium.dev/documentation/en/getting_started_with_webdriver/browsers/). Finally, the program is run from the terminal (command line), so you should familiarize yourself with running python programs from the terminal [here](https://realpython.com/run-python-scripts/).


### Instructions
1. Install Python:<br><br>
   `brew install python3` (with brew)<br><br>

2. Navigate to the root of the project:<br><br>
   `cd path/to/downloaded/project`<br><br>

3. Download the dependencies:<br><br>
   `pip3 install -r requirements.txt`<br><br>

4. (OPTIONAL) Download Chrome or Firefox driver [here](https://www.selenium.dev/documentation/en/getting_started_with_webdriver/browsers/).<br><br>
5. (OPTIONAL) Unzip the driver(s) and execute the binary.<br><br>


6. Run the bot from the project directory:<br><br>

```bash
$ python3 main.py --username myemail@gmail.com --password abc123 --url <your-shoes-url> --shoe-size 6 --driver-type chrome
```