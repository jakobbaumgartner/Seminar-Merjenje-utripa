import cv2 as cv
from kivy.clock import Clock
import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.signal import argrelextrema, find_peaks_cwt
import time

class heartDetector:

    fps = 15 # set fps, if too high camera limits it
    heights = []
    framesArr = [] 
    lastValuesHR = np.zeros((1,10))
    counterNums = []
    lookInterval = 20   # set how long is the rolling array
    meanValues =  np.zeros(15*lookInterval)
    timeArr = []
    prevFrameTime = 0
    newFrameTime = 0
    FPS = 0
    cameraId = 0

    def setCamera(self):

        self.heights = []
        self.framesArr = [] 
        self.lastValuesHR = np.zeros((1,10))
        self.counterNums = []
        self.meanValues =  np.zeros(15*self.lookInterval)
        self.timeArr = []
     
        # start camera
        self.cap = cv.VideoCapture(self.cameraId)
        self.cap.set(cv.CAP_PROP_FRAME_WIDTH, 320)
        self.cap.set(cv.CAP_PROP_FRAME_HEIGHT, 240)
        self.cap.set(cv.CAP_PROP_FPS, self.fps)

        self.t = time.time()

    def stopCamera(self):
        try:
            self.cap.release()
        except:
            print("cam off")
        

    def getFrame (self, frameCounterout):

        # calculate and print FPS
        self.prevFrameTime = self.newFrameTime
        self.newFrameTime = time.time()
        FPS = 1 / (self.newFrameTime - self.prevFrameTime)
        # print(FPS)

        # capture frame
        self.frameCounter = frameCounterout
        self.counterNums.append(self.frameCounter)
        self.ret, self.frame = self.cap.read()

        # convert frame to np
        print(self.frame)
        self.npFrame = np.asarray(self.frame)

           

        # get mean brightness of an image frame
        self.meanFrameValue = np.mean(self.npFrame)
        # append frame value to the rolling array
        self.meanValues = np.append(self.meanValues[1:], self.meanFrameValue)

        # equalise values, get local maxima and count them
        self.filteredMeanValues = gaussian_filter1d(self.meanValues, 2)
        self.localMaxIdx = np.array(argrelextrema(self.filteredMeanValues, np.greater)).flatten()
        self.numberOfPeaks = len(self.localMaxIdx)
   

        # From number of peaks compute heart rate
        self.heartRate = (self.numberOfPeaks * 60 / self.lookInterval)


        # average results of measurements, so that we get less jumpy result
        self.lastValuesHR = np.append(self.lastValuesHR, self.heartRate)
        self.lastValuesHR = self.lastValuesHR[1:] 
        self.averageHR = round(np.mean(self.lastValuesHR),1)

        
        # Update values on plot
        self.framesArr.append((self.frameCounter / self.fps, self.filteredMeanValues[-1]))
        self.timeArr.append(time.time())

        if(self.frameCounter == 15*20):

            np.save('newdataMV.npy', self.meanValues)
            np.save('newdataFMV.npy', self.filteredMeanValues)
            print("SAVED")

        print(self.cap.isOpened())

    

    def restart(self):
        self.meanValues =  np.zeros(15*self.lookInterval)
        self.framesArr = [] 
        self.heights = []
        self.timeArr = []

    def listCameras(self):

        workingPorts = []
        availablePorts = []

        portsToTest = [0,1,2,3,4,5]

        for port in portsToTest:
            camera = cv.VideoCapture(port)
            if not camera.isOpened():
                print("Port %s is not working." %port)
            else:
                is_reading, img = camera.read()
                w = camera.get(3)
                h = camera.get(4)
                if is_reading:
                    print("Port %s is working and reads images (%s x %s)" %(port,h,w))
                    workingPorts.append(port)
                else:
                    print("Port %s for camera ( %s x %s) is present but does not reads." %(port,h,w))
                    availablePorts.append(port)
            camera.release()
        return availablePorts,workingPorts

