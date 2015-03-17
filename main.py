# LiveTranslate was the result of roughly 24 hours of hackathon coding. 
# It is likely rife with bugs, lacks good style, and could generally be improved in many aspects.
# However, it works! 

import cv2
import numpy as np
import tesseract
import json
import requests
import urllib
import azure_translate_api
import threading
import Queue

WHITELIST = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ "


def updateWindow(videoCapture, frame):
    cv2.imshow("preview", frame)
    return videoCapture.read() # rval, frame

def updateTranslation(q, text):
    print 'TRANSLATING'
    client = azure_translate_api.MicrosoftTranslatorClient('HackRiceLiveTranslate', 'kD8XE7E0k/8YL7hekgFbuB3awbjagKuF1xG1aEpm220=')
  # This API key has been disabled
 q.put(client.TranslateText(text, 'en', 'es')) # Edit the languages here to change the "to" and "from" languages, respectively

def updateOCR(frame):
    api = tesseract.TessBaseAPI()
    api.SetVariable("tessedit_char_whitelist", WHITELIST)
    api.Init("C:\Program Files (x86)\Tesseract-OCR", "eng", tesseract.OEM_DEFAULT)
    api.SetPageSegMode(tesseract.PSM_AUTO)

    bitmap = cv2.cv.CreateImageHeader((frame.shape[1], frame.shape[0]), cv2.IPL_DEPTH_8U, 3)
    cv2.cv.SetData(bitmap, frame.tostring(), frame.dtype.itemsize * 3 * frame.shape[1])
    tesseract.SetCvImage(bitmap, api)
    text = api.GetUTF8Text()
    confidence = api.MeanTextConf()
    charMatrix = api.GetBoxText(0).split('\n')
    return text, confidence, charMatrix

def invertColor(color):
    return (255-color[0],255-color[1],255-color[2])

def displayText(text, font, boundingBox, frame, avgColor):
    avgColor = invertColor(avgColor)
    textList = text.split(" ")
    print textList
    tempText = ""
    avgY = cv2.getTextSize(textList[0], font, 1,2)[0][1]
    curY = boundingBox[0][1]
    startX = boundingBox[0][0]
    xDiff = boundingBox[1][0] - startX
    start = (startX, curY)
    for word in textList:
        curSize = cv2.getTextSize(tempText, font, 1,2)
        nextWordSize = cv2.getTextSize(word, font, 1,2)
        if curSize[0][0] + nextWordSize[0][0] >= xDiff:
            curY+=avgY
            start = (startX, curY)
            cv2.putText(frame, tempText, start, font, 1,avgColor,2, cv2.CV_AA)
            tempText = word + " "
        else:
            tempText += word + " "
    curY+=avgY
    start = (startX, curY)
    cv2.putText(frame, tempText, start, font, 1,avgColor,2, cv2.CV_AA)

def main():
    cv2.namedWindow("preview", cv2.cv.CV_WINDOW_NORMAL)
    vc = cv2.VideoCapture(0)
    height = int(vc.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))
    width = int(vc.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))
    print height, width

    rval = False
    if vc.isOpened(): # try to get the first frame
        rval, frame = vc.read()

    count = 0
    translatedText = None
    q = Queue.Queue()
    font = cv2.FONT_HERSHEY_DUPLEX
    while rval:
        rval, frame = updateWindow(vc, frame)

        if count % 5 == 0:
            text, confidence, charMatrix = updateOCR(frame)

        if confidence > 70:
            text = text.replace('\n', ' ')
            text = " ".join(text.split())
            #print text

            if count % 20 == 0 and len(text) > 2:
                t = threading.Thread(target=updateTranslation, args=(q, text))
                t.daemon = True
                t.start()
                if not q.empty():
                    translatedText = q.get(block=False).strip()
                    translatedText = ''.join(i for i in translatedText if i in WHITELIST)
                    print 'TRANS Returned: ' + translatedText
                #translatedText = "Por favor, no tome las sillas de la sala de clases"
            maxX = 0
            maxY = 0
            minX = width
            minY = height
            for charList in charMatrix:

                charVector = charList.split(" ")
                if len(charVector) > 1 and charVector[0] in WHITELIST:

                    pt1 = (int(charVector[1]), height - int(charVector[2]))
                    pt2 = (int(charVector[3]), height - int(charVector[4]))
                    minX = min(minX, pt1[0])
                    minY = min(minY, pt2[1])
                    maxX = max(maxX, pt2[0])
                    maxY = max(maxY, pt1[1])
                    #cv2.rectangle(frame, pt1, pt2, (0,255,0), 3)
                    #cv2.putText(frame, charVector[0], pt1, font, 1,(255,0,0),2)

            boundingPoints = ((minX,minY),(maxX,minY),(maxX,maxY),(minX,maxY))
            avgR, avgG, avgB = 0, 0, 0
            for point in boundingPoints:
                avgB += frame[point[1]-1, point[0]-1, 0]
                avgG += frame[point[1]-1, point[0]-1, 1]
                avgR += frame[point[1]-1, point[0]-1, 2]
            avgB /= 4
            avgG /= 4
            avgR /= 4
            avgColor = (avgB, avgG, avgR)

            if minX - maxX != width and minY - maxY != height and translatedText is not None:
                cv2.rectangle(frame, (minX, minY), (maxX, maxY), avgColor, -1)
                displayText(translatedText, font, boundingPoints, frame, avgColor)
            cv2.imshow("preview", frame)

        count += 1
        key = cv2.waitKey(10)
        if key == 27: # exit on ESC
            break
    vc.release()
    cv2.destroyWindow("preview")

main()


