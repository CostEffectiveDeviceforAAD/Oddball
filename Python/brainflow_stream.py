
import argparse
import time
import numpy as np
import mne
from mne.channels import read_layout
import brainflow
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import logging
import random
import serial
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds, BrainFlowError
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations, WindowFunctions, DetrendOperations





port = serial.Serial("COM8", 9600)
###############################################################

BoardShim.enable_dev_board_logger()

parser = argparse.ArgumentParser()
# use docs to check which parameters are required for specific board, e.g. for Cyton - set serial port
parser.add_argument('--timeout', type=int, help='timeout for device discovery or connection', required=False,
                    default=0)
parser.add_argument('--ip-port', type=int, help='ip port', required=False, default=0)
parser.add_argument('--ip-protocol', type=int, help='ip protocol, check IpProtocolType enum', required=False,
                    default=0)
parser.add_argument('--ip-address', type=str, help='ip address', required=False, default='')
parser.add_argument('--serial-port', type=str, help='serial port', required=False, default='COM7')
parser.add_argument('--mac-address', type=str, help='mac address', required=False, default='')
parser.add_argument('--other-info', type=str, help='other info', required=False, default='')
parser.add_argument('--streamer-params', type=str, help='streamer params', required=False, default='')
parser.add_argument('--serial-number', type=str, help='serial number', required=False, default='')
parser.add_argument('--board-id', type=int, help='board id, check docs to get a list of supported boards',
                    required=False, default='2')
parser.add_argument('--file', type=str, help='file', required=False, default='')
args = parser.parse_args()

params = BrainFlowInputParams()
BoardShim.enable_dev_board_logger()
params.ip_port = args.ip_port
params.serial_port = args.serial_port
params.mac_address = args.mac_address
params.other_info = args.other_info
params.serial_number = args.serial_number
params.ip_address = args.ip_address
params.ip_protocol = args.ip_protocol
params.timeout = args.timeout
params.file = args.file

board = BoardShim(args.board_id, params)
board.prepare_session()

# board.start_stream () # use this for default options
board.start_stream(45000, args.streamer_params)
time.sleep(10)
#data = board.get_current_board_data (125) # get latest 256 packages or less, doesnt remove them from internal buffer
input = board.get_board_data()  # get all data and remove it from internal buffer
# board.stop_stream()
#board.release_session()

#######################################



eeg_channels = board.get_eeg_channels(args.board_id)
aux_channels = board.get_analog_channels(args.board_id)

ti=[]
eeg = np.zeros((16,1))
aux = np.zeros((3,1))
eeg_data = np.array([])
temp=[]
w = 1
num = 1

print("start")
port.write(b'1')

while num < 2:  # + zeros

    ## new trial

    #input = board.get_board_data()
    #input = board.get_board_data()
    input = board.get_board_data()

    eeg_data = input[eeg_channels, :]
    aux_data = input[aux_channels, :]
    eeg = np.concatenate((eeg, eeg_data), axis=1)
    aux = np.concatenate((aux, aux_data), axis=1)
    print(aux_data)

    # detect sound
    if 1 in aux_data[1,:]:
        print("speech")
        print(aux_data)
        num = num+1

        #여기서의 첫 0.5 의 index를 찾아야해
        index = np.where(aux[1,:]==1)     # Onset 지점!
        onset = index[0][0]

        # onset 부터 3*125 구간이 되면 자르기시작.

        while len(eeg.T) < (onset + 125*3 + 125*10):       #한 trial while

            # receive data
            input = board.get_board_data()
            eeg_data = input[eeg_channels, :]
            aux_data = input[aux_channels, :]                 # 11,12,13 / 0 or 1
            eeg_record = np.concatenate((eeg_record, eeg_data), axis=1)     # channel by time
            aux_record = np.concatenate((aux_record, aux_data), axis=1)

            print("data" + str(len(eeg.T)))

            # beep 끝나고 난후 1초 후 부터 1초 넘을때마다 1초씩 자르기

            if len(eeg.T) > (onset + 125*3 + 125*(w)):

                # beep 후 data를 1초 단위 자르기.
                win = aux[:, onset + 125*3 + 125*(w-1) : onset + 125*3 + 125*(w)]

                print("1s")

                temp.append(win)

                ## 막 프로세싱
                time.sleep(0.5)    # 임의로 걸리는 시간을 잡음.
                w = w+1



board.stop_stream()
board.release_session()
port.close()

print("a")
