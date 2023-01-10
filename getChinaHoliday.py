import datetime, requests

def get_current_year():
    '''获取当前的年份'''
    return datetime.datetime.now().year


def get_current_isoweekday(today=None):
    '''获取当前的星期数（返回数字1-7代表周一到周日）'''
    if not today:
        return datetime.datetime.now().isoweekday()
    else:
        return datetime.datetime.strptime(today, "%Y-%m-%d").isoweekday()

def getChinaHoliday(current_year=None):
    try:
        url = 'https://cdn.jsdelivr.net/gh/NateScarlet/holiday-cn@master/{year}.json'.format(year=current_year)
        res = requests.get(url=url, timeout=5)
        if res.status_code == 200:
            return res.json()['days']
        else:
            print('主网址请求失败，正在发起重试！！！')
            url = 'https://natescarlet.coding.net/p/github/d/holiday-cn/git/raw/master/{year}.json'.format(
                year=current_year)
            res = requests.get(url=url, timeout=5)
            if res.status_code == 404:
                print('年份异常，请检查入参')
            return res.json()['days']
    except:
        try:
            print('主网址发生未知错误，正在请求备用站点！！！')
            # 主站挂了直接except,并存储到本地
            url = 'https://natescarlet.coding.net/p/github/d/holiday-cn/git/raw/master/{year}.json'.format(
                year=current_year)
            res = requests.get(url=url)
            if res.status_code == 404:
                print('年份异常，请检查入参')
            return res.json()['days']
        except:
            print('主站及备用站点均无法访问，请稍后再试！')


if __name__ == '__main__':

    dd = getChinaHoliday(2022)
    print(dd[0],type(dd[0]['date']))
