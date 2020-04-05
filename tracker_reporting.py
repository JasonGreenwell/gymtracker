import sqlite3
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from dateutil import parser


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