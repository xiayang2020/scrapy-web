import requests
from colorama import init,Fore
from docopt import docopt
from stations import stations

from_station = '北京'
to_station = '长沙'
date ='2018-08-15'
options = 'dg'

from_station, to_station = stations[from_station], stations[to_station]
print(from_station, to_station)
url = 'https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date={}&leftTicketDTO.from_station={}&leftTicketDTO.to_station={}&purpose_codes=ADULT'.format(
    date, from_station, to_station)

r = requests.get(url, verify=False)
available_trains = r.json()['data']['result']
available_place = r.json()['data']['map']

# print(available_place)
for item in available_trains:
    cm = item.split('|')
    train_no = cm[3]
    initial = train_no[0].lower()      # 所有大写字母转换成小写字母
    duration = cm[10]                  # 历时
    if initial in options:
        train = [
            train_no,
            '\n'.join([Fore.GREEN + cm[6] + Fore.RESET,
                       Fore.RED + cm[7] + Fore.RESET]),
            '\n'.join([Fore.GREEN + cm[8] + Fore.RESET,
                       Fore.RED + cm[9] + Fore.RESET]),
            duration,
            cm[-4] if cm[-4] else '--',
            cm[-5] if cm[-5] else '--',
            cm[-14] if cm[-14] else '--',
            cm[-12] if cm[-12] else '--',
            cm[-7] if cm[-7] else '--',
            cm[-6] if cm[-6] else '--',
            cm[-9] if cm[-9] else '--'
        ]
        # print(train)
