# 12306 查票程序
import requests
from stations import stations
from colorama import init, Fore
from prettytable import PrettyTable

init()

class searchTrain:
    def __init__(self):
        self.trainOption = input('-g高铁 -d动车 -z直达 -t特快 -k快速, Please input the trainType you want to search :')
        self.fromStation = input('Please input the city you want leave :')
        self.toStation = input('Please input the city you will arrive :')
        self.tripDate = input('Please input the date(Example:2017-09-27) :')
        self.headers = {
            "Cookie": "自定义",
            "User-Agent": "自定义",
        }
        self.available_trains, self.options, self.available_place = self.searchTrain()

    @property
    def trains(self):
        for item in self.available_trains:
            cm = item.split('|')
            train_no = cm[3]
            initial = train_no[0].lower()      # 所有大写字母转换成小写字母,与后面匹配
            duration = cm[10]  # 历时
            # print(cm)
            # print(cm[6])
            # print(self.available_place[cm[6]])
            if not self.options or initial in self.options:
                train = [
                train_no,
                '\n'.join([Fore.LIGHTGREEN_EX + self.available_place[cm[6]] + Fore.RESET,
                           Fore.LIGHTRED_EX + self.available_place[cm[7]] + Fore.RESET]),
                '\n'.join([Fore.LIGHTGREEN_EX + cm[8] + Fore.RESET,
                           Fore.LIGHTRED_EX + cm[9] + Fore.RESET]),
                duration,
                cm[-5] if cm[-5] else '--',
                cm[-6] if cm[-6] else '--',
                cm[-7] if cm[-7] else '--',    # 二等座 ---
                cm[-16] if cm[-16] else '--',  # 高级软卧 --
                cm[-14] if cm[-14] else '--',    # 软卧  --
                cm[-9] if cm[-9] else '--',     # 硬卧  --
                '--',     # 软座
                cm[-8] if cm[-8] else '--',     # 硬座 ---
                cm[-11] if cm[-11] else '--',   # 无座  --
                '--'    # 其他
                ]
                yield train

    def pretty_print(self):
        pt = PrettyTable()
        #header = '车次 车站 时间 历时 一等 二等 高级软卧 软卧 硬卧 硬座 无座'.split()
        header = '车次 车站 时间 历时 商务座/特等座 一等 二等 高级软卧 软卧 硬卧 软座 硬座 无座 其他'.split()
        pt._set_field_names(header)
        for train in self.trains:
            pt.add_row(train)
        print(pt)

    def searchTrain(self):
        arguments = {
            'option': self.trainOption,
            'from': self.fromStation,
            'to': self.toStation,
            'date': self.tripDate
        }
        options = ''.join([item for item in arguments['option']])  # 车次类型
        # 得到出发地，目的地的代码简称
        from_station, to_station, date = stations[arguments['from']], stations[arguments['to']], arguments['date']
        # print(from_station, to_station)
        url = 'https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date={}&leftTicketDTO.from_station={}&leftTicketDTO.to_station={}&purpose_codes=ADULT'.format(
            date, from_station, to_station)
        r = requests.get(url, verify=False)
        available_trains = r.json()['data']['result']
        available_place = r.json()['data']['map']
        return available_trains, options, available_place


if __name__ == '__main__':
    while True:
        asd = searchTrain()
        asd.pretty_print()


