import selenium.webdriver
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta, date
import calendar
from group_schedule import number_of_day, available_groups, available_days
from db_schedule import ScheduleDB

url = "https://sibsutis.ru/students/schedule/?type=student"

driver = ''
ScheduleDB = ScheduleDB('databases/schedule.db')


def select_group(group):
    driver.find_element(By.CLASS_NAME, 'select2-selection__rendered').click()
    driver.find_element(By.CLASS_NAME, 'select2-search__field').send_keys(group)
    time.sleep(1.5)
    driver.find_element(By.CLASS_NAME, 'select2-results__option').click()


def get_data(day, from_date=datetime.now()):
    search_day = available_days.index(day)
    from_day = from_date.weekday()
    if from_date.isoweekday() == 7:
        different_days = 7 + search_day - from_day if from_day >= search_day else from_day + search_day
    else:
        different_days = search_day - from_day if from_day >= search_day else search_day - from_day

    data_of_day = from_date + timedelta(days=different_days)

    return f'{"0" + data_of_day.day.__str__() if data_of_day.day < 10 else data_of_day.day}.' \
           f'{"0" + data_of_day.month.__str__() if data_of_day.month < 10 else data_of_day.month}'


def get_week_num(day: int = datetime.now().day, month: int = datetime.now().month,
                 year: int = datetime.now().year):
    calendar_ = calendar.TextCalendar(calendar.MONDAY)
    lines = calendar_.formatmonth(year, month).split('\n')
    days_by_week = [week.lstrip().split() for week in lines[2:]]
    str_day = str(day)
    for index, week in enumerate(days_by_week):
        if str_day in week:
            # проверка на воскресенье
            if datetime.now().isoweekday() == 7:
                return not bool((index + 1) % 2)
            else:
                return bool((index + 1) % 2)
        # False - 0 т.е. четная
        # True - 1 т.е. нечетная

    raise ValueError(f'Нет дня с номером {day} в месяце с номером {month} в {year} году!')


def find_first_monday(year, month):
    d = datetime(year, int(month), 7)
    offset = -d.weekday()
    dt = str((d + timedelta(offset)).date()).split('-')
    dt.remove(str(datetime.now().year))
    even_or_odd = get_week_num(int(dt[1]), int(dt[0]), datetime.now().year)
    return dt[::-1], even_or_odd


def fix_selday_tostr(dt, d):
    if len(str(d)) == 1:
        return '.'.join(['0' + str(d), dt[1]])
    else:
        return '.'.join([str(d), dt[1]])


def select_days(group):
    dt, even_or_odd = find_first_monday(datetime.now().year, datetime.now().month)
    res_even = []
    res_odd = []
    for day in number_of_day:
        # просчитываем first_week
        d = int(dt[0]) + number_of_day[day]
        selected_day = fix_selday_tostr(dt, d)
        driver.find_element(By.LINK_TEXT, selected_day).click()
        time.sleep(0.8)
        first_week = scrap_day()

        # просчитываем second_week
        d = 7 + int(dt[0]) + number_of_day[day]
        selected_day = fix_selday_tostr(dt, d)
        driver.find_element(By.LINK_TEXT, selected_day).click()
        time.sleep(0.8)
        second_week = scrap_day()

        # в зависимости от того какая была 1 неделя (чет/нечет) заносим в список
        # если четная
        if not even_or_odd:
            res_odd.append(second_week)
            res_even.append(first_week)
        # если нечетная
        else:
            res_odd.append(first_week)
            res_even.append(second_week)

    info = (group, *res_even, *res_odd)

    if not ScheduleDB.schedule_exists(group):
        ScheduleDB.add_schedule(info)
    else:
        print("Расписание уже есть в БД")


def scrap_day():
    schedule = {}
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    less = soup.find(class_="schedule__item")
    by_strings = list(less)

    info = []
    for i in range(len(by_strings) - 1):
        if by_strings[i].text != '':
            if by_strings[i + 1].name != 'hr':
                info.append(by_strings[i + 1].find('h6').text)
                info.append(by_strings[i + 1].find('span').text)
                for el in by_strings[i + 1].find(class_='card-body').findAll('div'):
                    if 'группа' not in el.text:
                        info.append(el.text)

                schedule[by_strings[i].text] = info
                info = []

    return make_result(schedule)


def make_result(schedule):
    result = ''
    if not schedule:
        return 'Занятий нет'
    for key in schedule:
        if len(schedule[key]) == 4:
            auditorium = ', ' + schedule[key][3] + '\n'
        else:
            auditorium = '\n'

        if schedule[key][1] == 'Практические занятия':
            result += key + ' - Практика' + auditorium + schedule[key][0] + '\n' + schedule[key][2] + '\n\n'
        else:
            result += key + ' - Лекция' + auditorium + schedule[key][0] + '\n' + schedule[key][2] + '\n\n'

    return result


def make_schedule(group):
    try:
        global driver
        driver = webdriver.Chrome(executable_path=r"chromedriver\chromedriver.exe")
        driver.get(url)

        select_group(group)
        select_days(group)

    except Exception as ex:
        print(ex)
        return -1
    finally:
        driver.close()
        driver.quit()



def get_schedule(group, day):
    if get_week_num(datetime.now().day, datetime.now().month, datetime.now().year):
        return ScheduleDB.get_schedule_odd(group, number_of_day[day])
    else:
        return ScheduleDB.get_schedule_even(group, number_of_day[day])


def fill_db():
    checksum_succes = 0
    checksum_failed = 0
    max_attempts = 2
    reply = []
    for group in available_groups:
        retrying = 0
        while not ScheduleDB.schedule_exists(group) and retrying != max_attempts:
            retrying += 1
            if make_schedule(group) != -1:
                checksum_succes += 1
                print(f'Расписание группы {group} - Добавлено!')
            else:
                if retrying == max_attempts:
                    checksum_failed += 1
                    reply.append(group)
                    print(f'Расписание группы {group} - Не удалось добавить!')

    return f'Успешно доабавлено {checksum_succes}. Не удалось добавить {checksum_failed} {reply}'


def reset_db():
    ScheduleDB.delete_all()
    return 'БД успешно очищена'
