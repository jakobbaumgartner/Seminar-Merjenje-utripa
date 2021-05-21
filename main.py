from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.graphics import *


from kivy.graphics.texture import Texture
import cv2 as cv
from kivy.utils import rgba
import numpy as np
from numpy.lib.function_base import average
from numpy.ma import size
from scipy.ndimage import gaussian_filter1d
from scipy.signal import argrelextrema
from kivy_garden.graph import Graph, LinePlot, MeshLinePlot
import matplotlib.pyplot as plt


from heart import heartDetector

detector = heartDetector()

class cameraOne(BoxLayout):
    
    orientation = 'vertical'
    isButtonPressed = False
    meanValues = []
    frameCounter = 0
    startFrameMean = 0
    seconds = []
    heartRate= 0
    xMinStart = 0  
    xMaxStart = 15
    padding = [5,15,5,5]
    settingsStatus = False

    image = Image()
    titleLabel = Label()
    titleLabel.text = "MERILEC UTRIPA"
    titleLabel.size_hint[1] = None
    titleLabel.size = (100,75) 
    titleLabel.font_size = 40
    titleLabel.color = [0,0,0,1]
    settingsButton = Button(text = 'Nastavitve', size_hint=(None, None), size = (390,50))
   
    # Prepare graph
    graph = Graph(x_ticks_minor=1,
            x_ticks_major=0, y_ticks_major=0, 
            y_grid_label=True, x_grid_label=True, padding=5,
            x_grid=False, y_grid=True, ymin=0, ymax=1, xmin = xMinStart, xmax = xMaxStart)
    
    plot = LinePlot(line_width=1,color=[164/255, 0/255, 0/255, 1])

    plot.points = []
    # self.graph.background_color = (1, 0, 0, 1)
    graph.add_plot(plot)

    heartRateLabel = Label(size = (600,50), pos = (0, 500))
    heartRateLabel.size_hint[1] = None
    heartRateLabel.font_size = 50
    heartRateLabel.color = [0,0,0,1]

    def __init__(self, **kwargs):
        super(cameraOne, self).__init__(**kwargs)
        availablePorts,workingPorts = detector.listCameras()
        print(workingPorts)
        # detector.setCamera()
        self.settingsScreen()

    def dropDownCallback(self,btn):
        # select camera
        self.dropdown.select(btn.text)
        detector.cameraId = int(btn.text[8:])
        print(btn.text[8:])
        try:
            Clock.unschedule(self.runner)
        except:
            print("runner off")

        detector.stopCamera()
        detector.setCamera()
        self.runner = Clock.schedule_interval(self.updateData, 1 / detector.fps)

    def settingsButtonMethod(self,_):
        self.settingsStatus = not self.settingsStatus
        print("Settings menu: " + str(self.settingsStatus))
        self.changeScreen()
    
    def changeScreen(self):
        """
            loads one of the screens
        """

        detector.stopCamera()

        try:
            Clock.unschedule(self.runner)
        except:
            print("runner off")

        

        if(self.settingsStatus):


            try:
                Clock.unschedule(self.runner)
            except:
                print("runner off")

            detector.stopCamera()
            # detector.setCamera()
            # self.runner = Clock.schedule_interval(self.updateData, 1 / detector.fps)

            self.remove_widget(self.titleLabel)
            self.remove_widget(self.image)
            self.remove_widget(self.mainbutton)
            self.remove_widget(self.settingsButton)
            self.measurementScreen()

        else:
            self.remove_widget(self.titleLabel)
            self.remove_widget(self.image)
            self.remove_widget(self.heartRateLabel)
            self.remove_widget(self.graph)
            self.remove_widget(self.startButton)
            self.remove_widget(self.settingsButton)
            self.settingsScreen() 




    def settingsScreen(self):
        """
            settings display
        """

        # detector.stopCamera()

        availablePorts,workingPorts = detector.listCameras()

        detector.setCamera()

        try:
            Clock.unschedule(self.runner)
        except:
            print("runner off")

        detector.stopCamera()
        detector.setCamera()
        self.runner = Clock.schedule_interval(self.updateData, 1 / detector.fps)

        # set DROPDOWN
        
        self.dropdown = DropDown()

        for index in workingPorts:
            # When adding widgets, we need to specify the height manually
            # (disabling the size_hint_y) so the dropdown can calculate
            # the area it needs.

            btn = Button(text='Camera: %d' % index, size_hint_y=None, height=44)

            # for each button, attach a callback that will call the select() method
            # on the dropdown. We'll pass the text of the button as the data of the
            # selection.
            btn.bind(on_release=lambda btn: self.dropDownCallback(btn))

            # then add the button inside the dropdown
            self.dropdown.add_widget(btn)

        # create a big main button
        self.mainbutton = Button(text='Select camera', size_hint=(None, None), width = Window.size[0]-10)

        # show the dropdown menu when the main button is released
        # note: all the bind() calls pass the instance of the caller (here, the
        # mainbutton instance) as the first argument of the callback (here,
        # dropdown.open.).
        self.mainbutton.bind(on_release=self.dropdown.open)

        # one last thing, listen for the selection in the dropdown list and
        # assign the data to the button text.
        self.dropdown.bind(on_select=lambda instance, x: setattr(self.mainbutton, 'text', x))




        self.add_widget(self.titleLabel)
        self.add_widget(self.image)
        self.add_widget(self.mainbutton)
        self.settingsButton.bind(on_release = self.settingsButtonMethod)
        self.add_widget(self.settingsButton)
        


    def measurementScreen(self):
        """
            normal operation of the application
        """

        # start camera
        detector.setCamera()

        # schedule measurements
        runner = Clock.schedule_interval(self.updateData, 1 / detector.fps)
        
           
      
        # # Prepare graph
        # self.graph = Graph(x_ticks_minor=1,
        #         x_ticks_major=0, y_ticks_major=0, 
        #         y_grid_label=True, x_grid_label=True, padding=5,
        #         x_grid=False, y_grid=True, ymin=0, ymax=1, xmin = self.xMinStart, xmax = self.xMaxStart)
        
        # self.plot = LinePlot(line_width=1,color=[164/255, 0/255, 0/255, 1])

        # self.plot.points = []
        # # self.graph.background_color = (1, 0, 0, 1)
        # self.graph.add_plot(self.plot)
        # self.graph.add_plot(self.heights)
        

       

        self.border = (10,10,10,10)

      # Prepare all widgets
        
        # self.heartRateLabel = Label(size = (600,50), pos = (0, 500))
        # self.heartRateLabel.size_hint[1] = None
        # self.heartRateLabel.font_size = 50
        # self.heartRateLabel.color = [0,0,0,1]
        self.startButton = Button(text = 'RESTART', size = (600,50))
        self.startButton.size_hint[1] = None
        # with self.heartRateLabel.canvas.before:
           
        #     Color(5/255, 0/255, 0/255)
        #     Rectangle(size=self.heartRateLabel.size, pos = self.heartRateLabel.pos)
            
            
        self.startButton.bind(on_release = self.startButtonMethod)
        self.add_widget(self.titleLabel)
        self.add_widget(self.image)
        self.add_widget(self.heartRateLabel)
        self.add_widget(self.graph)
        self.add_widget(self.startButton)
        self.add_widget(self.settingsButton)


    def updateData (self, _):

        # Keep track of running frames
        self.frameCounter += 1 

        
        # run detector methods
        detector.getFrame(self.frameCounter)

        # Move x axis if time exceeds 30s.
        if self.frameCounter % (self.xMaxStart * detector.fps) == 0 and self.frameCounter != 0:
            self.graph.xmin += self.xMaxStart
            self.graph.xmax += self.xMaxStart

        
        
        # Plot running values on graph
        self.graph.ymin = int((detector.meanFrameValue) - 3)
        self.graph.ymax = int((detector.meanFrameValue) + 3)
        self.plot.points = detector.framesArr    

        # Show current heart rate 
        
        self.heartRateLabel.text = str(int(detector.averageHR)) + ' BPM'

            
     

        # Camera feed visualization in kivy
        if detector.ret:
            buf1 = cv.flip(detector.frame, 0)
            buf = buf1.tostring()
            texture = Texture.create(size=(detector.frame.shape[1], detector.frame.shape[0]), colorfmt='bgr') 
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.image.texture = texture


    def startButtonMethod(self, _):
        self.isButtonPressed = not self.isButtonPressed
        # restart plot view
        self.meanValues = []
        self.frameCounter = 0
        detector.framesArr = []
        self.numberOfPeaks = 0
        # self.heartRateLabel.text = str(self.heartRate) + ' BPM'
        self.graph.xmin = self.xMinStart
        self.graph.xmax = self.xMaxStart

        detector.restart()
        
      




class CameraApp(App):
    Window.size = (400,700)
    Window.clearcolor = rgba(255,255,255,1)
    title = "Merilec utripa"

   
 
    
    
    def build(self):

        return cameraOne()


if __name__ == '__main__':
    CameraApp().run()