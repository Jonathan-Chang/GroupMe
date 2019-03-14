import requests
import time

import datetime
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
unique_id_bottom = 1
unique_id_top = 1000


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
            date_asked = datetime.datetime.utcfromtimestamp(int(message['created_at'])).strftime('%Y-%m-%d %H:%M:%S')
            shift_id = unique_random_numbers()
            name = message['name']
            station = args[1]
            cover_time = args[2]
            #date = args[3]
            try:
                date = args[3]
                month_of_date = int(date.split('/')[0])
                day_of_date = int(date.split('/')[1])
                year_of_date = datetime.date.today().year
                datetime.date(year_of_date, month_of_date, day_of_date)
                worksheet.append_row([date_asked, shift_id, name, date, cover_time, station])
                to_send = name + ", you've requested your shift to be covered at " + station + " from " + cover_time + " on " + str(date) + "\n" + "Accept Number: " + str(shift_id)
                post_params = {'bot_id' : config.bot_id, 'text': to_send}
                requests.post('https://api.groupme.com/v3/bots/post', params = post_params)
            except ValueError:

                to_send = "Invalid date!"
                post_params = {'bot_id' : config.bot_id, 'text': to_send}
                requests.post('https://api.groupme.com/v3/bots/post', params = post_params)





        #If the user doesn't specify the station of the shift
        elif (len(args) == 3):
            date_asked = datetime.datetime.utcfromtimestamp(int(message['created_at'])).strftime('%Y-%m-%d %H:%M:%S')

            shift_id = unique_random_numbers()
            name = message['name']
            cover_time = args[1]
            #date = args[2]

            try:
                date = args[2]
                month_of_date = int(date.split('/')[0])
                day_of_date = int(date.split('/')[1])
                year_of_date = datetime.date.today().year
                datetime.date(year_of_date, month_of_date, day_of_date)

                to_send = name + ", you've requested your shift to be covered from " + cover_time + " on " + date + "\n" + "Accept Number: " + str(shift_id)
                post_params = {'bot_id' : config.bot_id, 'text': to_send}
                requests.post('https://api.groupme.com/v3/bots/post', params = post_params)
                worksheet.append_row([date_asked, shift_id, name, date, cover_time, "None Given"])
            except ValueError:
                to_send = "Invalid date!"
                post_params = {'bot_id' : config.bot_id, 'text': to_send}
                requests.post('https://api.groupme.com/v3/bots/post', params = post_params)


        else:
            to_send = "Invalid number of parameters: \n USAGE: /add <station> <cover-time> <date>\n\n If the <station> is unknown:\n USAGE: /add <cover-time> <date>"
            post_params = {'bot_id' : config.bot_id, 'text': to_send}
            requests.post('https://api.groupme.com/v3/bots/post', params = post_params)




def accept_shift_command(message):
    args = message['text'].split(" ")
    args.pop(0)

    for accept_num in args:
        if(accept_num.isdigit()):
            try:
                row_number = worksheet.find(accept_num).row
                if(worksheet.cell(row_number, 7).value == ''):
                #print(type(worksheet.acell('G7').value))
                    to_send = "[COVER] " + message['name'] + " wants to cover " + worksheet.cell(row_number, 3).value + " on " + worksheet.cell(row_number, 4).value + " from " + worksheet.cell(row_number, 5).value + "\n" + "Student Managers, please like this message to confirm"
                    post_params = {'bot_id' : config.bot_id, 'text': to_send}
                    requests.post('https://api.groupme.com/v3/bots/post', params = post_params)
                    worksheet.update_cell(row_number,7, message['name'])
                else:
                    to_send = "Sorry, shift with ID " + accept_num + " has already been taken."
                    post_params = {'bot_id' : config.bot_id, 'text': to_send}
                    requests.post('https://api.groupme.com/v3/bots/post', params = post_params)


            except:
                to_send = "Invalid ID Number! \n Please check the spreadsheet."
                post_params = {'bot_id' : config.bot_id, 'text': to_send}
                requests.post('https://api.groupme.com/v3/bots/post', params = post_params)

        else:
            to_send = "Invalid parameters: \n USAGE: /accept <accept-number> <...>"
            post_params = {'bot_id' : config.bot_id, 'text': to_send}
            requests.post('https://api.groupme.com/v3/bots/post', params = post_params)


# Generate unique random numbers so that shifts don't have the same ID number
# Have to check the spreadsheet to see if any numbers that were once not available, available
def unique_random_numbers():
    count = 0
    global random_number_list
    global unique_id_top
    global unique_id_bottom

    random_number = randint(unique_id_bottom, unique_id_top)
    while random_number in random_number_list:
        random_number = randint(unique_id_bottom, unique_id_top)
        # If for some reason we keep getting already used random numbers, we want to increment
        # the range so that we can get a new unique number
        if(count == 10):
            unique_id_top += 5
            random_number = randint(unique_id_bottom, unique_id_top)
            count = 0
        count += 1


    random_number_list.append(random_number)
    return random_number


#Check for manual deletion in the spreadsheet
def check_for_deletion():
    global random_number_list
    # Gets all the IDs from the spreadsheet
    id_list = worksheet.col_values(2)

    #If the IDs in the random_number_list is not in the updated spreadsheet ID, that means it has been
    #deleted, thus we need to remove it off the list so the unique id can be used again
    for id in random_number_list:
        if str(id) not in id_list:
            random_number_list.remove(id)

def main():

    while True:
        response = requests.get(config.groupchat_url, params = request_params)
        if response.status_code == 200:
            response_messages = response.json()['response']['messages']
            print(response_messages)
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
