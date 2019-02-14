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

random_number_set = set()


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

    if(len(args) == 2):
        id_num = args[1]
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
        to_send = "Invalid number of parameters: \n USAGE: /accept <accept-number>"
        post_params = {'bot_id' : config.bot_id, 'text': to_send}
        requests.post('https://api.groupme.com/v3/bots/post', params = post_params)


# Generate unique random numbers so that shifts don't have the same ID number
def unique_random_numbers():
    random_number = randint(1,100)
    while random_number in random_number_set:
        random_number = randint(1,100)
    return random_number


# Delete shifts automatically from the spreadsheet after a certain amount of time








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
                    add_shifts_command(message)
                    request_params['since_id'] = message['id']
                    break
                if message['text'].startswith("/accept"):
                    accept_shift_command(message)
                    request_params['since_id'] = message['id']
                    break




        time.sleep(3)

main()
