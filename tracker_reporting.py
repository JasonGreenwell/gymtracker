import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.dates as mdates
from dateutil import parser
import logging

logging.basicConfig(filename='app.log', level=logging.INFO)

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

        return f'Last {days} days:\n' \
               f'Active Duty: {self.active_duty_numbers}\nCivilian: {self.civilian_numbers}\nRetirees: {self.retiree_numbers}' \
               f'\nTotal: {self.active_duty_numbers + self.civilian_numbers + self.retiree_numbers}'


    def show_chart(self):
        data = pd.read_sql_query(
            'SELECT dt_date as Date, category as Category, count(*) as Count FROM count WHERE category IS '
            '\'Active Duty\' GROUP BY dt_date, category ', self.db)
        data2 = pd.read_sql_query(
            'SELECT dt_date as Date, category as Category, count(*) as Count FROM count WHERE category IS '
            '\'Civilian\' GROUP BY dt_date, category ', self.db)
        data3 = pd.read_sql_query(
            'SELECT dt_date as Date, category as Category, count(*) as Count FROM count WHERE category IS '
            '\'Retired\' GROUP BY dt_date, category ', self.db)

        plt.plot(data.Date, data.Count, '-', label='Active Duty')
        plt.plot(data2.Date, data2.Count, '-', label='Civilian')
        plt.plot(data3.Date, data3.Count, '-', label='Retirees')
        plt.xlabel('Date')
        plt.ylabel('Number')
        plt.title('Patron Analysis')
        plt.legend()
        plt.show()