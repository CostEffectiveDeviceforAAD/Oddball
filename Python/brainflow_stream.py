
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
from datetime import datetime
from psychopy import visual, core, event, data





port = serial.Serial("COM10", 9600)
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
parser.add_argument('--serial-port', type=str, help='serial port', required=False, default='COM15')
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

print("start")
port.write(b'1')
# Import Current Date & Time
date_time = data.getDateStr()
block = 1
# Open Text file to record
with open(date_time + '.txt', 'w') as f:
    sttime = datetime.now().strftime('%H:%M:%S - ')
    f.write("START "+ sttime + "\n")
    f.write("block = "+str(block)+"\n\n")


Board_data = board.get_board_data()
while len(eeg.T) < 125*5:  # + zeros

    #time.sleep(1)
    input = board.get_board_data()

    #input = board.get_board_data()
    eeg_data = input[eeg_channels, :]
    aux_data = input[aux_channels, :]   # 11,12,13 / 0 or 1

    if eeg_data.size > 0 :

        eeg = np.concatenate((eeg, eeg_data), axis=1)
        aux = np.concatenate((aux, aux_data), axis=1)
        print(len(eeg.T))
        #print(aux_data)
        #time.sleep(1)

        # Record Data to a Text file in real-time
        sample_e = "".join([str(eeg_data.T)])
        sample_a = "".join([str(aux_data)])
        with open(date_time + '.txt', 'a+') as f:
            sttime = datetime.now().strftime('%Y%m%d_%H:%M:%S - ')
            f.write(str(len(eeg.T))+" : {0}  ".format(sample_e))
            f.write("  {0}".format(sample_a))
            f.write(sttime + "\n")
        time.sleep(1)

board.stop_stream()
board.release_session()
port.close()

print("a")
