from tkinter import *
import os
import numpy as np
from main import run
from selenium import webdriver


class BotGUI:

    def __init__(self, app):
        self.app = app
        # Login Information Label
        self.login_information_label = Label(
            app, text="Login Information", font=('bold', 16))
        self.login_information_label.grid(row=0, column=0, sticky=W, pady=10)

        # Username
        self.username_text = StringVar()
        self.username_label = Label(app, text="username *", font=('bold', 10))
        self.username_label.grid(row=1, column=0, sticky=W, padx=25)
        self.username_entry = Entry(app, textvariable=self.username_text)
        self.username_entry.grid(row=2, column=0, sticky=W, padx=25)

        # Password
        self.password_text = StringVar()
        self.password_label = Label(app, text="password *", font=('bold', 10))
        self.password_label.grid(row=1, column=1, sticky=W, padx=25)
        self.password_entry = Entry(app, textvariable=self.password_text)
        self.password_entry.grid(row=2, column=1, sticky=W, padx=25)

        # Shoe Information Label
        self.shoe_information_label = Label(
            app, text="Shoe Information", font=('bold', 16))
        self.shoe_information_label.grid(row=3, column=0, sticky=W, pady=10)

        # Url
        self.url_text = StringVar()
        self.url_label = Label(app, text="url *", font=('bold', 10))
        self.url_label.grid(row=4, column=0, sticky=W, padx=25)
        self.url_entry = Entry(app, textvariable=self.url_text)
        self.url_entry.grid(row=5, column=0, sticky=W, padx=25)

        # Show size
        self.shoe_size_text = StringVar()
        self.shoe_size_label = Label(
            app, text="shoe size (Men)*", font=('bold', 10))
        self.shoe_size_label.grid(row=4, column=1, sticky=W, padx=25)
        self.OptionList = [8, 8.5, 9, 9.5, 10, 10.5, 11, 11.5, 12, 13, 14, 15]
        self.shoe_size = StringVar()
        self.shoe_size.set(self.OptionList[0])
        self.shoe_size_dropdown = OptionMenu(
            app, self.shoe_size, *self.OptionList)
        self.shoe_size_dropdown.config(width=15, font=('Helvetica', 10))
        self.shoe_size_dropdown.grid(row=5, column=1, sticky=W, padx=25)

        # Bot Settings Label
        self.bot_settings_label = Label(
            app, text="Bot Settings", font=('bold', 16))
        self.bot_settings_label.grid(row=6, column=0, sticky=W, )

        # Disable lable
        self.bot_settings_label = Label(
            app, text="Check box to disable feature", font=('Helvetica', 8))
        self.bot_settings_label.grid(row=7, column=0, sticky=W, padx=25)

        # Login Time Status
        self.login_time_int = IntVar(value=1)
        self.login_time_int_checkbox = Checkbutton(
            app, text="Login Time", variable=self.login_time_int, command=self.logTimeStatus)
        self.login_time_int_checkbox.grid(row=8, column=0, sticky=W, padx=25)

        # Release Time Status
        self.release_time_int = IntVar(value=1)
        self.release_time_int_checkbox = Checkbutton(
            app, text="Release Time", variable=self.release_time_int, command=self.releaseTimeStatus)
        self.release_time_int_checkbox.grid(row=8, column=0, sticky=E, padx=25)

        # Retrie Status
        self.retries_int = IntVar(value=1)
        self.retries_int_checkbox = Checkbutton(
            app, text="Retries", variable=self.retries_int, command=self.retriesStatus)
        self.retries_int_checkbox.grid(row=8, column=1, sticky=W, padx=25)

        # Page Load Status
        self.page_load_int = IntVar(value=1)
        self.page_load_int_checkbox = Checkbutton(
            app, text="Page Load", variable=self.page_load_int, command=self.pageLoadTimeoutStatus)
        self.page_load_int_checkbox.grid(row=8, column=1, sticky=E, padx=25)

        # Log in time
        self.login_time_label = Label(
            app, text="Login Time (Military Time HH:MM)", font=('bold', 10))
        self.login_time_label.grid(row=9, column=0, sticky=W, padx=25)
        self.HoursList = np.arange(24)
        self.login_time_hours = StringVar()
        self.login_time_hours.set(self.HoursList[9])
        self.login_time_hours_dropdown = OptionMenu(
            app, self.login_time_hours, *self.HoursList)
        self.login_time_hours_dropdown.config(width=3, font=('Helvetica', 10))
        self.login_time_hours_dropdown.grid(
            row=10, column=0, sticky=W, padx=25)

        self.MinutesList = np.arange(60)
        self.login_time_minutes = StringVar()
        self.login_time_minutes.set(self.MinutesList[59])
        self.login_time_minutes_dropdown = OptionMenu(
            app, self.login_time_minutes, *self.MinutesList)
        self.login_time_minutes_dropdown.config(
            width=3, font=('Helvetica', 10))
        self.login_time_minutes_dropdown.grid(row=10, column=0,  padx=25)

        # Release Time
        self.release_time_label = Label(
            app, text="Release Time (Military Time)", font=('bold', 10))
        self.release_time_label.grid(row=9, column=1, sticky=W, padx=25)
        self.HoursList = np.arange(24)
        self.release_time = StringVar()
        self.release_time.set(self.HoursList[10])
        self.release_time_dropdown = OptionMenu(
            app, self.release_time, *self.HoursList)
        self.release_time_dropdown.config(width=15, font=('Helvetica', 10))
        self.release_time_dropdown.grid(row=10, column=1, sticky=W, padx=25)

        # Page Load Timeout
        self.PageLoadTimeoutSecondsList = [1, 2, 3]
        self.page_load_timeout_label = Label(
            app, text="Page Load Timeout", font=('bold', 10))
        self.page_load_timeout_label.grid(row=11, column=0, sticky=W, padx=25)
        self.page_load_timeout = StringVar()
        self.page_load_timeout.set(self.PageLoadTimeoutSecondsList[0])
        self.page_load_timeout_dropdown = OptionMenu(
            app, self.page_load_timeout, *self.PageLoadTimeoutSecondsList)
        self.page_load_timeout_dropdown.config(
            width=15, font=('Helvetica', 10))
        self.page_load_timeout_dropdown.grid(
            row=12, column=0, sticky=W, padx=25)

        # Retries
        self.RetriesSecondsList = [1, 2, 3, 4, 5]
        self.retries_label = Label(
            app, text="Number of Retries", font=('bold', 10))
        self.retries_label.grid(row=11, column=1, sticky=W, padx=25)
        self.retries = StringVar()
        self.retries.set(self.RetriesSecondsList[0])
        self.retries_dropdown = OptionMenu(
            app, self.retries, *self.RetriesSecondsList)
        self.retries_dropdown.config(width=15, font=('Helvetica', 10))
        self.retries_dropdown.grid(row=12, column=1, sticky=W, padx=25)

        # Web Driver
        self.DriverList = ["firefox", "chrome"]
        self.driver_label = Label(
            app, text="Web Driver", font=('bold', 10))
        self.driver_label.grid(row=13, column=0, sticky=W, padx=25)
        self.driver = StringVar()
        self.driver.set(self.DriverList[0])
        self.driver_dropdown = OptionMenu(app, self.driver, *self.DriverList)
        self.driver_dropdown.config(width=15, font=('Helvetica', 10))
        self.driver_dropdown.grid(row=14, column=0, sticky=W, padx=25)

        # CVV
        self.cvv_text = StringVar()
        self.cvv_label = Label(app, text="cvv *", font=('bold', 10))
        self.cvv_label.grid(row=13, column=1, sticky=W, padx=25)
        self.cvv_entry = Entry(app, textvariable=self.cvv_text)
        self.cvv_entry.grid(row=14, column=1, sticky=W, padx=25)

        # Headless
        self.headless_int = IntVar()
        self.headless_checkbox = Checkbutton(
            app, text="Headless", variable=self.headless_int)
        self.headless_checkbox.grid(row=15, sticky=W, padx=25)

        # No Quit
        self.no_quit_int = IntVar()
        self.no_quit_checkbox = Checkbutton(
            app, text="Dont Quit After Purchase", variable=self.no_quit_int)
        self.no_quit_checkbox.grid(row=16, sticky=W, padx=25)

        # No Quit
        self.purchase_int = IntVar()
        self.purchase_checkbox = Checkbutton(
            app, text="Purchase", variable=self.purchase_int)
        self.purchase_checkbox.grid(row=17, sticky=W, padx=25)

        # Start Script
        self.btn = Button(app, text='Start', width=12, command=self.test)
        self.btn.grid(row=18, column=0, sticky=W, padx=25)

        # Disabled items since auto check is enabled
        self.login_time_label.grid_remove()
        self.login_time_minutes_dropdown.grid_remove()
        self.login_time_hours_dropdown.grid_remove()
        self.release_time_label.grid_remove()
        self.release_time_dropdown.grid_remove()
        self.retries_label.grid_remove()
        self.retries_dropdown.grid_remove()
        self.page_load_timeout_label.grid_remove()
        self.page_load_timeout_dropdown.grid_remove()

        app.title('Sneaker Bot')
        app.rowconfigure(20, {'minsize': 30})
        app.columnconfigure(20, {'minsize': 30})

    def test(self):

        options = webdriver.FirefoxOptions()
        if(self.headless_int.get() != 0):
            options.add_argument("--headless")

        if(self.purchase_int.get() != 0):
            purchase = True
        else:
            purchase = False

        if(self.release_time_int.get() != 1):
            release_time = self.release_time.get() + "h"

        if(self.page_load_int.get() != 1):
            page_load_timeout = self.page_load_timeout.get()

        driver = webdriver.Firefox(
            executable_path="./bin/geckodriver", firefox_options=options, log_path=os.devnull)

        if(self.username_entry.get() != "" and self.password_entry.get() != "" and self.url_entry.get() != "" and self.shoe_size.get() != "" and self.cvv_entry.get() != ""):
            command = 'py .\experimental.py  --username %s --password %s --url %s --shoe-size %s --driver-type %s --cvv %s' % (
                self.username_entry.get(), self.password_entry.get(), self.url_entry.get(), self.shoe_size.get(), self.driver.get(), self.cvv_entry.get())

            run(driver=driver, shoe_type="M", username=self.username_entry.get(), password=self.password_entry.get(
            ), url=self.url_entry.get(), shoe_size=self.shoe_size.get(), cvv=self.cvv_entry.get(), purchase=purchase, release_time=release_time, page_load_timeout=page_load_timeout)

            #  Determines if bot features where disabled.
            # if(self.login_time_int.get() != 1):
            #     command += ' --login-time %sh%sm' % (
            #         self.login_time_hours.get(), self.login_time_minutes.get())
            # if(self.release_time_int.get() != 1):
            #     command += ' --release-time %sh' % (self.release_time.get())

            # if(self.retries_int.get() != 1):
            #     command += ' --num-retries %s' % (self.retries.get())

            # if(self.page_load_int.get() != 1):
            #     command += ' --page-load-timeout %s' % (
            #         self.page_load_timeout.get())

            # if(self.headless_int.get() != 0):
            #     command += ' --headless'

            # if(self.no_quit_int.get() != 0):
            #     command += ' --dont-quit'

            # if(self.purchase_int.get() != 0):
            #     command += ' --purchase'

            # print(command)
            # os.system(command)

    def logTimeStatus(self):
        #  Removes widget if disable checkbox is checked
        if(self.login_time_int.get() == 1):
            self.login_time_label.grid_remove()
            self.login_time_hours_dropdown.grid_remove()
            self.login_time_minutes_dropdown.grid_remove()
        else:
            self.login_time_label.grid()
            self.login_time_hours_dropdown.grid()
            self.login_time_minutes_dropdown.grid()

    def releaseTimeStatus(self):
        if(self.release_time_int.get() == 1):
            self.release_time_label.grid_remove()
            self.release_time_dropdown.grid_remove()
        else:
            self.release_time_label.grid()
            self.release_time_dropdown.grid()

    def retriesStatus(self):
        if(self.retries_int.get() == 1):
            self.retries_label.grid_remove()
            self.retries_dropdown.grid_remove()
        else:
            self.retries_label.grid()
            self.retries_dropdown.grid()

    def pageLoadTimeoutStatus(self):
        if(self.page_load_int.get() == 1):
            self.page_load_timeout_label.grid_remove()
            self.page_load_timeout_dropdown.grid_remove()
        else:
            self.page_load_timeout_label.grid()
            self.page_load_timeout_dropdown.grid()


app = Tk()
BotGUI(app)
# Start program
app.mainloop()
