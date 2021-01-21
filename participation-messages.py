# To run this in your terminal, type:
# python participation-messages.py [CSV_FILENAME]

import csv, sys, json, requests, config
from canvasapi import Canvas
from operator import itemgetter
from tests import is_file, test_class_data

#-----------------------------------------------------------------------------------#
# VARIABLES
#-----------------------------------------------------------------------------------#

# Canvas API
canvas = Canvas(config.API_URL, config.API_KEY)
users = canvas.get_course(config.COURSE).get_users(enrollment_type=['student'])

# CSV data
filename = is_file(sys.argv[-1])
class_data = []
categories = []

#-----------------------------------------------------------------------------------#
# HELPER FUNCTIONS
#-----------------------------------------------------------------------------------#

# Format point category names
def create_categories(category_list):
    new_categories = []
    for category in category_list:
        if (category.endswith(' (1)')):
            category = category.strip(' (1)')
        if (category == 'Participation'):
            category = 'Participation (chat, microphone, or small group)'
        new_categories.append(category)
    return new_categories

# Data wrangling specific to my ClassDojo csv data
def format_row(row):
    del row[1:7]
    del row[-3:]
    del row[-3:-1]
    return row

# Read CSV file into class_data
def create_class_data():
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        try:
            for row in reader:
                global class_data
                class_data.append(format_row(row)) 
        except csv.Error as ex:
            sys.exit('Exiting: Unable to read csv file {} at line {}: {}'.format(filename, reader.line_num, ex))
        else:
            global categories
            categories = create_categories(class_data[0])
            del class_data[0]
            class_data = sorted(class_data, key = itemgetter(0)) # Sort students alphabetically

def message_intro(first_name, point_total):
    return 'Hi ' + first_name + ',\n\nThis week you earned a total of ' + point_total + ' in-class participation point(s). '

def message_categories(student_data, data_length):
    m = 'Here are the categories you earned points for: \n\n'
    for i in range(data_length):
        if i == 0 or i == data_length - 1:
            continue
        if student_data[i] != '':
            m += categories[i]
            m += ": "
            m += student_data[i]
            m += '\n\n'
    m += 'You can use this data to help you write your participation reflection for this week.\n\n'
    return m

def message_no_participation():
    m = '\n\nPlease reach out to me if you need help feeling comfortable participating in class. You bring a valuable perspective to our learning community and participation is important for your own learning.\n\n'
    m += 'On the participation reflection homework for this week, please write a participation goal that you would like to work on for next week.\n\n'
    return m

# Create a new Canvas message for a specific user
def create_message(index):
    student_data = class_data[index]
    first_name = student_data[0].split(' ')[0]
    data_length = len(student_data)
    point_total = student_data[data_length - 1]

    # Build out Canvas message
    message = message_intro(first_name, point_total)
    if (int(point_total) > 0):
        message += message_categories(student_data, data_length)

        if (int(point_total) > 4):
            message += 'Keep up the great work!\n\n'

    else: # If students did not participate
        message += message_no_participation()
    
    message += '- Ms.Yupa\n'
    return message

# Send a Canvas message to a specific user
def send_message(user, student_index):
    message_body = create_message(student_index)
    canvas.create_conversation(
        recipients = [user.id],
        subject = 'Weekly Participation Report',
        force_new = True,
        body = message_body,
        context_code = config.COURSE_CONTEXT_CODE
    )

# Send a message to every student
def send_all_messages():
    student_index = 0
    for user in users:
        try:
            send_message(user, student_index)
            student_index += 1
        except:
            print('There was an user sending a message for this student at index {}.'.format(student_index))
            pass

def print_all_messages():
    student_index = 0
    for user in users:
        print(user.name + ':\n\n' + create_message(student_index))
        student_index += 1
        print('------------------------------------------------------------------\n\n')

#-----------------------------------------------------------------------------------#
# MAIN
#-----------------------------------------------------------------------------------#

def main():
    create_class_data()
    print_all_messages() 
    key = input('Does this look correct? (y/n): ').lower()
    valid_inputs = ['y', 'yes', 'n', 'no']
    if not (key in valid_inputs):
        sys.exit('User input invalid, try again.\n')
    elif key == 'y' or key == 'yes':
        send_all_messages()
        print('\n\nAll messages sent successfully.\n\n')
    else:
        sys.exit('\n\nExiting without sending messages.\n\n')
        

if __name__ == "__main__":
    main()