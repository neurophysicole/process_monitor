
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

cpu_or_state    = 'cpu' #can check on the state, or the cpe level.. checking cpu for now because it seems more straightforward
py_or_script    = 'script' #can use python or osascript — but python doesn’t seem to be working on Donbot
script_file     = '%s/sendMessage.applescript' %wd

cpu_threshold   = 10 #percent

interval_timing = 60 #seconds

process_monitor_fname   = '%s/process_monitor.txt' %wd #process monitor filename
process_fname           = '%s/processes.txt' %wd #process filename

open(process_monitor_fname, 'w')
time.sleep(.5)
open(process_fname, 'w')
time.sleep(.5)

phone_number    = 5092871811 #work phone number


# ----------------------
# find the process
process_name = input('\nWhat is the name of the process that you would like to monitor?\n\n')

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
    process_id = input('\n\nPlease indicate the number corresponding with the identified processes listed above that you would like to monitor:  ') #id the process
    if not int(process_id):
        print('\nWhat does that even mean? Try again, but this time, input your answer as a number.\n')
    if int(process_id) >= len(potential_processes):
        print('\nImpossible answer. Try again with a smaller number.\n')
    
    id_confirm_loop = True
    
    while id_confirm_loop:
        if int(process_id) < len(potential_processes):
            id_confirm = input( '%s\n\n Is that right? (y/n): ' %( potential_processes[int(process_id)] ) )
            if (id_confirm == 'y') or (id_confirm == ''):
                id_loop = False
                id_confirm_loop = False
            elif id_confirm == 'n':
                print('OK, try again.')
                id_confirm_loop = False
            else:
                print('wtf. Try again.')

process         = potential_processes[int(process_id)].split() #pick selection
pid             = process[0] #get pid
process_name    = process[3:] #get process name

# ----------------------
# begin monitoring

print('\n\n~~ Monitoring in Progress ~~\n\n')
start_date = datetime.today().strftime('%m-%d-%Y')
start_time = datetime.today().strftime('%-H:%M')
print( 'Start Date: %s  -- Start Time: %s' %(start_date, start_time) )

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
                print('\n\nSTUCK STUCK STUCK STUCK STUCK (…THE FOLLOWING MESSAGE MAY BE FALSE…)\n\n')
                monitoring_loop = False
            elif (state_1 == '') and (state_2 == '') and (state_3 == ''):
                monitoring_loop = False
            else:
                process_monitor_file.close()
                print('\nStill processing. . . .')

            state   = []

    else:
        print('\n\nERROR! Threshold determination not valid.\n\n')


# -------------------------------------------
# notify when process is complete
end_date = datetime.today().strftime('%m-%d-%Y')
end_time = datetime.today().strftime('%-H:%M')

notification = str( '\n\n~~ !!!! PROCESS COMPLETE !!! ~~\nEnd Date: %s -- End Time: %s\nStart Day: %s -- Start Time: %s' %(end_date, end_time, start_date, start_time) )

print(notification) #notification

if py_or_script == 'py':
    imessage.send(phone_number, notification) #send text
elif py_or_script == 'script':
    os.system( 'osascript %s %i "%s"' %(script_file, phone_number, notification) )
else:
    print('\n\nERROR! Notification mode not valid.\n\n')

# ----------------------
# close down shop
os.remove(process_fname)
os.remove(process_monitor_fname)

exit()
