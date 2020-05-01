#! /usr/bin/env python3
from tkinter import *
from tkinter.filedialog import askdirectory
import tkinter.font
import sqlite3
import logging
import matplotlib.pyplot as plt
import pandas as pd
import pygame.mixer
import pygame
import smtplib
from tkinter.messagebox import showinfo
from apscheduler.schedulers.background import BackgroundScheduler


class App:

    # Static variables
    folder_location = ""  # Future static var for location of database for multiple apps
    logging.basicConfig(filename='app.log', level=logging.INFO)

    def __init__(self, master):

        # Initialize Auxillaries
        pygame.mixer.init()

        # Reset/Initialize Counts for Button Text and instant reports
        self.ad_num = 0
        self.civ_num = 0
        self.ret_num = 0

        self.active_duty_numbers = 0
        self.civilian_numbers = 0
        self.retiree_numbers = 0

        # Establish connection to database
        try:
            self.db = sqlite3.connect("tracker.db")
        except sqlite3.OperationalError as oe:
            logging.error(f"Error trying to connect to DB: {oe}")
        self.cur = self.db.cursor()

        # Set Fonts
        default_font = tkinter.font.Font(family='Helvetica', size=48, weight='bold')

        # Buttons
        self.btn_adres = Button(master, text="0", command=lambda: self.onclick_ad(), font=default_font,
                                bg='#003B74', fg='white', relief=FLAT, bd=0, highlightthickness=0,
                                highlightcolor="#003B74", cursor="none",activeforeground='white',
                                activebackground='#003B74', height=1, width=3)

        self.btn_civ = Button(master, text="0", command=lambda: self.onclick_civ(), font=default_font,
                              bg='#328400', fg='white', relief=FLAT, bd=0, highlightthickness=0,
                              highlightcolor="#328400", cursor="none", activeforeground='white',
                              activebackground='#328400', height=1, width=3)

        self.btn_ret = Button(master, text="0", command=lambda: self.onclick_ret(), font=default_font,
                              bg='#A00004', fg='white', relief=FLAT, bd=0, highlightthickness=0,
                              highlightcolor="#A00004", cursor="none", activeforeground='white',
                              activebackground='#A00004', height=1, width=3)

        # Background Image
        self.filename = PhotoImage(file="Assets/gym9.png")
        self.background_label = Label(master, image=self.filename)

        # Menu Bar
        self.menubar = Menu(master)
        self.filemenu = Menu(self.menubar, relief=FLAT, font=default_font, tearoff=0)
        self.filemenu.add_command(label="Show Report", command=self.show_chart)
        self.filemenu.add_command(label="E-Mail", command=self.email)
        self.filemenu.add_command(label="Quit", command=master.destroy)
        self.menubar.add_cascade(label='Admin', menu=self.filemenu)

        # Place Widgets
        self.background_label.place(x=0, y=0)
        self.background_label.lower(self.btn_adres)

        master.config(menu=self.menubar)

        self.btn_adres.place(x=100, y=925)
        self.btn_civ.place(x=747, y=925)
        self.btn_ret.place(x=1370, y=925)

        # Start reset everyday at midnight
        self.sched = BackgroundScheduler()
        self.sched.add_job(self.reset, trigger='cron', hour=0, minute=0)
        self.sched.start()

    def onclick_ad(self):
        # Save to database
        self.save_db("Active Duty")

        # Increment ad numbers and update display
        self.ad_num += 1
        self.btn_adres.configure(text=self.ad_num)

        # Load and play sound
        pygame.mixer.music.load("Assets/Whistle-noise.mp3")
        pygame.mixer.music.play(0)

    def onclick_civ(self):
        # Save to database
        self.save_db("Civilian")

        # Increment civilian numbers and update display
        self.civ_num += 1
        self.btn_civ.configure(text=self.civ_num)

        # Load and play sound
        pygame.mixer.music.load("Assets/Retro.mp3")
        pygame.mixer.music.play(0)

    def onclick_ret(self):
        # Save to database
        self.save_db("Retired")

        # Increment retiree numbers and update display
        self.ret_num += 1
        self.btn_ret.configure(text=self.ret_num)

        # Load and play sound
        pygame.mixer.music.load("Assets/Wrong-number.mp3")
        pygame.mixer.music.play(0)

    def email(self):

        fromaddr = ''
        toaddr = ['']
        SUBJECT = "Totals for "
        TEXT = f'{self.get_report(1)}\n\n{self.get_report(7)}\n\n{self.get_report(14)}'
        msg = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)
        username = '@gmail.com'
        password = ''
        server = smtplib.SMTP('smtp.gmail.com:587')

        try:
            server.starttls()
            server.login(username, password)
            server.sendmail(fromaddr, toaddr, msg)
            showinfo("SUCCESS!", "E-mail Sent")
        except Exception as e:
            logging.error(f"Server connection error: {e}")
            showinfo("FAILED!", "Error Sending Email. See app.log for further details.")
        finally:
            server.quit()

    def save_db(self, category):

        # SQL Statements
        sql_create_table = 'create table if not exists count(dt_date DATE, dt_time DATE, category TEXT)'
        sql_insert = f'INSERT INTO count VALUES (DATE(\'now\', \'localtime\'), TIME(\'now\', \'localtime\'), "{category}")'

        # Execute the above statements
        try:
            self.cur.execute(sql_create_table)
            self.cur.execute(sql_insert)
            self.db.commit()
        except Exception as e:
            logging.error(f"Error trying to execute SQL: {e}")

    def get_report(self, days):

        # SQL Statements
        sql_ad = f'SELECT COUNT(*) FROM count WHERE dt_date BETWEEN DATE(\'now\', \'localtime\', \'-{days} day\'' \
                      f') AND DATE(\'now\', \'localtime\') AND category is \'Active Duty\''
        sql_civ = f'SELECT COUNT(*) FROM count WHERE dt_date BETWEEN DATE(\'now\', \'localtime\', \'-{days} day\'' \
                   f') AND DATE(\'now\', \'localtime\') AND category is \'Active Duty\''
        sql_ret = f'SELECT COUNT(*) FROM count WHERE dt_date BETWEEN DATE(\'now\', \'localtime\', \'-{days} day\'' \
                   f') AND DATE(\'now\', \'localtime\') AND category is \'Active Duty\''

        # Set numbers based on days for reuse
        self.active_duty_numbers = self.cur.execute(sql_ad).fetchone()[0]
        self.civilian_numbers = self.cur.execute(sql_civ).fetchone()[0]
        self.retiree_numbers = self.cur.execute(sql_ret).fetchone()[0]

        return f'Last {days} days:\n' \
               f'Active Duty: {self.active_duty_numbers}\nCivilian: {self.civilian_numbers}\nRetirees: ' \
               f'{self.retiree_numbers}\nTotal: {self.active_duty_numbers + self.civilian_numbers + self.retiree_numbers}'

    def show_chart(self):

        ad_data = pd.read_sql_query(
            'SELECT dt_date as Date, category as Category, count(*) as Count FROM count WHERE category IS '
            '\'Active Duty\' GROUP BY dt_date, category ', self.db)
        civ_data = pd.read_sql_query(
            'SELECT dt_date as Date, category as Category, count(*) as Count FROM count WHERE category IS '
            '\'Civilian\' GROUP BY dt_date, category ', self.db)
        ret_data = pd.read_sql_query(
            'SELECT dt_date as Date, category as Category, count(*) as Count FROM count WHERE category IS '
            '\'Retired\' GROUP BY dt_date, category ', self.db)

        plt.plot(ad_data.Date, ad_data.Count, '-', label='Active Duty')
        plt.plot(civ_data.Date, civ_data.Count, '-', label='Civilian')
        plt.plot(ret_data.Date, ret_data.Count, '-', label='Retirees')
        plt.xlabel('Date')
        plt.ylabel('Number')
        plt.gcf().canvas.set_window_title('Gym Tracker (BETA)')
        plt.title('Patron Analysis')
        plt.suptitle("Gym Tracker")
        plt.legend()
        plt.show()

    def set_db(self):
        """
        Future implementation: Allow user to set folder location for database
        :return:
        """
        folder_location = askdirectory()

    def __del__(self):
        """
        Destructor to close database connection
        :return: None
        """
        self.db.close()
        self.sched.shutdown()

    def reset(self):

        self.ad_num = 0
        self.civ_num = 0
        self.ret_num = 0

        self.btn_adres.configure(text=self.ad_num)
        self.btn_civ.configure(text=self.civ_num)
        self.btn_ret.configure(text=self.ret_num)


def main():
    root = Tk()
    app = App(root)

    # Settings
    root.state('zoomed')  # root.attributes("-fullscreen", True) for linux
    root.title('Awesome Gym Counter')

    # Start GUI
    root.mainloop()

if __name__ == '__main__': main()