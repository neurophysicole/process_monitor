
# monitor computer for specific program


# ----------------------
# import packages
import os
import pandas as pd
from tabulate import tabulate
from py_imessage import imessage
import time
from datetime import datetime


# ----------
# init vars
wd              = os.path.dirname(os.path.abspath('%s' %__file__))

py_or_script    = 'script' #can use python or osascript — but python doesn’t seem to be working on Donbot
script_file     = '%s/sendMessage.applescript' %wd  

interval_timing = 60 #seconds

phone_number    = 5092871811 #work phone number


# -----------------
# find the process
process_loop = True
while process_loop:
    process_name = input('\nWhat is the name of the process that you would like to monitor?\n\n')

    process_monitor_fname   = '%s/%s_monitor.txt' %(wd, process_name) #process monitor filename
    process_fname           = '%s/%s_processes.txt' %(wd, process_name) #process filename

    open(process_monitor_fname, 'w')
    time.sleep(.5)
    open(process_fname, 'w')
    time.sleep(.5)

    os.system( 'ps -ax | grep %s >> %s' %(process_name, process_fname) ) #save the processes

    # list the processes
    process_file    = open(process_fname, 'r') #open file
    all_processes   = process_file.readlines() #read file

    # get the processes
    potential_processes = []
    for line in range( 0, len(all_processes) ):
        this_line   = all_processes[line]
        if process_name in this_line:
            potential_processes.append(this_line)

    processes_df = pd.DataFrame( {'Processes': potential_processes} ) #list processes in a dataframe
    processes_df = str( tabulate(processes_df, headers = 'keys', tablefmt = 'psql', showindex = True) )
    os.system('echo \'%s\'' %processes_df) #print dataframe

    id_loop = True
    while id_loop:
        process_id = input('\n\nPlease indicate the number corresponding with the identified processes listed above that you would like to monitor (if none, type \'z\'):  ') #id the process
        if str(process_id) == 'z':
            print('\n\nOops, OK.\n')
            os.remove(process_monitor_fname)
            os.remove(process_fname)
            id_loop = False
        elif ( not int(process_id) ) and (process_id == 0):
                print('\n\nERROR: Please try again.')
        else:
            if int(process_id) >= len(potential_processes):
                print('\nImpossible answer. Try again with a smaller number.\n')
            elif int(process_id) < len(potential_processes):
                id_confirm_loop = True
                while id_confirm_loop:
                    if int(process_id) < len(potential_processes):
                        id_confirm = input( '%s\n\n Is that right? (y/n): ' %( potential_processes[int(process_id)] ) )
                        if (id_confirm == 'y') or (id_confirm == ''):
                            process_loop = False
                            id_loop = False
                            id_confirm_loop = False
                        elif id_confirm == 'n':
                            print('OK, try again.')
                            id_confirm_loop = False
                        else:
                            print('wtf. Try again.')
            else:
                print('\n\nERRROR: Please try again.\n')
    
process         = potential_processes[int(process_id)].split() #pick selection
pid             = process[0] #get pid
process_name    = process[3:] #get process name


# ------------------
# settings interview
print('\n\nSETTINGS CHECK-IN\n')

threshold_choices = ['cpu', 'state']
threshold_loop = True
while threshold_loop:
    cpu_or_state    = input('\n\Type the number corresponding to the processing state you would like to monitor for thresholding:\n\n1- cpu\n2- state\n\n:  ') #can check on the state, or the cpu level..
    if (int(cpu_or_state) > 2) or (int(cpu_or_state) < 1):
        print('\n\nImpossible selection. Please try again.\n')
    elif (int(cpu_or_state) == 1) or (int(cpu_or_state) == 2):
        threshold_confirm_loop = True
        while threshold_confirm_loop:
            threshold_confirm = input('\n\n%s, right? (y/n):  ' %threshold_choices[(int(cpu_or_state) - 1)])
            if (threshold_confirm == 'y') or (threshold_confirm == ''):
                cpu_or_state = threshold_choices[(int(cpu_or_state) - 1)]
                threshold_loop = False
                threshold_confirm_loop = False
            elif threshold_confirm == 'n':
                print('\n\nOK, try again.\n')
                threshold_confirm_loop = False
            else:
                print('\n\nERROR: Response not valid. Please try again.\n')
    else:
        print('\n\ERROR: Please try again.\n')

if cpu_or_state == 'cpu':
    manual_threshold_loop = True
    while manual_threshold_loop:
        manual_threhsold = input('\n\nThreshold = 10\%, do you want to change it? (y/n):  ')
        if (manual_threshold == 'y') or (manual_threshold == ''):
            change_threshold_loop = True
            while change_threshold_loop:
                change_threshold = input('\n\nSet the new cpu \% threshold:  ')
                if int(change_threshold):
                    confirm_threshold_loop = True
                    while confirm_threshold_loop:
                        confirm_threshold = input('\n\nSet threshold to %s\%? (y/n):  ')
                        if (confirm_threhsold == 'y') or (confirm_threshold == ''):
                            print('\nAs you wish.\n')
                            cpu_threshold = int(change_threshold)
                            manual_threshold_loop = False
                            change_threshold_loop = False
                            confirm_threshold_loop = False
                        elif confirm_threshold == 'n':
                            print('\nAlright, try again.\n')
                            confirm_threshold_loop = False
                        else:
                            print('\n\nwtf? Try again.\n')
                else:
                    print('\n\nERROR: Something went wrong. Please try again.\n')
        elif manual_threshold == 'n':
            print('\n\nCool cool cool cool cool.. We\'ll keep it at 10\% then.\n')
            cpu_threshold   = 10 #percent
        else:
            print('\n\nwtf? Please try again.\n')


# ----------------
# begin monitoring
print('\n\n~~ Monitoring in Progress ~~\n\n')
start_date = datetime.today().strftime('%m-%d-%Y')
start_time = datetime.today().strftime('%-H:%M')
print( 'Start Date: %s  -- Start Time: %s' %(start_date, start_time) )

# initial notification
notification_start = str( '\n\nMonitoring Process:\n%s\n\nStart Day: %s -- Start Time: %s' %(process_name, start_date, start_time) )

if py_or_script == 'py':
    imessage.send(phone_number, notification) #send text
elif py_or_script == 'script':
    os.system( 'osascript %s %i "%s"' %(script_file, phone_number, notification_start) )
else:
    print('\n\nERROR! Notification mode not valid.\n\n')


monitoring_loop = True
while monitoring_loop:
    os.system( str( 'top -l 5 -o cpu -n 10 -s %s >> %s' %(interval_timing, process_monitor_fname) ) ) #save the activity
    process_monitor_file = open(process_monitor_fname, 'r')
    process_monitor_file_contents = process_monitor_file.readlines()

    cpu     = []
    cpu_1   = 0
    cpu_2   = 0
    cpu_3   = 0

    state   = []
    state_1 = ''
    state_2 = ''
    state_3 = ''


    for line in range( 0, len(process_monitor_file_contents) ):
        line_list = process_monitor_file_contents[line].split()
        if pid in line_list:
            cpu.append( line_list[2] )
            state.append( line_list[12] )

    if cpu_or_state == 'cpu':

        if len(cpu) >= 5:
            cpu_3   = cpu[-1]
            cpu_2   = cpu[-2]
            cpu_1   = cpu[-3]

            if ( float(cpu_1) < cpu_threshold ) and ( float(cpu_2) < cpu_threshold ) and ( float(cpu_3) < cpu_threshold ):
                monitoring_loop = False
            elif (cpu_1 == 0) and (cpu_2 == 0) and (cpu_3 == 0):
                monitoring_loop = False
            else:
                process_monitor_file.close()
                print('\nStill processing. . . .')
    
            cpu     = []

    elif cpu_or_state == 'state':

        if len(state) >= 5:
            state_3     = state[-1]
            state_2     = state[-2]
            state_1     = state[-3]

            if (state_1 == 'sleeping') and (state_2 == 'sleeping') and (state_3 == 'sleeping'):
                monitoring_loop = False
            elif (state_1 == 'stuck') and (state_2 == 'stuck') and (state_3 == 'stuck'):
                print('\n\nSTUCK STUCK STUCK STUCK STUCK\n\n')
            elif (state_1 == '') and (state_2 == '') and (state_3 == ''):
                monitoring_loop = False
            else:
                process_monitor_file.close()
                print('\nStill processing. . . .')

            state   = []

    else:
        print('\n\nERROR! Threshold determination not valid.\n\n')


# -------------------------------
# notify when process is complete
end_date = datetime.today().strftime('%m-%d-%Y')
end_time = datetime.today().strftime('%-H:%M')

notification_complete = str( '\n\n~~ !!!! PROCESS COMPLETE !!! ~~\nEnd Date: %s -- End Time: %s' %(end_date, end_time) )

print(notification_complete) #notification

if py_or_script == 'py':
    imessage.send(phone_number, notification_complete) #send text
elif py_or_script == 'script':
    os.system( 'osascript %s %i "%s"' %(script_file, phone_number, notification_complete) )
else:
    print('\n\nERROR! Notification mode not valid.\n\n')


# ---------------
# close down shop
os.remove(process_fname)
os.remove(process_monitor_fname)

exit()
