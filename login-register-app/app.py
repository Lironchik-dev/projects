#1. build visual app(main_screen, login_screen, register_screen, choose_language_screen...).
#2. creat scripts for example: (give commands to buttons).
#3. creat connection animation with the server. if can't connect to the server show error message. 
#4. do messagebox when the user whant to close the app or another action. 
#5. create the server and the talk to the server(the protocol in the chatlib file).
#6. create buaitiful interface!


from Check_English import *
import threading
import time
from tkinter import *
from chatlib import *
from PIL import Image, ImageTk
from tkinter import messagebox
from socket import *
import os

# Base directory of this file, so image paths work on any computer
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, "images")


SERVER_IP = "127.0.0.1"
SERVER_PORT = 6996
MAX_MSG_SIZE = 1024




tk = Tk() #the app

check = False


h = 400 #hieght of the app/window.
w = 350 #widht of the app/window.

place_h = 850 #the spawn place of the app/window on the screen in hieght.
place_w = 300 #the spawn place of the app/window on the screen in width.

# images
open_eye = Image.open(os.path.join(IMAGES_DIR, "eye.png"))
open_eye = open_eye.resize((40, 30))
tk_open_eye = ImageTk.PhotoImage(open_eye)

close_eye = Image.open(os.path.join(IMAGES_DIR, "hide.png"))
close_eye = close_eye.resize((40, 30))
tk_close_eye = ImageTk.PhotoImage(close_eye)


#app settings
tk.iconbitmap(os.path.join(IMAGES_DIR, "Snake_33920.ico"))
tk.title('LOGI APP')
tk.geometry(f"{h}x{w}+{place_h}+{place_w}")
tk.resizable(False, False)
#tk.maxsize()

def connection_ok():
    global b1, b2
    clear_tk()
    print("connect")
    if status == 'main_screen' or status == 'connection_failed_screen':
        b1 = Button(tk, text="LOGIN", font=('Secular One',25, 'bold'), command=login_screen, activebackground='gray', relief=RAISED, bd=5, height=1, width=6)
        b1.place(x=20, y=140)
        b2 = Button(tk, text="REGISTER", font=('Secular One',25, 'bold'), command=register_screen, activebackground='gray', relief=RAISED, bd=5, height=1, width=8)
        b2.place(x=190, y=140)
    elif status == 'login_screen':
        login_screen()
    elif status == 'register_screen':
        register_screen()





def connection_failed():
    global error_connect_label, try_to_connect_agin_button, status
    print("connect failed")
    clear_tk()
    error_connect_label = Label(tk, text='CONNECTION ERROR\nCheck your internet connection\nor contact support', font=("", 15))
    error_connect_label.place(x=60, y=120)
    try_to_connect_agin_button = Button(tk, text='Try agin', command=try_to_connect, activebackground='gray', font=("MS Reference Sans Serif", 13))
    try_to_connect_agin_button.place(x=155, y=195)
    status = 'connection_failed_screen'


def connection():
    global client_socket, status
    status = 'main_screen'
    client_socket = socket(AF_INET, SOCK_STREAM) #creat socket
    client_socket.connect((SERVER_IP, SERVER_PORT))
    connection_ok()


def try_to_connect():
    try:
        connection()
    except error:
        connection_failed()



def register_toggle_password():
    if register_entry_password.cget('show') == '':
        register_entry_password.config(show='•')
        show_register_password_button.config(image=tk_open_eye)
    else:
        register_entry_password.config(show='')
        show_register_password_button.config(image=tk_close_eye)


def login_toggle_password():
    if entry_password.cget('show') == '':
        entry_password.config(show='•')
        show_login_password_button.config(image=tk_open_eye)
    else:
        entry_password.config(show='')
        show_login_password_button.config(image=tk_close_eye)


def limit_size_user_login(*args): #i found this function in the internet because i dont know how do this but i search information in the internet on each of function or methods and the strange argumen '*args' im realy dont know what is mean but i search in the internet and i think if i dont find answer on my questions i ask the computer teacher.
    value = login_user_name.get()
    if len(value) > 13: login_user_name.set(value[:13])
    if ' ' in value: login_user_name.set(value[:-1])
    if value == '': None
    if not isEnglish(value[-1]) and not value[-1].isnumeric(): login_user_name.set(value[:-1])
    else: None


def limit_size_password_login(*args):
    value = login_password.get()
    if len(value) > 13: login_password.set(value[:13])
    if ' ' in value: login_password.set(value[:-1])
    if value == '': None
    if not isEnglish(value[-1]) and not value[-1].isnumeric(): login_password.set(value[:-1])
    else: None


def limit_size_user_name_register(*args):
    value = register_user_name.get()
    if len(value) > 13: register_user_name.set(value[:13])
    if ' ' in value: register_user_name.set(value[:-1])
    if value == '': None
    if not isEnglish(value[-1]) and not value[-1].isnumeric(): register_user_name.set(value[:-1])
    else: None


def limit_size_password_register(*args):
    value = register_password.get()
    if len(value) > 13: register_password.set(value[:13])
    if ' ' in value: register_password.set(value[:-1])
    if value == '': None
    if not isEnglish(value[-1]) and not value[-1].isnumeric(): register_password.set(value[:-1])
    else: None


def main_screen(): #this function return to the main with 'back_button'.
    global status
    clear_tk()
    b1.place(x=20, y=140)
    b2.place(x=190, y=140)
    status = 'main_screen'


def login():
    print("part1")
    if str(login_user_name.get()) != '' and str(login_password.get()) != '':
        join_login = join_data([str(login_user_name.get()), str(login_password.get())])
        try:
            client_socket.send(build_message("LOGIN", join_login).encode('utf-8'))
            print("try to login")
        except:
            check_connect()
            print("daniel homo")
        print("part 30")
        data = client_socket.recv(MAX_MSG_SIZE).decode()
        print("part 4")
        print(data)
        cmd = parse_message(data)[0]
        msg = parse_message(data)[1]
        server_values = PROTOCOL_SERVER.values()
        server_values_list = list(server_values)
        if cmd == server_values_list[0]:
            print("successful login")
        elif cmd == server_values_list[1]:
            print("login failed")


def register():
    print("register button pressed")
    if str(register_user_name.get()) != '' and str(register_password.get()) != '':
        join_register = join_data([str(register_user_name.get()), str(register_password.get())])
        print("join data")
        try:
            client_socket.send(build_message("REGISTER", join_register).encode('utf-8'))
            print("send register data")
        except:
            check_connect()
            print("Register Erorr")
        data = client_socket.recv(MAX_MSG_SIZE).decode()
        print("data received")
        print(data)
        cmd = parse_message(data)[0]
        msg = parse_message(data)[1]
        server_values = PROTOCOL_SERVER.values()
        server_values_list = list(server_values)
        if cmd == server_values_list[2]:
            print("seccessful register")
        elif cmd == server_values_list[3]:
            print("register failed")


def login_screen(): #this function set login screen and hide the 'b1(login button)' and 'b2(register button)'.
    global user_name_label, entry_user_name, back_button, login_user_name, login_password, entry_password, password_label, show_login_password_button, status
    b1.place_forget()
    b2.place_forget()
    stay_in_system_login = Checkbutton(tk, text="Stay in system", font=('Microsoft YaHei UI',15))
    user_name_label = Label(tk, text='USER NAME', font=('Secular One', 30, 'bold'))
    password_label = Label(tk, text='PASSWORD', font=('Secular one', 30, 'bold'))
    back_button = Button(tk, text='BACK', font=('MS Reference Sans Serif',10,'bold'), command=main_screen, activebackground='gray')
    login_button = Button(tk, text='LOGIN', font=('Secular one', 18, 'bold'), activebackground='gray', relief=RAISED, width=7, command=login)
    back_button.place(x=0, y=0)
    login_user_name = StringVar() #i dont know
    login_user_name.trace('w', limit_size_user_login) #i dont know 
    entry_user_name = Entry(tk, font=('Microsoft YaHei UI',20), textvariable=login_user_name, width=16)
    login_password = StringVar()
    entry_password = Entry(tk, font=('Microsoft YaHei UI',20), textvariable=login_password, width=11, show='•')
    show_login_password_button = Button(tk, image=tk_open_eye, command=login_toggle_password)
    login_password.trace('w', limit_size_password_login)
    show_login_password_button.place(x=50, y=201)
    stay_in_system_login.place(x=110, y=240)
    login_button.place(x=130, y=280)
    user_name_label.place(x=80, y=60)
    password_label.place(x=82, y=150)
    entry_user_name.place(x=68, y=110)
    entry_password.place(x=105, y=200)
    status = 'login_screen'


def register_screen(): #this function set register screen and hide the 'b1(login button)' and 'b2(register button)'.
    global back_button, creat_user_name_label, register_user_name, register_entry_user_name, creat_passwords_label, register_password, register_entry_password, show_register_password_button, status
    b2.place_forget()
    b1.place_forget()
    back_button = Button(tk, text='BACK', font=('MS Reference Sans Serif',10,'bold'), command=main_screen, activebackground='gray')
    register_button = Button(tk, text='REGISTER', font=('Secular one', 18, 'bold'), command=register, activebackground='gray')
    back_button.place(x=0, y=0)
    creat_user_name_label = Label(tk, text='Create a user name', font=('Microsoft YaHei UI',20,'bold'))
    creat_passwords_label = Label(tk, text='Create a password', font=('Microsoft YaHei UI', 20, 'bold'))
    register_user_name = StringVar()
    register_user_name.trace('w', limit_size_user_name_register)
    register_entry_user_name = Entry(tk, font=('Microsoft YaHei UI',20), textvariable=register_user_name, width=16)
    register_password = StringVar()
    register_password.trace('w', limit_size_password_register)
    register_entry_password = Entry(tk, font=('Microsoft YaHei UI',20), textvariable=register_password, width=11, show='•')
    show_register_password_button = Button(tk, image=tk_open_eye, command=register_toggle_password)
    show_register_password_button.place(x=55, y=222)
    register_entry_user_name.place(x=72, y=120)
    creat_user_name_label.place(x=75, y=72)
    creat_passwords_label.place(x=80, y=170)
    register_entry_password.place(x=110, y=220)
    register_button.place(x=130, y=280)
    status = 'register_screen'


def clear_tk():
    for widget in tk.winfo_children():
        try:
           widget.place_forget()
        except:
            widget.grid_forget()



def check_connect():
    try:
        client_socket.send(build_message("CHECK_CONNECTION", '(Check connection message)').encode())
        try:
            print("send check connection msg")
        except:
            None
    except:
        print("create socket")
        try_to_connect()




def ask_exit():
    global loop
    result_of_ask_exit = messagebox.askyesno('Exit','Are you sure you want to exit?')
    if result_of_ask_exit:
        try:
            client_socket.send(build_message("DISCONNECT", 'bye').encode())
            client_socket.close()
        except:
            None
        finally:
            tk.destroy()
            loop = False
tk.protocol('WM_DELETE_WINDOW', ask_exit)

#try to connect to the server
try_to_connect()


def background_loop_of_connection():
    global loop
    loop = True
    num = 1
    while loop: 
        check_connect()
        print("loop", num)
        num += 1
        if loop is False:
            break
        time.sleep(5)
        


b = threading.Thread(name='background_loop_of_connection', target=background_loop_of_connection)

b.start()

# loop of the app
tk.mainloop()