import requests
import time
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import config
from random import *

request_params = {'token': config.bot_token}
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name(config.credentials_file_name, scope)
gc = gspread.authorize(credentials)
worksheet = gc.open('Test').sheet1

random_number_list = []


#TEST
def show_shifts_command():
    to_send = "Please go to this link to see available shifts: https://docs.google.com/spreadsheets/d/1REpCAbxi9rU6mHWmvY94vKlBw-rnW12471cSAZw2vqg/edit#gid=0"
    post_params = {'bot_id' : config.bot_id, 'text': to_send}
    requests.post('https://api.groupme.com/v3/bots/post', params = post_params)



def add_shifts_command(message):


    shifts = []
    ##If student puts multiple shifts in one message, it should be split by a new line
    if ('\n' in message['text']):
        shifts = message['text'].split("\n")

    else:
        shifts.append(message['text'])


    for shift in shifts:
        args = shift.split(" ")

        #If the user specifies the station of the shift
        if(len(args) == 4):
            date_asked = datetime.utcfromtimestamp(int(message['created_at'])).strftime('%Y-%m-%d %H:%M:%S')
            shift_id = unique_random_numbers()
            name = message['name']
            station = args[1]
            cover_time = args[2]
            date = args[3]



            worksheet.append_row([date_asked, shift_id, name, date, cover_time, station])
            to_send = name + ", you've requested your shift to be covered at " + station + " from " + cover_time + " on " + str(date) + "\n" + "Accept Number: " + str(shift_id)
            post_params = {'bot_id' : config.bot_id, 'text': to_send}
            requests.post('https://api.groupme.com/v3/bots/post', params = post_params)

        #If the user doesn't specify the station of the shift
        elif (len(args) == 3):
            date_asked = datetime.utcfromtimestamp(int(message['created_at'])).strftime('%Y-%m-%d %H:%M:%S')

            shift_id = unique_random_numbers()
            name = message['name']
            cover_time = args[1]
            date = args[2]


            to_send = name + ", you've requested your shift to be covered from " + cover_time + " on " + date + "\n" + "Accept Number: " + shift_id

            post_params = {'bot_id' : config.bot_id, 'text': to_send}
            requests.post('https://api.groupme.com/v3/bots/post', params = post_params)

            worksheet.append_row([date_asked, shift_id, name, date, cover_time, "None Given"])

        else:
            to_send = "Invalid number of parameters: \n USAGE: /add <station> <cover-time> <date>\n\n If the <station> is unknown:\n USAGE: /add <cover-time> <date>"
            post_params = {'bot_id' : config.bot_id, 'text': to_send}
            requests.post('https://api.groupme.com/v3/bots/post', params = post_params)




def accept_shift_command(message):




    args = message['text'].split(" ")
    print(args)
    if(len(args) >= 2):
        for
        try:
            row_number = worksheet.find(id_num).row
            to_send = "[COVER] " + message['name'] + " wants to cover " + worksheet.cell(row_number, 3).value + " on " + worksheet.cell(row_number, 4).value + " from " + worksheet.cell(row_number, 5).value + "\n" + "Student Managers, please like this message to confirm"
            post_params = {'bot_id' : config.bot_id, 'text': to_send}
            requests.post('https://api.groupme.com/v3/bots/post', params = post_params)

            worksheet.update_cell(row_number,7, message['name'])
        except:
            to_send = "Invalid ID Number! \n Please check the spreadsheet."
            post_params = {'bot_id' : config.bot_id, 'text': to_send}
            requests.post('https://api.groupme.com/v3/bots/post', params = post_params)



    else:
        to_send = "Invalid number of parameters: \n USAGE: /accept <accept-number> <...>"
        post_params = {'bot_id' : config.bot_id, 'text': to_send}
        requests.post('https://api.groupme.com/v3/bots/post', params = post_params)


# Generate unique random numbers so that shifts don't have the same ID number
# Have to check the spreadsheet to see if any numbers that were once not available, available
def unique_random_numbers():
    global random_number_list
    random_number = randint(1,100)
    while random_number in random_number_list:
        random_number = randint(1,100)
    random_number_list.append(random_number)
    print(random_number_list)
    return random_number





#Check for manual deletion in the spreadsheet
def check_for_deletion():
    id_list = worksheet.col_values(1)
    for id in random_number_list:
        if id not in id_list:
            random_number_list.remove(id)


#Delete rows after a certain time period
#Look up Advanced Python Scheduler on Desktop
def delete_rows_after_time():










def main():

    while True:
        response = requests.get(config.groupchat_url, params = request_params)
        if response.status_code == 200:
            response_messages = response.json()['response']['messages']
            for message in response_messages:

                if message['text'] == "/shifts":
                    show_shifts_command()
                    request_params['since_id'] = message['id']
                    break
                if message['text'].startswith("/add"):
                    check_for_deletion()
                    add_shifts_command(message)
                    request_params['since_id'] = message['id']

                    break
                if message['text'].startswith("/accept"):
                    accept_shift_command(message)
                    request_params['since_id'] = message['id']
                    break




        time.sleep(3)

        if response.status_code == 429:
            time.sleep(5)

main()
