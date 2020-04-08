#! /usr/bin/env python3
import yagmail
import sqlite3
import matplotlib.pyplot as plt
import pandas as pd

db = sqlite3.connect("tracker.db")
cur = db.cursor()

def main():
    username = '@gmail.com'
    password = ''
    to_address = ''
    subject = 'Today\'s Gym Patron Report'
    message = f'{get_report(1)}\n\n{get_report(7)}\n\n{get_report(14)}'
    get_chart()
    attachments = 'gymtracker.pdf'

    email = yagmail.SMTP(username, password)

    email.send(to=[to_address], subject=subject, contents=message, attachments=attachments)


def get_report(days):

    # SQL Statements
    sql_ad = f'SELECT COUNT(*) FROM count WHERE dt_date BETWEEN DATE(\'now\', \'localtime\', \'-{days} day\'' \
                  f') AND DATE(\'now\', \'localtime\') AND category is \'Active Duty\''
    sql_civ = f'SELECT COUNT(*) FROM count WHERE dt_date BETWEEN DATE(\'now\', \'localtime\', \'-{days} day\'' \
               f') AND DATE(\'now\', \'localtime\') AND category is \'Active Duty\''
    sql_ret = f'SELECT COUNT(*) FROM count WHERE dt_date BETWEEN DATE(\'now\', \'localtime\', \'-{days} day\'' \
               f') AND DATE(\'now\', \'localtime\') AND category is \'Active Duty\''

    # Set numbers based on days for reuse
    active_duty_numbers = cur.execute(sql_ad).fetchone()[0]
    civilian_numbers = cur.execute(sql_civ).fetchone()[0]
    retiree_numbers = cur.execute(sql_ret).fetchone()[0]

    return f'Last {days} days:\n' \
           f'Active Duty: {active_duty_numbers}\nCivilian: {civilian_numbers}\nRetirees: ' \
           f'{retiree_numbers}\nTotal: {active_duty_numbers + civilian_numbers + retiree_numbers}'


def get_chart():

    ad_data = pd.read_sql_query(
        'SELECT dt_date as Date, category as Category, count(*) as Count FROM count WHERE category IS '
        '\'Active Duty\' GROUP BY dt_date, category ', db)
    civ_data = pd.read_sql_query(
        'SELECT dt_date as Date, category as Category, count(*) as Count FROM count WHERE category IS '
        '\'Civilian\' GROUP BY dt_date, category ', db)
    ret_data = pd.read_sql_query(
        'SELECT dt_date as Date, category as Category, count(*) as Count FROM count WHERE category IS '
        '\'Retired\' GROUP BY dt_date, category ', db)

    plt.plot(ad_data.Date, ad_data.Count, '-', label='Active Duty')
    plt.plot(civ_data.Date, civ_data.Count, '-', label='Civilian')
    plt.plot(ret_data.Date, ret_data.Count, '-', label='Retirees')
    plt.xlabel('Date')
    plt.ylabel('Number')
    plt.gcf().canvas.set_window_title('Gym Tracker (BETA)')
    plt.title('Patron Analysis')
    plt.suptitle("Gym Tracker")
    plt.legend()
    plt.savefig("gymtracker.pdf", bbox_inches='tight')

if __name__ == '__main__': main()