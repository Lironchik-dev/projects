# Protocol Constants

CMD_FIELD_LENGTH = 16	# Exact length of cmd field (in bytes)
LENGTH_FIELD_LENGTH = 4   # Exact length of length field (in bytes)
MAX_DATA_LENGTH = 10**LENGTH_FIELD_LENGTH-1  # Max size of data field according to protocol
MSG_HEADER_LENGTH = CMD_FIELD_LENGTH + 1 + LENGTH_FIELD_LENGTH + 1  # Exact size of header (CMD+LENGTH fields)
MAX_MSG_LENGTH = MSG_HEADER_LENGTH + MAX_DATA_LENGTH  # Max size of total message
DELIMITER = "|"  # Delimiter character in protocol

# Protocol Messages 
# In this dictionary we will have all the client and server command names

PROTOCOL_CLIENT = {
"login_msg" : "LOGIN",
"register_msg" : "REGISTER",
"logout_msg" : "LOGOUT",
"check_connection_msg" : "CHECK_CONNECTION",
"disconnect_msg" : "DISCONNECT"
} # .. Add more commands if needed


PROTOCOL_SERVER = {
"login_ok_msg" : "LOGIN_OK",
"login_failed_msg" : "ERROR",
"register_ok_msg" : "REGISTER_OK",
"register_failed_msg" : "ERROR"
} # ..  Add more commands if needed


# Other constants

ERROR_RETURN = None  # What is returned in case of an error


def build_message(cmd, data):
    full_msg = ''
    for client_protocol_value in PROTOCOL_CLIENT.values():
        if cmd == client_protocol_value:
            len_cmd_space = 16 - len(cmd)
            cmd_space = len_cmd_space * ' '
            full_msg += cmd
            full_msg += cmd_space
            full_msg += DELIMITER
            if len(data) <= 9999:
                data_len = len(data)
                data_len = str(data_len).zfill(4)
                full_msg += data_len
                full_msg += DELIMITER
                full_msg += data
                return full_msg
            else:
                return ERROR_RETURN
        else:
            for server_protocol_value in PROTOCOL_SERVER.values():
                if cmd == server_protocol_value:
                    len_cmd_space = 16 - len(cmd)
                    cmd_space = len_cmd_space * ' '
                    full_msg += cmd
                    full_msg += cmd_space
                    full_msg += DELIMITER
                    if len(data) <= 9999:
                        data_len = len(data)
                        data_len = str(data_len).zfill(4)
                        full_msg += data_len
                        full_msg += DELIMITER
                        full_msg += data
                        return full_msg
                    else:
                        return ERROR_RETURN


def parse_message(data):
    if data.count(DELIMITER) == 2:
        split_data = data.split(DELIMITER)
        if len(split_data[0]) == 16 and len(split_data[1]) == 4:
            cmd = split_data[0].replace(' ', '')
            msg = split_data[2]
            return cmd, msg
        else:
            return ERROR_RETURN
    else:
        return ERROR_RETURN


def split_data(msg):
    if 'Ж' in msg:
        msg_split = msg.split('Ж')
        return msg_split
    else:
        return ERROR_RETURN


def join_data(msgs):
    join_data = 'Ж'.join(msgs)
    return join_data