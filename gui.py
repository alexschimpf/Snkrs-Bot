import PySimpleGUI as sg
import main
import sys
import subprocess

sg.theme('DarkAmber')    

layout = [[sg.Text('Enter Nike Account information')],
    [sg.Text('Username', size=(15, 1) ), sg.InputText(key='-user-')],
    [sg.Text('Password', size=(15, 1) ), sg.InputText(key='-pass2-')],
    [sg.Text('URL', size=(15, 1)), sg.InputText(key='-url-')],
    [sg.Text('Size', size=(15, 1)), sg.InputText(key='-size-')],
    [sg.Submit('Submit'), sg.Cancel()]]      

window = sg.Window('Slippery', layout)

event, values = window.Read()

user = values['-user-']
pass2 = values['-pass2-']
url = values['-url-']
size = values['-size-']

runcommand = 'python main.py --username {} --password {} --url {} --shoe-size {} --driver-type chrome --num-retries 3'.format(user, pass2, url, size)

if event == 'Submit':
    subprocess.call(runcommand)
try:
    check = subprocess.check_output(runcommand)
    
except subprocess.CalledProcessError as e:
            check = e.output
while True:                             # The Event Loop
    event, values = window.read() 
    print(event, values)       
    if event == sg.WIN_CLOSED or event == 'Exit':
        break      


print(check)