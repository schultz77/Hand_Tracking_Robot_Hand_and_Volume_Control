""" This script enables the control of lego motors using buildhat with raspberry pi 4 (bullseye)
for mimicking hand movements. Finger/hand detection was performed by using the library mediapipe. 
Basis for the implementation can be found here: https://github.com/Diwas524/Volume-Control-using-gesture  """


import cv2
import time
from gtts import gTTS
import playsound
import os

from Frame_Capture_thrd_stop import piVideoStream
import hand_tracking_module as htm
from buildhat import Motor

# setting parameters for streaming window
dispW = 640
dispH = 480
frameRate = 30
fps = 0
textPos = (30, 60)
font = cv2.FONT_HERSHEY_SIMPLEX
textHeight = 1
textWeight = 3
textColor = (0, 0, 180)

# init max length from finger tips to wrist
maxThumb_len = 0
maxIndex_len = 0
maxMid_len = 0
maxRing_len = 0
maxPinky_len = 0

# init finger open flags
thumbOpen = None
indexOpen = None
midOpen = None
ringOpen = None
pinkyOpen = None

# defining lego build hat ports connected to finger motors
mid = 'A'
idx = 'D'
rng = 'B'
pnk = 'C'

# setting finger motors
mid_finger = Motor(mid)
ring_finger = Motor(rng)
pinky = Motor(pnk)
idx_finger = Motor(idx)
speed = 100

# init previous finger open flags
idx_prev = None
mid_prev = None
rng_prev = None
pnk_prev = None

# instantiating class for capturing frames
myCap = piVideoStream(resolution=(dispW, dispH), framerate=frameRate)
# starting thread for capturing frames
myCap.start()
# instantiating class for detecting hands
myDetector = htm.handDetector(detectionConf=0.7)

# myLM_List_1 = []
# myLM_List_2 = []

while True:
    img = myCap.getFrame()
    tStart = time.time()

    if len(img):
        img=cv2.flip(img,-1)  # flipping frame by 180 degrees
        img = myDetector.findHands(img=img)  # detecting hand on image
        lmList = myDetector.findPosition(img, draw=False)  # finding hand position on image, returning landmarks
        if len(lmList):

            # index finger mcp to middle finger mcp - reference
            len_idx_mid_mcp, idx_mid_mcp_coord = myDetector.findLength(lmList, 5, 9)
            # center_text = '{:.2f}'.format(len_idx_mid_mcp)
            # myDetector.showLen(img, idx_mid_mcp_coord, center_text)

            # thumb tip to wrist
            len_thumb_wrist, thb_wrist_coord = myDetector.findLength(lmList, 4, 0)
            maxThumb_len = len_idx_mid_mcp * 4  # ccb, parameter defined empirically
            if len_thumb_wrist <= maxThumb_len:
                thumbOpen = False
                # center_text = 'Thumb closed {:.2f}'.format(len_thumb_wrist)
            else:
                thumbOpen = True
                # center_text = 'Thumb open {:.2f}'.format(len_thumb_wrist)
            # myDetector.showLen(img, thb_wrist_coord, center_text)

            # index fingertip to wrist
            len_idx_tip_wrist, idx_tip_wrist_coord = myDetector.findLength(lmList, 8, 0)
            # maxIndex_len = len_idx_mid_mcp * 7.5  # ccb 
            maxIndex_len = len_idx_mid_mcp * 6.5  # ccb, parameter defined empirically
            if len_idx_tip_wrist <= maxIndex_len:
                indexOpen = False
                # center_text = 'Index closed {:.2f}'.format(len_idx_tip_wrist)
            else:
                indexOpen = True
                # center_text = 'Index open {:.2f}'.format(len_idx_tip_wrist)
            # myDetector.showLen(img, idx_tip_wrist_coord, center_text)

            # middle fingertip to wrist
            len_mid_tip_wrist, mid_tip_wrist_coord = myDetector.findLength(lmList, 12, 0)
            maxMid_len = len_idx_mid_mcp * 7  # ccb, parameter defined empirically
            if len_mid_tip_wrist <= maxMid_len:
                midOpen = False
                # center_text = 'Mid closed {:.2f}'.format(len_mid_tip_wrist)
            else:
                midOpen = True
            #     center_text = 'Mid open {:.2f}'.format(len_mid_tip_wrist)
            # myDetector.showLen(img, mid_tip_wrist_coord, center_text)

            # ring fingertip to wrist
            len_rng_tip_wrist, rng_tip_wrist_coord = myDetector.findLength(lmList, 16, 0)
            maxRing_len = len_idx_mid_mcp * 6.5  # ccb, parameter defined empirically
            if len_rng_tip_wrist <= maxRing_len:
                ringOpen = False
                # center_text = 'Ring closed {:.2f}'.format(len_rng_tip_wrist)
            else:
                ringOpen = True
            #     center_text = 'Ring open {:.2f}'.format(len_rng_tip_wrist)
            # myDetector.showLen(img, rng_tip_wrist_coord, center_text)

            # pinky fingertip to wrist
            len_pnk_tip_wrist, pnk_tip_wrist_coord = myDetector.findLength(lmList, 20, 0)
            maxPinky_len = len_idx_mid_mcp * 5.5  # ccb, parameter defined empirically
            if len_pnk_tip_wrist <= maxPinky_len:
                pinkyOpen = False
                # center_text = 'Pinky closed {:.2f}'.format(len_pnk_tip_wrist)
            else:
                pinkyOpen = True
                # center_text = 'Pinky open {:.2f}'.format(len_pnk_tip_wrist)
            # myDetector.showLen(img, pnk_tip_wrist_coord, center_text)

            # myLM_List_1.append(len_idx_mid_mcp)
            # myLM_List_2.append(len_rng_tip_wrist)

        cv2.putText(img, str(int(fps)) + ' FPS', textPos, font, textHeight, textColor, textWeight)
        cv2.imshow('Preview', img)  # Display the Video

        if indexOpen and indexOpen != idx_prev:
            idx_finger.run_to_position(-60,speed,blocking=False)
        elif indexOpen != idx_prev:
            idx_finger.run_to_position(160,speed, blocking=False)
        idx_prev = indexOpen

        if midOpen and midOpen != mid_prev:
            mid_finger.run_to_position(0,speed,blocking=False)        
        elif midOpen != mid_prev:
            mid_finger.run_to_position(-90,speed, blocking=False)
        mid_prev = midOpen

        if ringOpen and ringOpen != rng_prev:
            ring_finger.run_to_position(0,speed,blocking=False)        
        elif ringOpen != rng_prev:
            ring_finger.run_to_position(-90,speed, blocking=False)
        rng_prev = ringOpen

        if pinkyOpen and pinkyOpen != pnk_prev:
            pinky.run_to_position(-90,blocking=False)        
        elif pinkyOpen != pnk_prev:
            pinky.run_to_position(160,speed, blocking=False)
        pnk_prev = pinkyOpen
                
        if cv2.waitKey(1) == ord('q'):
            myCap.stop()  # When everything done, release the capture
            myCap.join()
            break

        tEnd = time.time()
        loopTime = tEnd - tStart
        fps = 0.8 * fps + 0.2 * (1 / loopTime)

# When everything done, release the capture
cv2.destroyAllWindows()
# factorList = [n1/n2 for n1, n2 in zip(myLM_List_2, myLM_List_1)]
# print(np.mean(factorList), np.std(factorList))

# showing the middle finger to say goodbye :D
idx_finger.run_to_position(160,speed, blocking=False)
mid_finger.run_to_position(0,speed, blocking=False)
ring_finger.run_to_position(-90,speed, blocking=False)
pinky.run_to_position(160,speed, blocking=False)

tts = gTTS('Schleich dich', lang='de')
tts.save('schleichen.mp3')
playsound.playsound('schleichen.mp3')
os.remove('schleichen.mp3')
