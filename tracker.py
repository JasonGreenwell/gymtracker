import tkinter
import tkinter.font
from tkinter import *
import smtplib
import pygame.mixer
import pygame
import datetime
import sqlite3
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from dateutil import parser
from matplotlib import style
style.use('fivethirtyeight')

todays_date = datetime.date.today()
timedelta = datetime.timedelta(days=6)
date1 = todays_date
date2 = date1 - timedelta
day1 = date1.strftime("%d %b %y")
day2 = date2.strftime("%d %b %y")
assets_folder = "Assets/"


class GymTracker:

    def __init__(self):
        pass

    def gui(self):

        root = tkinter.Tk()
        root.wm_attributes('-alpha', '0.0')
        root.wm_attributes('-fullscreen', True)
        filename = PhotoImage(file=assets_folder + "gym9.png")
        background_label = Label(root, image=filename)
        background_label.place(x=0, y=0)
        root.title("Awesome Gym Counter")
        myFont = tkinter.font.Font(family='Helvetica', size=48, weight='bold')

        pygame.mixer.init()
        pygame.init()

        # Menu bar
        menubar = Menu(root)
        filemenu = Menu(menubar, relief=FLAT, font=myFont, tearoff=0)
        filemenu.add_command(label="E-Mail", command=self.email)
        filemenu.add_command(label="Quit", command=root.destroy)
        menubar.add_cascade(label='Admin', menu=filemenu)

        # Display MenuBar
        root.config(menu=menubar)
        global ad
        global civ
        global ret

        ad = tkinter.IntVar()
        civ = tkinter.IntVar()
        ret = tkinter.IntVar()

        # AD
        tkinter.Button(root, textvariable=ad, command=self.onClick_ad, font=myFont, bg='#003B74', fg='white',
                       relief=FLAT, bd=0, highlightthickness=0, highlightcolor="#003B74", cursor="none",
                       activeforeground='white', activebackground='#003B74', height=1, width=3).place(x=100, y=925)

        # Civilian
        tkinter.Button(root, textvariable=civ, command=self.onClick_civ, font=myFont, bg='#328400', fg='white',
                       relief=FLAT, bd=0, highlightthickness=0, highlightcolor="#328400", cursor="none",
                       activeforeground='white', activebackground='#328400', height=1, width=3).place(x=747, y=925)

        # Retired
        tkinter.Button(root, textvariable=ret, command=self.onClick_ret, font=myFont, bg='#A00004', fg='white',
                       relief=FLAT, bd=0, highlightthickness=0, highlightcolor="#A00004", cursor="none",
                       activeforeground='white', activebackground='#A00004', height=1, width=3).place(x=1370, y=925)

        mainloop()

    def email(self):
        ## Insert email address you would like to mail from
        fromaddr = 'email@email.com'
        ## Insert email address you would like to send to
        toaddrs = ['email@email.com']
        SUBJECT = "Totals for " + str(day2) + " -- " + str(day1)
        TEXT = ','.join(["AD #'s-" + str(ad.get()) + '\n' + "Civ #'s-" + str(civ.get())
                         + '\n' + "Ret #'s -" + str(ret.get())])
        msg = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)
        ## Credentials (if needed)
        ## I used gmail so setup below is for gmail
        ## Enter use name
        username = 'username'
        ## Enter password for email account
        password = 'password'
        # The actual mail send
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.starttls()
        server.login(username, password)
        server.sendmail(fromaddr, toaddrs, msg)
        server.quit()
        print('Email Sent!')
        print(datetime.datetime.now())

        ad.set(ad.get() * 0)
        civ.set(civ.get() * 0)
        ret.set(ret.get() * 0)

    # AD##
    def onClick_ad(self, event=None):
        #ad.set(ad.get() + 1)
        #print("AD #'s-" + str(ad.get()))
        #pygame.mixer.music.load(assets_folder + "Whistle-noise.mp3")
        #pygame.mixer.music.play(0)
        self.save_db("Active Duty")

    # Civ##
    def onClick_civ(self, event=None):
        #civ.set(civ.get() + 1)
        #print("Civilian #'s-" + str(civ.get()))
        #pygame.mixer.music.load(assets_folder + "Retro.mp3")
        #pygame.mixer.music.play(0)
        self.save_db("Civilian")

    # Retired##
    def onClick_ret(self, event=None):
        #ret.set(ret.get() + 1)
        #print("Retired #'s-" + str(ret.get()))
        #pygame.mixer.music.load(assets_folder + "Wrong-number.mp3")
        #pygame.mixer.music.play(0)
        self.save_db("Retired")

    def save_db(self, category):
        try:
            db = sqlite3.connect("tracker.db")
        except sqlite3.OperationalError as oe:
            print(f"Could not connect to database{db}: {oe}")
        cur = db.cursor()

        # Create table if it does not exist
        sql = 'create table if not exists count(dt_date DATE, dt_time DATE, category TEXT)'
        cur.execute(sql)
        db.commit()

        # Insert date/time and category clicked
        cur.execute(f'INSERT INTO count VALUES (DATE(\'now\', \'localtime\'), TIME(\'now\', \'localtime\'), "{category}")')
        db.commit()
        db.close()


class Reporting:

    def __init__(self):
        try:
            self.db = sqlite3.connect("tracker.db")
        except sqlite3.OperationalError as oe:
            print(f"Could not connect to database{self.db}: {oe}")
        self.cur = self.db.cursor()

        self.active_duty_numbers = 0
        self.civilian_numbers = 0
        self.retiree_numbers = 0

    def get_report(self, days):

        active_duty = f'SELECT COUNT(*) FROM count WHERE dt_date BETWEEN DATE(\'now\', \'localtime\', \'-{days} day\'' \
                      f') AND DATE(\'now\', \'localtime\') AND category is \'Active Duty\''
        civilian = f'SELECT COUNT(*) FROM count WHERE dt_date BETWEEN DATE(\'now\', \'localtime\', \'-{days} day\'' \
                   f') AND DATE(\'now\', \'localtime\') AND category is \'Active Duty\''
        retirees = f'SELECT COUNT(*) FROM count WHERE dt_date BETWEEN DATE(\'now\', \'localtime\', \'-{days} day\'' \
                   f') AND DATE(\'now\', \'localtime\') AND category is \'Active Duty\''

        self.active_duty_numbers = self.cur.execute(active_duty).fetchone()[0]
        self.civilian_numbers = self.cur.execute(civilian).fetchone()[0]
        self.retiree_numbers = self.cur.execute(retirees).fetchone()[0]

        self.db.close()

        return f'Last {days} days:\n' \
               f'Active Duty: {self.active_duty_numbers}\nCivilian: {self.civilian_numbers}\nRetirees: {self.retiree_numbers}' \
               f'\nTotal: {self.active_duty_numbers + self.civilian_numbers + self.retiree_numbers}'


    def show_chart(self):
        # TODO: Clean Up Chart

        self.cur.execute('SELECT dt_date, category, count(*) FROM count  GROUP BY dt_date, category ')
        data = self.cur.fetchall()
        print(data)

        cat = []
        date = []
        total = []

        for row in data:
            cat.append(row[0])
            date.append(row[1])
            total.append(row[2])

        plt.plot_date(cat, total, date, '-')
        plt.show()
