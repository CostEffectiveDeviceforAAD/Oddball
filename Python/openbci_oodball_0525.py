""""""""""""""""""""""""""""""""""""""""""
 #        OpenBCI - Python LSL           #
 #           For Online AAD              #
""""""""""""""""""""""""""""""""""""""""""
#################

#================================== SET EXPERIMENT ================================================#

###### Imports #####
import librosa, warnings, random, time, sys, serial, pickle
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pylsl import StreamInlet, resolve_stream, StreamInfo
#from OpenBCI_lsl import *
from scipy import signal
from scipy.signal import butter, lfilter, resample, filtfilt
import scipy.io
#from helper import *
#from pymtrf import *
from psychopy import visual, core, event, data
from psychopy.tools.filetools import fromFile, toFile
#from preprocessing_ha import *
import msvcrt as m


#############################
#----------------------------- Connect to port of arduino ------------------------------#

port = serial.Serial("COM8", 9600)   ## ksit laptop : com8 / my laptop : com10

#----------------------------- Open LSL network -----------------------------#

# first resolve an EEG stream on the lab network
print("looking for an EEG stream...")
streams_eeg = resolve_stream('type', 'EEG')
streams_aux = resolve_stream('type', 'AUX')


# create a new inlet to read from the stream
print("StreamInlet")
inlet_eeg = StreamInlet(streams_eeg[0])    # channel
inlet_aux = StreamInlet(streams_aux[0])            # aux


#----------------------------- Parameter Setting -----------------------------#

# Set int
tr = 0
a = 0
b = 0
eeg = []
aux = []
subject = 1
EEG_Record = []
AUX_Record = []
path = 'C:/Users/LeeJiWon/Desktop/Oddball Task/save_data/'         ##'C:/Users/LeeJiWon/Desktop/Oddball Task/save_data/'   ##'C:/Users/user/Desktop/hy-kist/OpenBCI/save_data/'

#===================== Excel ==================#
'''
psychopyVersion = '2020.2.10'
#expName = '05.01_2'
#expInfo = {'participant': '', 'session': '001'}
#expInfo['date'] = data.getDateStr()  # add a simple timestamp
#expInfo['expName'] = expName
#expInfo['psychopyVersion'] = psychopyVersion

thisExp = data.ExperimentHandler(name='ff', version='',
    extraInfo=None, runtimeInfo=None,
    originPath='C:\\Users\\user\\Desktop\\hy-kist\\OpenBCI\\Python_code\\openbci_oddball_0510.py',
    savePickle=True, saveWideText=True,
    dataFileName='subject')
'''
#===========================================================================================#
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
    #pos = [100,0]
                    )


#
def window(a, b, c, size1, size2, size3):
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

def windowc(a,b, size1, size2):
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


window(None,None,None,None,None,None)
key = event.waitKeys(keyList = ["space","escape"], clearEvents = True)
if key == ["escape"]:
    core.quit()

'''
#============= 인사
a = "안녕하세요. \n\n Auditory Oddball 실험에 \n\n참가해주셔서 감사합니다. "
c = "\n\n‘스페이스 바’ 를 누르면 다음 페이지로 넘어갑니다."
window(a, None, c, 50, None, 25)
# 스페이스 기다리기
key = event.waitKeys(keyList = ["space","escape"], clearEvents = True)
if key == ["escape"]:
    core.quit()
'''

#=============== 실험 개요
a = "본 실험에선\n\n " \
    "두가지의 소리를 듣고 한 소리의 개수를 세는 \n\n " \
    "과제를 수행하게 될 것입니다. "
c = "‘스페이스 바’ 를 누르면 다음 페이지로 넘어갑니다."
window(a,None, c, 35, None, 23)

key = event.waitKeys(keyList = ["space","escape"], clearEvents = True)
if key == ["escape"]:
    core.quit()

#================ 자극 설명
a = "'기본 소리'  와  '목표 소리' \n\n 두가지의 소리를 듣게 될 것이며,\n\n" \
    "이 두 소리는 서로 다른 비율로 제시될 것입니다."

window(a, None, c, 35, None, 23)
key = event.waitKeys(keyList = ["space","escape"], clearEvents = True)
if key == ["escape"]:
    core.quit()

#=========== 자극 비율 설명

a = "그 중  '목표 소리'  가 더 적은 비율로 나올 것입니다. \n\n" \
    "당신은  '목표 소리'  가 몇번 나왔는지 세어주세요.\n\n\n"\
    "그럼, 사용되는 두 소리를 들려드리겠습니다."

window(a, None, c, 35, None, 23)

key = event.waitKeys(keyList = ["space","escape"], clearEvents = True)
if key == ["escape"]:
    core.quit()


#==== standard 사운드
a = "이 소리를 기억하세요.\n\n\n\n"
window(a,None, None, 35, None, None)

time.sleep(1)
port.write(b'2') # 아두이노에 테스트용 사운드 제시 코드 걸기.
b = "'기본 소리' 입니다.\n\n\n"
c = "‘b’ 를 누르면 다시 한번 재생됩니다.\n\n"\
    "‘스페이스 바’ 를 누르면 다음 페이지로 넘어갑니다."
window(a,b, c, 35, 35, 23)
#time.sleep(1)

#=================== 다시

key = event.waitKeys(keyList = ["space",'b', "escape"], clearEvents = True)
if key == ["escape"]:
    core.quit()

# 사운드 다시
if key == ['b']:
    while key == ['b']:

        # a = " 다시2 "
        # window(a,b, c, 50, 50, 40)
        port.write(b'2')
        time.sleep(2)
        key = event.waitKeys(keyList=["space", 'b',"escape"], clearEvents=True)
        if key == ["escape"]:
            core.quit()

#======================= Next =====================#

#====================== Target Sound
a = "이 소리를 기억하세요.\n\n\n\n"
window(a,None, None, 35, None, None)

time.sleep(1)
port.write(b'3') # 아두이노에 테스트용 사운드 제시 코드 걸기.
b = "'목표 소리' 입니다.\n\n\n"
c = "‘b’ 를 누르면 다시 한번 재생됩니다.\n\n"\
    "‘스페이스 바’ 를 누르면 다음 페이지로 넘어갑니다."
window(a,b, c, 35, 35, 23)
#time.sleep(1)

#====================== 다시
key = event.waitKeys(keyList=["space", 'b',"escape"], clearEvents=True)
if key == ["escape"]:
    core.quit()

# 사운드 다시
while key == ['b']:

    #a = " 다시2 "
    #window(a,b, c, 50, 50, 40)
    port.write(b'3')
    time.sleep(2)
    key = event.waitKeys(keyList=["space", 'b', "escape"], clearEvents=True)
    if key == ["escape"]:
        core.quit()

#========================= Next


#==================== 주의 사항
a = "소리가 제시되는 동안은 \n\n" \
    "' + ' \n\n" \
    "위 기호에 시선을 집중하여 주시고,\n\n"\
    "몸과 눈의 움직임을 최소화하여 주세요."

c = "‘스페이스 바’ 를 누르면 다음 페이지로 넘어갑니다."
window(a, None, c, 35, None, 23)

key = event.waitKeys(keyList = ["space","escape"], clearEvents = True)
if key == ["escape"]:
    core.quit()

#============================ 연습
a = "그럼, 연습을 해보겠습니다.\n\n\n\n"
b = "'목표 소리' 가 몇번 나왔는지 세어주세요.\n\n"
window(a, b, None, 35, 30, None)
time.sleep(1)
for i in (5,4,3,2,1):
    c = str(i)+"초 뒤 시작됩니다."
    #b = "Target sound가 몇번 나왔는지 세어주세요."
    window(a, b, c, 35, 30, 30)
    time.sleep(1)

a = " + "
windowc(a,None, 100, None)
port.write(b'4') # 아두이노에 연습 음원
time.sleep(9) # 연습음원 시간만큼

#============================== 몇번?
a = "'목표 소리' 는 몇번 나왔나요?"
c = "키보드에 입력해주세요."
window(a, None, c, 38, None, 30)
key = event.waitKeys(keyList=['0','1','2','3','4','5','6','7','8','9'], clearEvents=True)
time.sleep(1)

#============================== 틀렸을 때 다시.
if key != ['2']:  # 정답수
    a = "다시 해보겠습니다.\n\n\n\n"
    b = "'목표 소리' 가 몇번 나왔는지 세어주세요.\n\n"
    window(a, b, None, 35, 30, None)
    time.sleep(1)

    for i in (5,4,3,2,1):
        b = str(i) + "초 뒤 시작됩니다."
        window(a, b, c, 35, 30, 30)
        time.sleep(1)

    # 자극
    a = " + "
    windowc(a, None, 100 ,None)
    time.sleep(3)
    port.write(b'4') # 아두이노에 연습 음원
    time.sleep(9) # 연습음원 시간만큼

    # 몇번?
    a = "'목표 소리' 는 몇번 나왔나요?\n\n"
    c = "해당 숫자의 키보드를 눌러주세요."
    window(a, None, c, 38, None, 30)
    key = event.waitKeys(keyList=['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'], clearEvents=True)
    time.sleep(1)

#================== 실험 구성 설명

a = "잘하셨습니다! \n\n\n " \
    "과제는 총 3개의 세션으로 나눠져 진행 될 것이며,\n\n" \
    "각 세션의 소요시간은 5분입니다."
c = "‘스페이스 바’ 를 누르면 다음 페이지로 넘어갑니다."
window(a,None, c, 35, None, 23)

key = event.waitKeys(keyList = ["space","escape"], clearEvents = True)
if key == ["escape"]:
    core.quit()

#=============================== 통과
a = "각 세션이 끝난 후 쉬는 시간이 주어지며,\n\n" \
    "쉬는 시간 동안은 자리에서 몸을 움직이셔도 됩니다.\n\n"\
    "충분히 쉬신 후 '스페이스 바'를 눌러 다음 세션을 진행하세요."

window(a, None, c, 35, None, 23)
key = event.waitKeys(keyList = ["space","escape"], clearEvents = True)
if key == ["escape"]:
    core.quit()

#==============
a = "그럼, 첫번째 세션을 시작하겠습니다."

c = "궁금한게 있으시면 손을 들어 주시고,\n\n"\
    "준비가 되셨으면 '스페이스 바' 를 눌러주세요."

window(a, None, c, 50, None, 25)
key = event.waitKeys(keyList = ["space","escape"], clearEvents = True)
if key == ["escape"]:
    core.quit()

#######################################################################
'''
# 엑셀연동
wb = openpyxl.Workbook()
sheet = wb.active
sheet['A1'] = "Key"
'''

block = 1
trial = 375

date = data.getDateStr()
# Open Text file
with open(date + '.txt', 'w') as f:
    sttime = datetime.now().strftime('%H:%M:%S - ')
    f.write("START "+ sttime + "\n")
    f.write("block = "+str(block)+"\n\n")

##============================ streaming ==========================##
while block != 4:

    inlet_eeg = StreamInlet(streams_eeg[0])  # channel
    inlet_aux = StreamInlet(streams_aux[0])  # aux

    # 시작
    a = "START"
    for i in (5, 4, 3, 2, 1):
        b = str(i) + "초 뒤 시작됩니다."
        windowc(a, b, 100, 35)
        time.sleep(1)

    # sound start
    #port.write(b'1')
    a = "+"
    windowc(a,None, 100, None)
    port.write(b'1')

     # 실제 실험 아두이노.

    ######### streaming


    while True:

        [sample_eeg, ts_eeg] = inlet_eeg.pull_sample()
        [sample_aux, ts_aux] = inlet_aux.pull_sample()
        key = event.getKeys()
        if key == ["escape"]:
            core.quit()

        #sample_aux[0] = round(sample_aux[0])
        #sample_aux[1] = round(sample_aux[1])

        if sample_eeg:
            eeg.append(sample_eeg)
            aux.append(sample_aux)
            #print("{}".format(len(eeg)))
            print("{}".format(sample_aux))

            ##
            sample_e = "".join([str(sample_eeg)])
            sample_a = "".join([str(sample_aux)])
            with open(date + '.txt', 'a+') as f:
                sttime = datetime.now().strftime('%Y%m%d_%H:%M:%S - ')
                f.write(str(len(eeg))+" : {0}  ".format(sample_e))
                f.write("  {0}".format(sample_a))
                f.write(sttime + "\n")


        if len(eeg) == (125*(trial*0.8)+250):  # 시간에 따라

            EEG_Record.append(eeg)
            AUX_Record.append(aux)

            # Save per block
            EEG_b = np.asarray(eeg)
            AUX_b = np.asarray(aux)
            np.save(path + 'EEG_' + str(block), EEG_b)
            np.save(path + 'AUX_' + str(block), AUX_b)

            # question
            a = str(block) + " Block 이 끝났습니다."
            c = "'목표 소리'가 몇번 나왔는지 키보드에 입력하여주세요."
            window(a, None, c, 50, None, 35)
            key = event.waitKeys(keyList=['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', "escape"], clearEvents=True)
            key2 = event.waitKeys(keyList=['0', '1', '2', '3', '4', '5', '6', '7', '8', '9',"escape"], clearEvents=True)

            if key == ["escape"] or key2 == ["escape"]:
                core.quit()
            #time.sleep(1)

            # Write Text file
            key = "".join([str(key[0])])
            key2 = "".join([str(key2[0])])

            with open(date + '.txt', 'a+') as f:
                sttime = datetime.now().strftime('%Y%m%d_%H:%M:%S - ')
                f.write("Answer = {0} / ".format(key+key2))
                f.write(sttime + "\n\n")
                f.write("block = " + str(block+1) + "\n\n")

            if block != 3:

                # break
                a = "Break Time"
                b = "\n\n'스페이스 바' 를 누르면 다음 세션이 시작됩니다."
                windowc(a, b, 90, 35)
                key = event.waitKeys(keyList=["space", "escape"], clearEvents=True)
                if key == ["escape"]:
                    core.quit()

            elif block == 3:

                a = "THE END"
                b = "수고하셨습니다!"
                windowc(a,b, 100, 40)
                time.sleep(3)


            block = block + 1
            # reset
            eeg = []
            aux = []
            break


port.close()
screen.close()

# save
# Blcok by time by channel
EEG = np.asarray(EEG_Record)
AUX = np.asarray(AUX_Record)

##
np.save(path+'EEG_0526', EEG)
np.save(path+'A_0526', AUX)

scipy.io.savemat(path+'EEG_0526.mat', {'EEG':EEG})
scipy.io.savemat(path+'A_0526.mat', {'AUX':AUX})