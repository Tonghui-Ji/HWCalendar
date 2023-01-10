from datetime import datetime,timedelta
from icalendar import Calendar, Event, vDatetime
import requests

class HuaweiCalendar:
    def __init__(self,year):
        # self.year = self.datetime.datetime.now().year
        self.year = year
        self.workdayDateList = []
        self.holidayDateList = []

    def getChinaHolidayList(self):
        ChinaHolidayList = []
        url = 'https://cdn.jsdelivr.net/gh/NateScarlet/holiday-cn@master/{year}.json'.format(year=self.year)
        res = requests.get(url=url, timeout=50)
        if res.status_code == 200:
            rawChinaHolidayList = res.json()['days']
        else:
            print('主网址请求失败，正在发起重试！！！')
            url = 'https://natescarlet.coding.net/p/github/d/holiday-cn/git/raw/master/{year}.json'.format(
                year=self.year)
            res = requests.get(url=url, timeout=5)
            if res.status_code == 404:
                print('年份异常，请检查入参')
                rawChinaHolidayList = res.json()['days']
        if len(rawChinaHolidayList) == 0:
            print('主网址发生未知错误，正在请求备用站点！！！')
            # 主站挂了直接except,并存储到本地
            url = 'https://natescarlet.coding.net/p/github/d/holiday-cn/git/raw/master/{year}.json'.format(
                year=self.year)
            res = requests.get(url=url)
            if res.status_code == 404:
                print('年份异常，请检查入参')
            rawChinaHolidayList = res.json()['days']
        if len(rawChinaHolidayList) == 0:
            print('主站及备用站点均无法访问，请稍后再试！')
            return

        for holiday in rawChinaHolidayList:       
            if holiday['isOffDay'] == True:
                ChinaHolidayList.append( {'summary':holiday['name']+'假期', \
                    'datetime':datetime.strptime(holiday['date'],'%Y-%m-%d'), \
                        'offDay': True} )
                self.holidayDateList.append(datetime.strptime(holiday['date'],'%Y-%m-%d').date())
            else:
                ChinaHolidayList.append( {'summary':holiday['name']+'调休', \
                    'datetime':datetime.strptime(holiday['date'],'%Y-%m-%d'), \
                        'offDay': False} )
                self.workdayDateList.append(datetime.strptime(holiday['date'],'%Y-%m-%d').date())

        return ChinaHolidayList

    def getHuaweiLastSatudayList(self): 
        if  len(self.workdayDateList) == 0 or len(self.holidayDateList) == 0:
            self.getChinaHolidayList()
        monthLastSatudayList = []
        for month in range(1,12):
            firstDate = datetime(self.year,month,20).date() # 因为月末的周六不会早于20号（不会早于22号）
            tmpDate= firstDate
            while tmpDate.month == firstDate.month:
                tmpDate += timedelta(days=1)
                if tmpDate.weekday() == 5: #this is Thursday 
                    lastSatudayDate = tmpDate
            # 以上可以判断出月末的周六，一下是华为日历的一些判定
            # 1.如果月末周六是法定节假日(包括节假日调休)，则提前一周
            # 2.如果月末周日是法定节假日的调休，则提前一周（避免连续上七天）
            # ChinaHolidayDateList = self.ChinaHolidayList()['date']
            if lastSatudayDate in self.holidayDateList or lastSatudayDate in self.workdayDateList:
                lastSatudayDate -= timedelta(weeks=1)
            if (lastSatudayDate + timedelta(days=1)) in self.workdayDateList:
                lastSatudayDate -= timedelta(weeks=1)      
            if lastSatudayDate == datetime(self.year,12,31).date():
                lastSatudayDate -= timedelta(weeks=1)

            monthLastSatudayList.append( {'summary':'华为月末周六加班', \
                'datetime': datetime.strptime(str(lastSatudayDate), '%Y-%m-%d'), \
                    'offDay': False} )
            
        return monthLastSatudayList
    def generateHuaweiCalender(self):
        cal = Calendar()
        
        specialDateList = []
        specialDateList.extend(self.getChinaHolidayList())  
        specialDateList.extend(self.getHuaweiLastSatudayList())
        print(specialDateList)

        for day in specialDateList:
            event = Event()
            event.add('summary', day['summary'])
            event.add('dtstart',day['datetime'].date())
            event.add('dtend', day['datetime'].date())
            event.add('sequence', 0)
            cal.add_component(event)

        f = open("huaweiCal.ics",'wb')
        f.write(cal.to_ical())
        f.close()

    def updateeHuaweiCalender(self):
        f = open("huaweiCal.ics",'rb')
        cal = Calendar()
        cal.add('version','2.0')

        for component in cal.from_ical(f.read()).walk():
            if component.name == "VEVENT":
                cal.add_component(component) 
        f = open("huaweiCal.ics",'wb')                 
        f.write(cal.to_ical())
        f.close()

if __name__ == '__main__':
    hc = HuaweiCalendar(2023)
    hc.generateHuaweiCalender()
    # hc.updateeHuaweiCalender()
