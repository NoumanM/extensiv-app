import threading
import time
from flask import Flask, request, render_template, jsonify
import schedule
import extensiv
app = Flask(__name__)



@app.route('/')
def home():
    return render_template('home.html')


@app.route('/getResults', methods=['POST'])
def my_form_post():
    data = request.get_json()
    person_names = data.get('personName', [])
    client_names = data.get('clientName', [])
    selected_date = data.get('selectedDate', '')
    endSelectedDate = data.get('endSelectedDate', '')
    print(selected_date)
    if len(person_names) == 0:
        person_names.append('None')

    if len(client_names) == 0:
        client_names.append('None')
    list_of_items = extensiv.average_picking_time_perday_in_sec(selected_date, endSelectedDate, person_names,
                                                                client_names)
    total_time = 0
    for one_item in list_of_items:
        total_time += float(one_item['avgTime'])
    total_avg_time = total_time // len(list_of_items)

    if 'None' in person_names and 'None' in client_names:
        result = {
            "createdProducts": f"Products Created: {extensiv.how_many_products_created_on_that_day(selected_date, endSelectedDate, person_names, client_names)}",
            "pickedProducts": f"Products Picked: {extensiv.how_many_products_picked_on_that_day(selected_date,endSelectedDate, person_names, client_names)}",
            # "averagePickingTime": f"Average Picking Time (sec): {total_avg_time}",
            "averagePickingTime": f"Average Picking Time (sec): {total_avg_time}",
            "clientName": client_names,
            "personName": person_names
        }
    else:
        result = {
            "createdProducts": f"Products Created: {extensiv.how_many_products_created_on_that_day(selected_date, endSelectedDate, person_names, client_names)}",
            "pickedProducts": f"Products Picked: {extensiv.how_many_products_picked_on_that_day(selected_date,endSelectedDate, person_names, client_names)}",
            "averagePickingTime": f"Average Picking Time (sec): {total_avg_time}",
            # "averagePickingTime": f"Average Picking Time (sec): {extensiv.average_picking_time_per_sec(selected_date, endSelectedDate, person_name, client_name)}",
            "clientName": client_names,
            "personName": person_names
        }


    result = {str(key): value for key, value in result.items()}
    return jsonify(result=result)


@app.route('/person', methods=['GET'])
def person_names():
    list_of_persons = extensiv.get_all_job_assignees()
    return list_of_persons

@app.route('/fetchTime', methods=['GET'])
def last_fetch_time():
    dateAndTime = extensiv.data_fetch_time_and_date()
    return dateAndTime

@app.route('/client', methods=['GET'])
def client_names():
    list_of_clients = extensiv.get_all_customer_names()
    return list_of_clients


@app.route('/fetch_data', methods=['GET'])
def fetch_new_data():
    msg = extensiv.fetch_and_write_data()
    if msg:
        success_msg = "Data Successfully Fetched..."
        return success_msg
    else:
        return "Data not fetched please try again."


@app.route('/productsCreatedLastSevenDays', methods=['POST'])
def prod_created_in_last_seven_days():
    data = request.get_json()
    person_names = data.get('personName', [])
    client_names = data.get('clientName', [])
    start_date = data.get('selectedDate', '')
    end_date = data.get('endSelectedDate', '')
    if len(person_names) == 0:
        person_names.append('None')

    if len(client_names) == 0:
        client_names.append('None')
    list_of_items = extensiv.products_created_in_last_seven_days(start_date, end_date, person_names, client_names)
    return jsonify(list_of_items)


@app.route('/productsPickedLastSevenDays', methods=['POST'])
def prod_picked_in_last_seven_days():
    data = request.get_json()
    person_names = data.get('personName', [])
    client_names = data.get('clientName', [])
    start_date = data.get('selectedDate', '')
    end_date = data.get('endSelectedDate', '')
    if len(person_names) == 0:
        person_names.append('None')

    if len(client_names) == 0:
        client_names.append('None')
    list_of_items = extensiv.products_picked_in_last_seven_days(start_date, end_date, person_names, client_names)
    return jsonify(list_of_items)


@app.route('/fetchAveragePickingTime', methods=['POST'])
def fetch_average_picking_time_per_day():
    data = request.get_json()
    person_names = data.get('personName', [])
    client_names = data.get('clientName', [])
    start_date = data.get('selectedDate', '')
    end_date = data.get('endSelectedDate', '')
    if len(person_names) == 0:
        person_names.append('None')

    if len(client_names) == 0:
        client_names.append('None')
    list_of_items = extensiv.average_picking_time_perday_in_sec(start_date, end_date, person_names, client_names)
    return jsonify(list_of_items)


# def schedule_periodic_task():
#     # Schedule the initial execution of the function
#     extensiv.fetch_and_write_data()
#
#     # Schedule the function to run every hour afterwards
#     schedule.every().hour.do(extensiv.fetch_and_write_data)
#
#     # Keep the scheduler running in a separate thread
#     while True:
#         schedule.run_pending()
#         time.sleep(1)
#
# # Start the periodic task scheduler in a separate thread
# scheduler_thread = threading.Thread(target=schedule_periodic_task)
# scheduler_thread.start()
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)