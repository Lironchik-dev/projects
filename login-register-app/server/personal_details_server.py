import socket
import select
import os
import json
from colorama import Fore
from chatlib import *


MAX_MSG_SIZE = 1024
SERVER_PORT = 6996
SERVER_IP = '127.0.0.1'
data_file_path = r'data\\users.json'



print("Setting up server...")
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_IP, SERVER_PORT))
server_socket.listen()
print("Server listening for clients...")
client_sockets = []


def get_user_number():
    with open(data_file_path, 'r') as users_json_dict_w:
        users_dict_w = json.load(users_json_dict_w)
    users_keys = users_dict_w.keys()
    users_list = list(users_keys)
    last_user = users_list[-1]
    str_num_of_last_user = last_user[-1]
    finall_num_of_new_user = int(str_num_of_last_user) + 1
    return finall_num_of_new_user


def check_if_the_user_exists():
    with open(data_file_path, 'r') as users_json_list_r:
        users_dict_w = json.load(users_json_list_r)
    list_of_users = []
    for user_r in users_dict_w.values():
        list_of_users.append(user_r['user_name'])
    print(list_of_users)
    if user_name_r in list_of_users:
        print("user name in list")
        return True
    else:
        print("user name not in the list")
        return False


while True:
    ready_to_read, ready_to_write, in_error = select.select([server_socket] +
    client_sockets, [], [])
    for currrent_socket in ready_to_read:
        if currrent_socket is server_socket:
            (client_socket, client_adress) = currrent_socket.accept()
            print(Fore.GREEN + f"New client joined from {client_adress}")
            client_sockets.append(client_socket)
        else:
            try:
                data = currrent_socket.recv(MAX_MSG_SIZE).decode()
                print("data received")
            except:
                client_sockets.remove(currrent_socket)
                print(Fore.GREEN + f"Connection closed with {client_adress}")
                currrent_socket.close()
            try: 
                cmd = parse_message(data)[0]
                msg = parse_message(data)[1]
            except:
                client_sockets.remove(currrent_socket)
                print(Fore.GREEN + f"Connection closed with {client_adress}")
                currrent_socket.close()                
            client_values = PROTOCOL_CLIENT.values()
            client_values_list = list(client_values)
            if cmd == client_values_list[4]:
                print(Fore.GREEN + f"Connection closed with {client_adress}")
                client_sockets.remove(currrent_socket)
                currrent_socket.close()
            elif cmd == client_values_list[3]:
                None
            elif cmd == client_values_list[0]:
                print("user try to login")
                user_name_u, password = split_data(msg)
                with open(data_file_path, 'r') as users_json_dict_u:
                    users_dict_u = json.load(users_json_dict_u)
                login_status = False
                for user_u in users_dict_u.values():
                    if user_u['user_name'] == user_name_u and user_u['password'] == password:
                        login_status = True
                    elif user_u['user_name'] != user_name_u or user_u['password'] != password:
                        None
                if login_status == False:
                    print("ERROR LOGIN")
                    currrent_socket.send(build_message("ERROR", "login_error").encode())
                else:
                    print(Fore.GREEN + f"{client_adress} successful login")
                    currrent_socket.send(build_message("LOGIN_OK", "login its ok").encode())
            elif cmd == client_values_list[1]:
                file_status = False
                user_name_r, password_r = split_data(msg)
                try:
                    with open(data_file_path, 'r') as users_json_list_r:
                        users_dict_w = json.load(users_json_list_r)
                        file_status = True
                except:
                    print("ERROR")
                if file_status == True:
                    if check_if_the_user_exists() == False:
                        user_num = get_user_number()
                        users_dict_w[f"USER_{user_num}"] = {"user_name" : user_name_r, "password" : password_r}
                        with open(data_file_path, 'w') as users_json_dict_write:
                            write_end = json.dump(users_dict_w, users_json_dict_write, indent = 8)
                            print("create new acount")
                        currrent_socket.send(build_message('REGISTER_OK', "register its ok").encode())
                    else:
                        print("error register")
                        currrent_socket.send(build_message("ERROR", "user_name").encode())