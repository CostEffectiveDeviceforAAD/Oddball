""""""""""""""""""""""""""""""""""""""""""
 #        OpenBCI - Python LSL           #
 #           For Online AAD              #
""""""""""""""""""""""""""""""""""""""""""

###### Imports #####
import librosa, warnings, random, time, sys, serial, pickle, scipy.io, brainflow, logging, mne, argparse
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pylsl import StreamInlet, resolve_stream, StreamInfo
#from OpenBCI_lsl import *
from scipy import signal
from scipy.signal import butter, lfilter, resample, filtfilt
#from helper import *
#from pymtrf import *
from psychopy import visual, core, event, data
from psychopy.tools.filetools import fromFile, toFile
#from preprocessing_ha import *
import msvcrt as m
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds, BrainFlowError
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations, WindowFunctions, DetrendOperations
from mne.channels import read_layout



#----------------------------- Connect to port of arduino ------------------------------#

port = serial.Serial("COM10", 9600)   ## ksit laptop : com8 / my laptop : com10

#-------------------------------- Open BrainFlow Board network -------------------------------------#


BoardShim.enable_dev_board_logger()

parser = argparse.ArgumentParser()
# use docs to check which parameters are required for specific board, e.g. for Cyton - set serial port
parser.add_argument('--timeout', type=int, help='timeout for device discovery or connection', required=False,
                    default=0)
parser.add_argument('--ip-port', type=int, help='ip port', required=False, default=0)
parser.add_argument('--ip-protocol', type=int, help='ip protocol, check IpProtocolType enum', required=False,
                    default=0)
parser.add_argument('--ip-address', type=str, help='ip address', required=False, default='')
parser.add_argument('--serial-port', type=str, help='serial port', required=False, default='COM15')        #kist = com7 // hy = com15
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
Board_data = board.get_board_data()  # get all data and remove it from internal buffer

# Channel index
eeg_channels = board.get_eeg_channels(args.board_id)
aux_channels = board.get_analog_channels(args.board_id)


#-------------------------------- Parameter Setting -----------------------------------#

# Set int
tr = 0
a = 0
b = 0
eeg = np.zeros((16,1))
aux = np.zeros((3,1))
EEG_Record = []
AUX_Record = []
path = 'C:/Users/user/Desktop/hy-kist/OpenBCI/save_data/'


# kist path : 'C:/Users/LeeJiWon/Desktop/Oddball Task/save_data/'
# hy path : 'C:/Users/user/Desktop/hy-kist/OpenBCI/save_data/'


#================================ Define Windows =====================================#

# Make window
screen = visual.Window([1024, 768],
    screen = 0,
    pos = [600,0],
    fullscr = True,
    winType = 'pyglet',
    allowGUI = False,
    allowStencil = False,
    monitor ='testMonitor',
    color = [-1,-1,-1],
    blendMode = 'avg',
    units = 'pix',
    )

# Customize windows
def window_1(a, b, c, size1, size2, size3):
    text = visual.TextStim(screen, text= a,
                           height=size1,
                           color=[1, 1, 1],
                           bold=True,
                           wrapWidth=1500,
                           font='Arial',
                           pos =(0,20),
                           autoLog=False)
    text2 = visual.TextStim(screen, text= b,
                           height=size2,
                           color=[1, 1, 1],
                           wrapWidth=1500,
                           font='Arial',
                           pos  = (0,-100),
                           autoLog=False)
    text3 = visual.TextStim(screen, text= c,
                           height=size3,
                           color=[1, 1, 1],
                           wrapWidth=1500,
                           font='Arial',
                           pos  = (0,-230),
                           autoLog=False)
    text.draw()
    text2.draw()
    text3.draw()
    screen.flip()

def window_2(a,b, size1, size2):
    text = visual.TextStim(screen, text= a,
                           height=size1,
                           color=[1, 1, 1],
                           bold=True,
                           wrapWidth=2000,
                           font='Arial',
                           pos =(0,0),
                           autoLog=False)
    text2 = visual.TextStim(screen, text= b,
                           height=size2,
                           wrapWidth= 2000,
                           color=[1, 1, 1],
                           font='Arial',
                           pos  = (0,-150),
                           autoLog=False)
    text.draw()
    text2.draw()
    screen.flip()

#==================================================================================#

# blank before start
window_1(None,None,None,None,None,None)

# Press the space bar to start or the escape to exit
key = event.waitKeys(keyList = ["space","escape"], clearEvents = True)
if key == ["escape"]:
    core.quit()


#================================= START EXPERIMENT ====================================#


##### Explain the experiment #####
'''
#------------------ 실험 개요 ------------------#

a = "본 실험에선\n\n " \
    "두가지의 소리를 듣고 한 소리의 개수를 세는 \n\n " \
    "과제를 수행하게 될 것입니다. "
c = "‘스페이스 바’ 를 누르면 다음 페이지로 넘어갑니다."
window_1(a,None, c, 35, None, 23)

key = event.waitKeys(keyList = ["space","escape"], clearEvents = True)
if key == ["escape"]:
    core.quit()

#------------------ 자극 설명 ------------------#

a = "'기본 소리'  와  '목표 소리' \n\n 두가지의 소리를 듣게 될 것이며,\n\n" \
    "이 두 소리는 서로 다른 비율로 제시될 것입니다."

window_1(a, None, c, 35, None, 23)
key = event.waitKeys(keyList = ["space","escape"], clearEvents = True)
if key == ["escape"]:
    core.quit()

#---------------- 자극 비율 설명 ----------------#

a = "그 중  '목표 소리'  가 더 적은 비율로 나올 것입니다. \n\n" \
    "당신은  '목표 소리'  가 몇번 나왔는지 세어주세요.\n\n\n"\
    "그럼, 사용되는 두 소리를 들려드리겠습니다."

window_1(a, None, c, 35, None, 23)

key = event.waitKeys(keyList = ["space","escape"], clearEvents = True)
if key == ["escape"]:
    core.quit()


#--------------- Standard 사운드 ---------------#

a = "이 소리를 기억하세요.\n\n\n\n"
window_1(a,None, None, 35, None, None)

time.sleep(1)
port.write(b'2')     # Sends the Serial value to Arduino to play the Standard sound
b = "'기본 소리' 입니다.\n\n\n"
c = "‘b’ 를 누르면 다시 한번 재생됩니다.\n\n"\
    "‘스페이스 바’ 를 누르면 다음 페이지로 넘어갑니다."
window_1(a,b, c, 35, 35, 23)

key = event.waitKeys(keyList = ["space",'b', "escape"], clearEvents = True)
if key == ["escape"]:
    core.quit()


#-------------- 다시 ( 'b' 누른 경우 ) --------------#

if key == ['b']:
    while key == ['b']:

        port.write(b'2')
        time.sleep(2)
        key = event.waitKeys(keyList=["space", 'b',"escape"], clearEvents=True)
        if key == ["escape"]:
            core.quit()


#----------------- Target 사운드 ------------------#

a = "이 소리를 기억하세요.\n\n\n\n"
window_1(a,None, None, 35, None, None)

time.sleep(1)
port.write(b'3')    # Sends the Serial value to Arduino to play the Target sound
b = "'목표 소리' 입니다.\n\n\n"
c = "‘b’ 를 누르면 다시 한번 재생됩니다.\n\n"\
    "‘스페이스 바’ 를 누르면 다음 페이지로 넘어갑니다."
window_1(a,b, c, 35, 35, 23)

key = event.waitKeys(keyList=["space", 'b',"escape"], clearEvents=True)
if key == ["escape"]:
    core.quit()


#-------------- 다시 ( 'b' 누른 경우 ) --------------#

while key == ['b']:

    port.write(b'3')
    time.sleep(2)
    key = event.waitKeys(keyList=["space", 'b', "escape"], clearEvents=True)
    if key == ["escape"]:
        core.quit()


#-------------------- 주의 사항 --------------------#

a = "소리가 제시되는 동안은 \n\n" \
    "' + ' \n\n" \
    "위 기호에 시선을 집중하여 주시고,\n\n"\
    "몸과 눈의 움직임을 최소화하여 주세요."

c = "‘스페이스 바’ 를 누르면 다음 페이지로 넘어갑니다."
window_1(a, None, c, 35, None, 23)

key = event.waitKeys(keyList = ["space","escape"], clearEvents = True)
if key == ["escape"]:
    core.quit()


#----------------------- 연습 -----------------------#

a = "그럼, 연습을 해보겠습니다.\n\n\n\n"
b = "'목표 소리' 가 몇번 나왔는지 세어주세요.\n\n"
window_1(a, b, None, 35, 30, None)
time.sleep(1)
for i in (3,2,1):
    c = str(i)+"초 뒤 시작됩니다."
    window_1(a, b, c, 35, 30, 30)
    time.sleep(1)

a = " + "
window_2(a,None, 100, None)

port.write(b'4')    # Play practice sound ( 10 trial )
time.sleep(11)       # length of the practice sound


#------------------- 정답 타이핑 -------------------#

a = "'목표 소리' 는 몇번 나왔나요?"
c = "키보드에 입력해주세요."
window_1(a, None, c, 38, None, 30)

key = event.waitKeys(keyList=['0','1','2','3','4','5','6','7','8','9'], clearEvents=True)
time.sleep(1)

#------------------ 틀렸을 때 다시 ------------------#

if key != ['2']:  # 정답수 = 2
    a = "다시 해보겠습니다.\n\n\n\n"
    b = "'목표 소리' 가 몇번 나왔는지 세어주세요.\n\n"
    window_1(a, b, None, 35, 30, None)
    time.sleep(1)

    for i in (5,4,3,2,1):
        b = str(i) + "초 뒤 시작됩니다."
        window_1(a, b, c, 35, 30, 30)
        time.sleep(1)

    # 자극
    a = " + "
    window_2(a, None, 100 ,None)
    time.sleep(3)
    port.write(b'4')   # Play practice sound ( 10 trial )
    time.sleep(9)      # length of the practice sound

    # 몇번?
    a = "'목표 소리' 는 몇번 나왔나요?\n\n"
    c = "해당 숫자의 키보드를 눌러주세요."
    window_1(a, None, c, 38, None, 30)
    key = event.waitKeys(keyList=['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'], clearEvents=True)
    time.sleep(1)

#------------------ 실험 구성 설명 ------------------#
'''
a = "잘하셨습니다! \n\n\n " \
    "과제는 한번 진행되며, \n\n" \
    "소요시간은 대략 20분 입니다.\n"

c = "‘스페이스 바’ 를 누르면 다음 페이지로 넘어갑니다."
window_1(a,None, c, 35, None, 23)

key = event.waitKeys(keyList = ["space","escape"], clearEvents = True)
if key == ["escape"]:
    core.quit()

#---------------------- 시작 전 ----------------------#

a = "그럼, 실험을 시작하겠습니다."
c = "궁금한게 있으시면 손을 들어 주시고,\n\n"\
    "준비가 되셨으면 '스페이스 바' 를 눌러주세요."
window_1(a, None, c, 50, None, 25)

key = event.waitKeys(keyList = ["space","escape"], clearEvents = True)
if key == ["escape"]:
    core.quit()


#--------------------------------------------------------------------#
#---------------------------- START TASK ----------------------------#
#--------------------------------------------------------------------#


# Set parameter
block = 1
trial = 5

# Import Current Date & Time
date_time = data.getDateStr()

# Open Text file to record
with open(date_time + '.txt', 'w') as f:
    sttime = datetime.now().strftime('%H:%M:%S - ')
    f.write("START "+ sttime + "\n")
    f.write("block = "+str(block)+"\n\n")

#============================== Streaming ============================#

# Run during 3 blocks
while block < 2:

    # Start task
    a = "START"
    for i in (5, 4, 3, 2, 1):
        b = str(i) + "초 뒤 시작됩니다."
        window_2(a, b, 100, 35)
        time.sleep(1)

    # Sound start
    a = "+"
    window_2(a,None, 100, None)
    port.write(b'1')      # Sends the Serial value to Arduino to play sound array during a block
    Board_data = board.get_board_data()
    # EEG Data & AUX Data Recording
    while True:

        # Receive All Data

        # data = board.get_current_board_data(125)
        Board_data = board.get_board_data()

        # Seperate data
        eeg_data = Board_data[eeg_channels, :]
        aux_data = Board_data[aux_channels, :]

        # EXIT
        key = event.getKeys()
        if key == ["escape"]:
            core.quit()

        # Check whether the sample has been entered or not
        # Stack data only when sample is entered, because there are cases where sample_eeg is not entered.
        if eeg_data.size > 0 :

            # Stack data in list
            eeg = np.concatenate((eeg, eeg_data), axis=1)
            aux = np.concatenate((aux, aux_data), axis=1)
            print("{}".format(aux_data))  # for checking

            # Record Data to a Text file in real-time
            sample_e = "".join([str(eeg_data)])
            sample_a = "".join([str(aux_data)])

            with open(date_time + '.txt', 'a+') as f:
                sttime = datetime.now().strftime('%Y%m%d_%H:%M:%S - ')
                f.write(str(len(eeg.T))+" : {0}  ".format(sample_e))
                f.write("  {0}".format(sample_a))
                f.write(sttime + "\n")


        # Set the Experiment time corresponcing to the sample length.
        # End current block
        if len(eeg.T) > (125*31):        #((125*1.1)*(trial)+(125*5)):  # Extra 5 seconds (250sample)

            # Stack the total data of the current block.
            EEG_Record.append(eeg)
            AUX_Record.append(aux)

            # Save data over each block.
            EEG = np.asarray(EEG_Record)
            AUX = np.asarray(AUX_Record)
            np.save(path + 'EEG', EEG)
            np.save(path + 'A', AUX)

            # Question
            a = "실험이 끝났습니다."
            c = "'목표 소리'가 몇번 나왔는지 키보드에 입력하여주세요."
            window_1(a, None, c, 50, None, 35)

            key = event.waitKeys(keyList=['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', "escape"], clearEvents=True)
            key2 = event.waitKeys(keyList=['0', '1', '2', '3', '4', '5', '6', '7', '8', '9',"escape"], clearEvents=True)

            if key == ["escape"] or key2 == ["escape"]:
                core.quit()

            # Write a response to the Text file
            key = "".join([str(key[0])])
            key2 = "".join([str(key2[0])])

            with open(date_time + '.txt', 'a+') as f:
                sttime = datetime.now().strftime('%Y%m%d_%H:%M:%S - ')
                f.write("Answer = {0} / ".format(key+key2))
                f.write(sttime + "\n\n")
                #f.write("block = " + str(block+1) + "\n\n")

            a = "THE END"
            b = "수고하셨습니다!"
            window_2(a,b, 100, 40)
            time.sleep(3)

            # Next block
            block = block + 1

            # Exit second while
            break

# Close port & window
port.close()
screen.close()

## Save mat file
scipy.io.savemat(path+'EEG.mat', {'EEG':EEG})
scipy.io.savemat(path+'A.mat', {'AUX':AUX})