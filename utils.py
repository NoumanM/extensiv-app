from datetime import datetime, timedelta, date
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

def last_7_dates_from_today():
    today = date.today()
    last_7_dates = []

    for i in range(7):
        current_date = today - timedelta(days=i)
        last_7_dates.append(str(current_date))

    return last_7_dates


def get_dates_between(start_date, end_date):
    date_format = "%Y-%m-%d"
    start = datetime.strptime(start_date, date_format)
    end = datetime.strptime(end_date, date_format)

    # Calculate the number of days between start and end dates
    num_days = (end - start).days

    # Generate a list of dates between start and end dates
    dates = [start + timedelta(days=i) for i in range(num_days + 1)]

    # Format the dates as strings in the desired format
    formatted_dates = [date.strftime(date_format) for date in dates]

    return formatted_dates

def click_element(driver, by_locator):
    element = WebDriverWait(driver, 600).until(EC.element_to_be_clickable((By.XPATH, by_locator)))
    driver.execute_script(
        "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center', inline: 'nearest'})", element)
    element.click()


def get_todate():
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%dT%H:%M:%S")
    return formatted_datetime


def subtract_months(num_months):
    current_datetime = datetime.now()
    subtracted_datetime = current_datetime - timedelta(days=num_months * 30)
    formatted_date = subtracted_datetime.strftime("%Y-%m-%d")
    return formatted_date


def get_required_columns(response_list):
    required_params = {
        'Order Id': response_list.get('OrderId'),
        'Create Date': response_list.get('CreationDate'),
        'Pick Done Date': response_list.get('PickDoneDate'),
        'Close Date': response_list.get('ProcessDate'),
        'Reference Number': response_list.get('ReferenceNum'),
        'Product Number/Quantity': response_list.get('SkuAndQty'),
        'Pick Job Assignee': response_list.get('PickJobAssignee'),
        'Status': response_list.get('Status'),
        'Customer': response_list.get('Customer'),
        'CustomerId': response_list.get('CustomerId')
    }
    return required_params