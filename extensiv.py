import csv
import os
from selenium_stealth import stealth
import undetected_chromedriver as uc
import json
import requests
import math
import datetime
from payload import header_payload
import re
from webdriver_manager.chrome import ChromeDriverManager
from utils import *
from test_data import TestData

data_list = []


def get_data_from_API(page_start, headers, payload):
    global data_list
    final_data = []
    url = f"https://3w.extensiv.com/WebUI/Shipping/FindOrders/OrderData?sorts=[]&filters=[]&pgnum={page_start}&pgsiz=2000"
    response = requests.request("PUT", url, headers=headers, data=payload, timeout=60)
    data = json.loads(response.text)
    final_data = data['Data']
    for d in final_data:
        data_list.append(d)


def fetch_and_write_data():
    BASE_DIR = os.path.dirname(os.path.realpath(__file__))
    print("In fetch Data")
    global data_list
    options = uc.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument("--log-level=3")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.115 Safari/537.36")
    driver = uc.Chrome(driver_executable_path=ChromeDriverManager().install(),options=options)
    stealth(driver,
            user_agent='DN',
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )
    driver.implicitly_wait(20)

    driver.get("https://app.extensiv.com/login")
    try:
        driver.find_element(By.XPATH, "//input[@name='email']").send_keys(TestData.email)
        driver.find_element(By.XPATH, "//input[@name='password']").send_keys(TestData.password)
        driver.find_element(By.XPATH, "//button[@data-testid='LoginSubmitBtn']").click()
    except:
        driver.save_screenshot('error.png')
        print("Login Failed")
        pass

    pl_button = WebDriverWait(driver, 600).until(
        EC.element_to_be_clickable((By.XPATH, '//p[text()="3PL Warehouse Manager"]/ancestor::div[1]')))
    pl_button.click()

    frame_element = WebDriverWait(driver, 600).until(
        EC.presence_of_element_located((By.XPATH, "//iframe[@id='spaWrapperIframe']")))
    driver.switch_to.frame(frame_element)
    click_element(driver, by_locator='(//a[@title="Orders"])[last()]')
    # all_requests = []
    # loaded_requests = driver.requests
    # for i in loaded_requests:
    #     if i.url == 'https://cognito-idp.us-east-1.amazonaws.com/':
    #         response = i.response.body
    #         resp = json.loads(response)
    #         all_requests.append(resp)
    # authenticationResult = all_requests[1]['AuthenticationResult']
    # accessToken = authenticationResult['AccessToken']
    # idToken = authenticationResult['IdToken']
    # refreshToken = authenticationResult['RefreshToken']

    if os.path.isfile(f'{BASE_DIR}/cookies.json'):
        os.remove(f'{BASE_DIR}/cookies.json')
    with open(f'{BASE_DIR}/cookies.json', 'w') as cookie:
        cookie.write(json.dumps(driver.get_cookies()))

    with open('cookies.json', 'r') as outCookie:
        main_cookie = json.loads(outCookie.read())[1]
        session_id = main_cookie['value']

    payload, headers = header_payload(session_id)
    url = f"https://3w.extensiv.com/WebUI/Shipping/FindOrders/OrderData?sorts=[]&filters=[]&pgnum=1&pgsiz=2000"
    response = requests.request("PUT", url, headers=headers, data=payload, timeout=60)
    data = json.loads(response.text)
    total = math.ceil(data['Total'] / 2000)
    final_data = data['Data']
    for d in final_data:
        data_list.append(d)

    for i in range(2, total + 1):
        get_data_from_API(i, headers, payload)

    validate_data = list(map(get_required_columns, data_list))
    output_filename = 'output.csv'
    if os.path.isfile(output_filename):
        os.remove(output_filename)
    with open(output_filename, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=validate_data[0].keys())
        writer.writeheader()
        for d in validate_data:
            writer.writerow(d)

    driver.quit()

    with open("data_fetch_time.txt", mode="a+", encoding="utf-16") as file:
        file.write(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')

    if os.path.isfile(output_filename):
        os.remove('assignee.txt')
        os.remove('customer.txt')
        return True
    else:
        return False




def get_all_job_assignees():
    job_assignee_list = []
    assignee_file_name = 'assignee.txt'
    if os.path.isfile(assignee_file_name):
        with open(assignee_file_name, 'r', encoding='utf-16') as a_file:
            return a_file.read().splitlines()
    else:
        assignee_final_set = set()
        with open('output.csv', 'r') as file:
            reader = csv.reader(file)
            count = 0
            for row in reader:
                if count == 0:
                    count += 1
                    continue
                else:
                    if row[6] == '':
                        continue
                    assignee_final_set.add(row[6])

    for assignee in assignee_final_set:
        job_assignee_list.append(assignee)
        with open(assignee_file_name, mode="a+", encoding="utf-16") as file:
            file.write(f"{assignee}\n")
    return job_assignee_list


def get_all_customer_names():
    customer_names_list = []
    customer_file_name = 'customer.txt'
    if os.path.isfile(customer_file_name):
        with open(customer_file_name, 'r', encoding='utf-16') as a_file:
            return a_file.read().splitlines()
    else:
        customer_names_list_set = set()
        with open('output.csv', 'r') as file:
            reader = csv.reader(file)
            count = 0
            for row in reader:
                if count == 0:
                    count += 1
                    continue
                else:
                    if row[8] == '':
                        continue
                    customer_names_list_set.add(row[8])

    for customer in customer_names_list_set:
        customer_names_list.append(customer)
        with open(customer_file_name, mode="a+", encoding="utf-16") as file:
            file.write(f"{customer}\n")
    return customer_names_list


def how_many_products_created_on_that_day(start_date, end_date, person_name, clientName):
    item = {}
    for one_date in get_dates_between(start_date=start_date, end_date=end_date):
        with open('output.csv', 'r') as product_created:
            reader = csv.reader(product_created)
            item.update({one_date: []})
            for r in reader:
                if 'None' in person_name and 'None' in clientName:
                    if r[1].split('T')[0] == one_date:
                        try:
                            all_orders = re.findall(r'\((\d+)\)', r[5])
                            for order in all_orders:
                                item[one_date].append(int(order))
                        except:
                            pass
                if 'None' in clientName and 'None' not in person_name:
                    if r[6].strip() in person_name and r[1].split('T')[0] == one_date:
                        try:
                            all_orders = re.findall(r'\((\d+)\)', r[5])
                            for order in all_orders:
                                item[one_date].append(int(order))
                        except:
                            pass
                if  'None' in person_name and 'None' not in clientName:
                    if r[8].strip() in clientName and r[1].split('T')[0] == one_date:
                        try:
                            all_orders = re.findall(r'\((\d+)\)', r[5])
                            for order in all_orders:
                                item[one_date].append(int(order))
                        except:
                            pass

                else:
                    if r[6].strip() in person_name and r[8].strip() in clientName and r[1].split('T')[
                        0] == one_date:
                        try:
                            all_orders = re.findall(r'\((\d+)\)', r[5])
                            for order in all_orders:
                                item[one_date].append(int(order))
                        except:
                            pass

    total_products = 0
    for date in get_dates_between(start_date=start_date, end_date=end_date):
        try:
            total_products += sum(item[date])
        except:
            pass

    return total_products


def how_many_products_picked_on_that_day(start_date, end_date, personName, clientName):
    item = {}
    for date in get_dates_between(start_date=start_date, end_date=end_date):
        with open('output.csv', 'r') as product_created:
            reader = csv.reader(product_created)
            item.update({date: []})
            for r in reader:
                if 'None' in clientName and 'None' in personName:
                    if r[2].split('T')[0] == date:
                        try:
                            all_orders = re.findall(r'\((\d+)\)', r[5])
                            for order in all_orders:
                                item[date].append(int(order))
                        except:
                            pass
                if 'None' in clientName and 'None' not in personName:
                    if r[6].strip() in personName and r[2].split('T')[0] == date:
                        try:
                            all_orders = re.findall(r'\((\d+)\)', r[5])
                            for order in all_orders:
                                item[date].append(int(order))
                        except:
                            pass

                if 'None' in personName and 'None' not in clientName:
                    if r[8].strip() in clientName and r[2].split('T')[0] == date:
                        try:
                            all_orders = re.findall(r'\((\d+)\)', r[5])
                            for order in all_orders:
                                item[date].append(int(order))
                        except:
                            pass
                else:
                    if r[6].strip() in personName and r[8].strip() in clientName and r[2].split('T')[
                        0] == date:
                        try:
                            all_orders = re.findall(r'\((\d+)\)', r[5])
                            for order in all_orders:
                                item[date].append(int(order))
                        except:
                            pass

    total_products = 0
    for date in get_dates_between(start_date=start_date, end_date=end_date):
        try:
            total_products += sum(item[date])
        except:
            pass

    return total_products


def average_picking_time_per_sec(start_date, end_date, personName, clientName):
    item = {}
    number_of_products = how_many_products_picked_on_that_day(start_date, end_date, personName, clientName)
    if number_of_products != 0:
        for date in get_dates_between(start_date=start_date, end_date=end_date):
            with open('output.csv', 'r') as product_created:
                reader = csv.reader(product_created)
                item.update({date: []})
                for r in reader:
                    if clientName == 'None' and personName != 'None':
                        if r[6].strip() in personName and r[2].split('T')[0] == date:
                            try:
                                time_str = r[2].split('T')[1].split('.')[0]
                                time_obj = datetime.strptime(time_str, "%H:%M:%S").time()
                                item[date].append(time_obj)
                            except:
                                pass

                    if personName == 'None' and clientName != 'None':
                        if r[8].strip() in clientName and r[2].split('T')[0] == date:
                            try:
                                time_str = r[2].split('T')[1].split('.')[0]
                                time_obj = datetime.strptime(time_str, "%H:%M:%S").time()
                                item[date].append(time_obj)
                            except:
                                pass
                    else:
                        if r[6].strip() in personName and r[8].strip() in clientName and \
                                r[2].split('T')[
                                    0] == date:
                            try:
                                time_str = r[2].split('T')[1].split('.')[0]
                                time_obj = datetime.strptime(time_str, "%H:%M:%S").time()
                                item[date].append(time_obj)
                            except:
                                pass

        total_average_picking_time = 0
        all_dates = get_dates_between(start_date=start_date, end_date=end_date)
        for date in all_dates:
            try:
                min_time = min(item[date])
                max_time = max(item[date])

                fixed_date = datetime(1900, 1, 1)
                min_datetime = datetime.combine(fixed_date, min_time)
                max_datetime = datetime.combine(fixed_date, max_time)

                # Calculate time difference in seconds
                time_difference = max_datetime - min_datetime
                difference_in_seconds = time_difference.total_seconds()

                total_average_picking_time += (difference_in_seconds - 3600)
            except:
                all_dates.remove(date)
                print(date, "Data is missing")

        return_data = str(total_average_picking_time // number_of_products)
        return return_data.replace('-', '')

    else:
        return "No product found"


def products_created_in_last_seven_days(start, end, personName, clientName):
    item_list = []
    for date in get_dates_between(start_date=start, end_date=end):
        with open('output.csv', 'r') as input_file:
            file_data = csv.reader(input_file)
            total_orders = 0
            for row in file_data:
                if 'None' in personName and 'None' not in clientName:
                    if row[8].strip() in clientName and \
                            row[1].split('T')[
                                0] == date:
                        try:
                            all_orders = re.findall(r'\((\d+)\)', row[5])
                            for order in all_orders:
                                total_orders += int(order)
                        except:
                            pass

                if 'None' in clientName and 'None' not in personName:
                    if row[6].strip() in personName and \
                            row[1].split('T')[0] == date:
                        try:
                            all_orders = re.findall(r'\((\d+)\)', row[5])
                            for order in all_orders:
                                total_orders += int(order)
                        except:
                            pass

                if 'None' in clientName and 'None' in personName:
                    if row[1].split('T')[0] == date:
                        try:
                            all_orders = re.findall(r'\((\d+)\)', row[5])
                            for order in all_orders:
                                total_orders += int(order)
                        except:
                            pass

                if row[6].strip() in personName and row[8].strip() in clientName and row[1].split('T')[
                    0] == date:
                    try:
                        all_orders = re.findall(r'\((\d+)\)', row[5])
                        for order in all_orders:
                            total_orders += int(order)
                    except:
                        pass
            if total_orders != 0:
                item_list.append({'date': date, 'total_orders': str(total_orders)})

    return item_list


def products_picked_in_last_seven_days(start, end, personName, clientName):
    item_list = []
    for date in get_dates_between(start_date=start, end_date=end):
        with open('output.csv', 'r') as input_file:
            file_data = csv.reader(input_file)
            total_orders = 0
            for row in file_data:
                if 'None' in clientName and 'None' not in personName:
                    if row[6].strip() in personName and \
                            row[2].split('T')[
                                0] == date:
                        try:
                            all_orders = re.findall(r'\((\d+)\)', row[5])
                            for order in all_orders:
                                total_orders += int(order)
                        except:
                            pass

                if 'None' in personName and 'None' not in clientName:
                    if row[8].strip() in clientName and \
                            row[2].split('T')[
                                0] == date:
                        try:
                            all_orders = re.findall(r'\((\d+)\)', row[5])
                            for order in all_orders:
                                total_orders += int(order)
                        except:
                            pass

                if 'None' in clientName and 'None' in personName:
                    if row[2].split('T')[0] == date:
                        try:
                            all_orders = re.findall(r'\((\d+)\)', row[5])
                            for order in all_orders:
                                total_orders += int(order)
                        except:
                            pass

                if row[6].strip() in personName and row[8].strip() in clientName and row[2].split('T')[
                    0] == date:
                    try:
                        all_orders = re.findall(r'\((\d+)\)', row[5])
                        for order in all_orders:
                            total_orders += int(order)
                    except:
                        pass
            if total_orders != 0:
                item_list.append({'date': date, 'total_orders': str(total_orders)})

    return item_list


def average_picking_time_perday_in_sec(start_date, end_date, personName, clientName):
    item_list = []
    for date in get_dates_between(start_date=start_date, end_date=end_date):
        with open('output.csv', 'r') as product_created:
            reader = csv.reader(product_created)
            total_products_picked_on_day = []
            complete_time_list = []
            for r in reader:
                if 'None' in clientName and 'None' in personName:
                    if r[2].split('T')[0] == date:
                        try:
                            all_orders = re.findall(r'\((\d+)\)', r[5])
                            for order in all_orders:
                                total_products_picked_on_day.append(int(order))
                        except:
                            pass

                        try:
                            time_str = r[2].split('T')[1].split('.')[0]
                            time_obj = datetime.strptime(time_str, "%H:%M:%S").time()
                            complete_time_list.append(time_obj)
                        except:
                            pass
                elif 'None' in personName and 'None' not in clientName:
                    if r[8].strip() in clientName and r[2].split('T')[
                        0] == date:
                        try:
                            all_orders = re.findall(r'\((\d+)\)', r[5])
                            for order in all_orders:
                                total_products_picked_on_day.append(int(order))
                        except:
                            pass

                        try:
                            time_str = r[2].split('T')[1].split('.')[0]
                            time_obj = datetime.strptime(time_str, "%H:%M:%S").time()
                            complete_time_list.append(time_obj)
                        except:
                            pass

                elif 'None' in clientName and 'None' not in personName:
                    if r[6].strip() in personName and r[2].split('T')[
                        0] == date:
                        try:
                            all_orders = re.findall(r'\((\d+)\)', r[5])
                            for order in all_orders:
                                total_products_picked_on_day.append(int(order))
                        except:
                            pass

                        try:
                            time_str = r[2].split('T')[1].split('.')[0]
                            time_obj = datetime.strptime(time_str, "%H:%M:%S").time()
                            complete_time_list.append(time_obj)
                        except:
                            pass


                if r[6].strip() in personName and r[8].strip() in clientName and r[2].split('T')[
                    0] == date:
                    try:
                        all_orders = re.findall(r'\((\d+)\)', r[5])
                        for order in all_orders:
                            total_products_picked_on_day.append(int(order))
                    except:
                        pass

                    try:
                        time_str = r[2].split('T')[1].split('.')[0]
                        time_obj = datetime.strptime(time_str, "%H:%M:%S").time()
                        complete_time_list.append(time_obj)
                    except:
                        pass

            if len(total_products_picked_on_day) != 0:
                total_average_picking_time = 0
                try:
                    min_time = min(complete_time_list)
                    max_time = max(complete_time_list)

                    fixed_date = datetime(1900, 1, 1)
                    min_datetime = datetime.combine(fixed_date, min_time)
                    max_datetime = datetime.combine(fixed_date, max_time)

                    # Calculate time difference in seconds
                    time_difference = max_datetime - min_datetime
                    difference_in_seconds = time_difference.total_seconds()

                    total_average_picking_time += (difference_in_seconds - 3600)
                except:
                    print(date, "Data is missing")

                picking_time = total_average_picking_time // sum(total_products_picked_on_day)
                item_list.append({'date': date, "avgTime": str(picking_time).replace('-', '')})

    return item_list


def data_fetch_time_and_date():
    if os.path.isfile("data_fetch_time.txt"):
        with open("data_fetch_time.txt", 'r', encoding='utf-16 le') as a_file:
            return str((a_file.read().splitlines())[-1])
    else:
        return "No Latest Fetch"
