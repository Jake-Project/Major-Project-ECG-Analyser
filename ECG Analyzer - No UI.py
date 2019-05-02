# -*- coding: utf-8 -*-
"""
Created on Mon Apr  1 17:22:38 2019

@author: rocke
"""

# File that was created in order to process the ECG data from the Welch Allyn System.
# Data aquisition Flow:
#   Welch Allyn -> Export To SCP -> Import to ECG Toolkit 2.4 -> 
#   Export As CSV -> Utilize this program to properly format CSV

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QMainWindow, QLabel, QGridLayout, QWidget, QSizePolicy, QVBoxLayout, QPushButton
from PyQt5.QtCore import QSize 

import matplotlib.pyplot as plt

#todo do i need this?
import math

from scipy.interpolate import interp1d # Maybe take out if not used


import os # Needed for folders
import sys
import csv
import numpy as np

# Boilerplate code - https://github.com/spyder-ide/spyder/wiki/How-to-run-PyQt-applications-within-Spyder
class createMainWindow(QMainWindow):
    
    # __init__ Is the constructor method for this class.
    # The object that we are constructing is QMainWindow which is part of PyQt
    # When createMainWindow is called we are creating the window in the constructor below
    # In summary self is the QMainWindow that we create that we are setting the variables for
    def __init__(self):
        QMainWindow.__init__(self)

        self.setMinimumSize(QSize(800, 600))    
        self.setWindowTitle("Please select a window containing all of the data you want to test in CSV format") 
        
        centralWidget = QWidget(self)          
        self.setCentralWidget(centralWidget)   
 
        gridLayout = QGridLayout(self)     
        centralWidget.setLayout(gridLayout)  

        
        # File Menu options
        file = self.menuBar().addMenu('File')
        actionQuit = file.addAction('Quit')
        actionQuit.setShortcut('Ctrl+Q')
        actionQuit.setShortcut('Ctrl+W')
        actionQuit.triggered.connect(QtWidgets.QApplication.quit)
        
        actionOpen = file.addAction('Open File')
        actionOpen.setShortcut('Ctrl+O')
        actionOpen.setStatusTip('Import File')
        actionOpen.triggered.connect(self.importFiles)
        # actionOpen = Action performed when button is pressed.
        # .triggered.connect causes the action to be performed
    
    # Function that allows for files to be imported into the program.
    # The user chooses a folder. The CSV Files in this folder are then imported into the program
    # Data from the files is iterated through and graphs are created
    def importFiles(self):

        # Sets filter to stop anything except CSV files
        filter = "Data Files(*.csv)"
        
        # Sets window name and directory to search in
        # Allows user to choose a directory containing ecg data
        folderInformation = QtWidgets.QFileDialog.getExistingDirectory(self, "Choose a folder which you want to test the data for", r'C:\Users\rocke\Sandbox\ECG\Major-Project-ECG-Analyser\Data', QtWidgets.QFileDialog.ShowDirsOnly)
        
        #If folderInformation[0] is populated, user has selected a file name that is not blank
        if folderInformation[0]:
            
            print('Folder Location: ' + str(folderInformation))
            # Gets files which are found in the location which the user selected
            for file in os.listdir(folderInformation):
                # Only allows files ending with .csv
                if file.endswith(".csv"):
                    # Prints the files that have been found to the user
                    print("File to open: " + str(folderInformation + '/' + file)) 
                    
                    # TODO - Method that opens each file individually to process the data
                    self.parseCsv(folderInformation, file)
            
    # Method to parse the CSV data
    def parseCsv(self, folderLocation, fileName):
        print("Parsing CSV data to an array")
        
        file = open(folderLocation + '/' + fileName, 'r')

        # Read in the data
        with file:
            ecgData = file.read()
            print('There are ' + str(sum(1 for row in ecgData)) + ' Records in the CSV data')
            #print(type(ecgData))
            #print(ecgData)
            ecgDataLines = [] # To hold all of the data for all 8 leads including the averaged signal - Holds as CSV for saving out
            averagedSignalData = [] # To hold only the data for the averaged signal - Holds like an array
            
            # for zero crossing
            ecgMean = 0.0
            ecgMeanCounter = 0
            
            # Test for zero crossings - Uses rolling average
            ecgRunningMean = 0.0
            ecgRunningMeanCounter = 0
            runningMeanDatapoints = []
            runningMeanMaxDatapoints = 400
            
            # For testing the Cubic Interpolation - TODO May be wrong... could possibly remove
            runningMeanDatapointsForCubicInterpolation = []
            
            previousChars = []
            
            # Remove all white space and seperate the values
            for meshedData in ecgData: # For each character in the csv data
                
                if meshedData != "\n": # If meshed data is a new line, append all previous chars to said array
                    if meshedData != "\t":
                        previousChars.append(meshedData) # Add chars to new array
                    else:
                        previousChars.append(",") # Get rid of tabs and add ',' to make CSV File
                # Add average of data to the end of the array before adding the line
                else:
                    if previousChars[0] != 's': # Stops the first line which is made up from chars from being accepted
                        averagedSignal = self.createAverageSignal("".join(previousChars))
                        
                        # for zero crossing
                        ecgMean += averagedSignal
                        ecgMeanCounter += 1
                        
                        # For zero crossings moving average experimental
                        ecgRunningMean += averagedSignal
                        ecgRunningMeanCounter += 1
                        if ecgRunningMeanCounter == runningMeanMaxDatapoints:
                            averagedPoints = [ecgRunningMean / ecgRunningMeanCounter] * runningMeanMaxDatapoints
                            runningMeanDatapoints.extend(averagedPoints)
                            runningMeanDatapointsForCubicInterpolation.append(ecgRunningMean/ecgRunningMeanCounter)
                            ecgRunningMean = 0.0
                            ecgRunningMeanCounter = 0
                        
                        previousChars.append("," + str(averagedSignal))
                        
                        # To save to the averaged signal list
                        averagedSignalData.append(averagedSignal)
                    ecgDataLines.append("".join(previousChars)) # Join list of chars into string
                    #print("Data Line")
                    #print(ecgDataLines)
                    previousChars.clear()
            
            print(str(ecgMean))
            print(str(ecgMeanCounter))
            meanOfData = ecgMean / ecgMeanCounter
            print("Mean for zero crossings = " + str(meanOfData))
            
            # Calculate Cubic Interpolation
            # Uses the running average sections previously calculated to find the moving average
            self.calculateCubicInterpolation(averagedSignalData, runningMeanDatapointsForCubicInterpolation, runningMeanDatapoints, folderLocation, fileName)
            
            # Save graph of running mean datapoints
            plt.plot(runningMeanDatapoints)
            folderToSaveTo = folderLocation +'/Graphs/Running Mean Data Points/'
        
            # Make sure directory exists to save file to
            self.saveGraph(folderToSaveTo, fileName+'.png')
            
            
            # Save graph of averaged signals with no other processing
            plt.plot(averagedSignalData)
            folderToSaveTo = folderLocation +'/Graphs/Averaged Signals Without Further Processing/'
        
            # Make sure directory exists to save file to
            self.saveGraph(folderToSaveTo, fileName+'.png')
            
            # TODO Can add this again - But need to make a new folder for it possibly
            # Function to find zero crossings on the averaged signal in the data set
            # self.findZeroCrossings(averagedSignalData, meanOfData, runningMeanDatapoints, folderLocation, fileName)
        
            # Save data to CSV
            # np.savetxt(docLocation, ecgDataLines, delimiter=",", fmt='%s')
            
    
    # Function that returns the averaged signal to append to the data
    def createAverageSignal(self, charString):
        # print('This is the char array ' + str(charString))
        total = 0.00
        ecgDataInstance = charString.split(",") # Split by the commas and retrieve data as an array to iterate through
        for x in range(1, 9): # Do not include first position in array because this data is not needed
            total += float(ecgDataInstance[x]) # Add all of the data together and cast to float
            # print(total)
        
        averagedSignal = total / 9
        # print("Averaged Signal: " + str(averagedSignal))
        
        return averagedSignal
    
    
    # Function to calculate the cubic spline interpolation of the running average sections of the signal
    def calculateCubicInterpolation(self, averagedSignalData, singularMeanOfData, runningMeanDatapoints, folderLocation, fileName):
        print("Calculating the Cubic Interpolation of the running mean sections")
        
        y = []
       
        # For the amount of data points in our code - TODO This must be changed to the lenght of meanOfData (Here and below)
        for x in range(1, len(singularMeanOfData) + 1):
            y.append(x)
        
        print(len(singularMeanOfData))
        print(len(y))
        # X is horizontal (The data point included in the mean of data)
        # Y is vertical (The mean of data that we wish to look at)
        # This returns the interpolation function which we need to make use of
        cubicInterpolatedRepresentation = interp1d(y, singularMeanOfData, 'cubic')
        
        xnew = np.arange(1, 15, 0.00233)
        ynew = cubicInterpolatedRepresentation(xnew) 
        
        print('ynew = ' + str(len(ynew)))
        print(type(ynew))
        print(str(ynew))
        plt.plot(runningMeanDatapoints, 'o', ynew, '--')
        plt.legend(['Running Average Sections', 'Cubic Interpolation Of Running Average Sections'], loc='best')
        
        folderToSaveTo = folderLocation +'/Graphs/Cubic Interpolation Paired With Running Average Sections/'
        
        # Make sure directory exists to save file to
        self.saveGraph(folderToSaveTo, fileName+'.png')
        
        #TODO CHANGE NAME OF XNEW YNEW
        plt.plot(averagedSignalData)
        plt.plot(ynew)
        #plt.plot(averagedSignalData, 'o', ynew, '--')
        #plt.legend(['Averaged Signal Data', 'Cubic Interpolation Of Running Average Sections'], loc='best')
        
        folderToSaveTo = folderLocation +'/Graphs/Cubic Interpolation Paired With Averaged Signal Data/'
        
        # Make sure directory exists to save file to
        self.saveGraph(folderToSaveTo, fileName+'.png')
        
        # Can possibly remove later on.....
        self.removeDrift(averagedSignalData, ynew, folderLocation, fileName)
        
        # Function to find zero crossings for the averaged signal of the dataset using the 
        self.findZeroCrossings(averagedSignalData, 0, ynew, folderLocation, fileName)
    
    # Function to find zero crossings in data set
    def findZeroCrossings(self, averagedEcgData, meanOfData, runningMeanDatapoints, folderLocation, fileName):
        print("Finding Zero Crossings")
        
        lastDataPoint = meanOfData
        
        dataUnder = 0
        dataOver = 0
        
        # To colour the zero crossings differently
        zeroCrossingCounter = 0
        zeroCrossingPlotArray = []
        
        for dataPoint in averagedEcgData:
            
            # TODO maybe remove this
            zeroCrossingCounter += 1
            zeroCrossingPlotArray.append(dataPoint)
            
            # If data has gone above crossing point
            if dataPoint >= runningMeanDatapoints[zeroCrossingCounter-1] and lastDataPoint < runningMeanDatapoints[zeroCrossingCounter-1]:
                dataOver += 1
                # TODO - Testing
                plt.plot(zeroCrossingPlotArray, 'b')
                zeroCrossingPlotArray.clear()
                toDoWillyWonka = [np.nan] * zeroCrossingCounter
                zeroCrossingPlotArray.extend(toDoWillyWonka)
                
            # If data has gone below crossing point    
            elif dataPoint < runningMeanDatapoints[zeroCrossingCounter-1] and lastDataPoint > runningMeanDatapoints[zeroCrossingCounter-1]:
                dataUnder += 1
                # TODO - Testing 
                plt.plot(zeroCrossingPlotArray, 'r')
                zeroCrossingPlotArray.clear()
                toDoWillyWonka = [np.nan] * zeroCrossingCounter
                zeroCrossingPlotArray.extend(toDoWillyWonka)
                
                
                
            lastDataPoint = dataPoint # Set last datapoint to this data point
        
        print('Data Over = ' + str(dataOver) + ' And Data Under = ' + str(dataUnder))
        
        # plt.plot(averagedEcgData) # Plot ecg data
        
        # Is this needed?
        y = []
       
        for x in range(1, 6001):
            y.append(x)
        
        # blah = interp1d(runningMeanDatapoints, y, kind='cubic')
        
        plt.plot(runningMeanDatapoints)
        
        # To add the mean of the data to the graph
        plt.plot(np.repeat(meanOfData, len(averagedEcgData)))
        
        folderToSaveTo = folderLocation +'/Graphs/ECG Data plotted against Moving Point Average/'
        
        # Make sure directory exists to save file to
        self.saveGraph(folderToSaveTo, fileName+'.png')
        
        #Probably remove from here and put elsewhere......
        self.calculateFft(averagedEcgData, runningMeanDatapoints, folderLocation, fileName)
        #for csvData in ecgData:
         #   print("Data = " + str(ecgData))

    
    # Calculate the FFT using the averaged ECG Data
    def calculateFft(self, averagedEcgData, runningMeanDatapoints, folderLocation, fileName):
        averageEcgFft = np.fft.fft(np.array(averagedEcgData).flatten())
        # TODO can remove this as well later possibly
        folderToSaveTo = folderLocation +'/Graphs/Averaged Signals With FFT/'
        plt.plot(averageEcgFft)
        self.saveGraph(folderToSaveTo, fileName+'.png')
        
        folderToSaveTo = folderLocation +'/Graphs/Averaged Signals With FFT FREQ/'
        # TODO - remove me. This line below is a direct copy for testing
        freq = np.fft.fftfreq(len(averagedEcgData))
        
        print('freq = ' + str(freq))
        print(len(freq))
        
        # Below block is copied from here http://scipy-lectures.org/intro/scipy/auto_examples/plot_fftpack.html
        power = np.abs(averageEcgFft)        
        pos_mask = np.where(freq > 0)
        freqs = freq[pos_mask]
        peak_freq = freqs[power[pos_mask].argmax()]
        averageEcgFft[np.abs(freq) < peak_freq] = 0
        filtered_sig = np.fft.ifft(averageEcgFft)
        plt.plot(filtered_sig)
        plt.plot(runningMeanDatapoints)
        self.saveGraph(folderToSaveTo, fileName+'.png')
        
        #plots the freq against the length
        #plt.plot(freq, np.abs(averageEcgFft))
        #self.saveGraph(folderToSaveTo, fileName+'.png')
         
    # TODO May be a load of shit - worth giving it a go
    # Function that will eliminate baseline drift of the biological ECG signal
    def removeDrift(self, averagedEcgData, runningMeanDatapoints, folderLocation, fileName):
        newData = []
        print('Length of averaged data = ' + str(len(averagedEcgData)) + '. Length of running mean datapoints' + str(len(runningMeanDatapoints)))
        counter = 0
        
        # THis line is a copy - Make it yours
        runningMeanDatapoints = runningMeanDatapoints[:len(runningMeanDatapoints)-9]
        
        print('LOLOLOL' + str(len(runningMeanDatapoints)))
        for data in runningMeanDatapoints:
            
            newData.append(averagedEcgData[counter] - self.distance(0, data))
            counter += 1
    
        plt.plot(newData)
        folderToSaveTo = folderLocation +'/Graphs/BSHDSAJHDJA/'
        self.saveGraph(folderToSaveTo, fileName+'.png')
            
    
    # TODO this is totally someone elses function. If it needs keeping then it needs to be deleted and rewritten
    def distance(self, a, b):
        if (a == b):
            return 0
        elif (a < 0) and (b < 0) or (a > 0) and (b > 0):
            if (a < b):
                return (abs(abs(a) - abs(b)))
            else:
                return -(abs(abs(a) - abs(b)))
        else:
            return math.copysign((abs(a) + abs(b)),b)
            

    # Function to make a directory in python to save the graphs to     
    def saveGraph(self, folderToSaveTo, fileName):
        try:
            os.mkdir(folderToSaveTo)
            print('The Directory: ' + folderToSaveTo + ' Has Been Created. Saving Data')
        except:
            print('The Directory: ' + folderToSaveTo + ' Already Exists. Saving Data')
        
        # Set X and Y Labels on the plot
        plt.title('Some Graph', fontsize = 20)
        plt.xlabel('Time in 600ths of a second', fontsize = 14)
        plt.ylabel('Amplitude in Mv (Millivolts)', fontsize = 14)
        
        plt.show()
        
        # Save and clear the plot
        plt.savefig(folderToSaveTo + fileName)
        plt.cla() # Clear the plot

# Call the main function
if __name__ == '__main__':
  def run_folder_selector_ui():
        print("UI Running - User can now select the folder containing their data")
        # Boiler plate code - https://github.com/spyder-ide/spyder/wiki/How-to-run-PyQt-applications-within-Spyder
        app = QtWidgets.QApplication(sys.argv)
        mainWin = createMainWindow()
        mainWin.show()
        app.exec_()
  
  # Allows for the document selector method to run
  run_folder_selector_ui()
  
  ## TODO
  # Change names from functions to methods and vice versa. Look up naming concepts
  # Write tests for the code
  # Break into seperate files if needed
  # Use correct naming constraints. Should it be  house_party or houseParty? is it the same for both methods, functions and variables?
  # Apply some sort of filter on the ECG...
  # Fix issue with UI not working correctly for the file button. Maybe add a graphic
  # Change readme to explain how to use this program compared to the other programs
  # Make output in console look neater
  # Change scale on output from matplotlib so that instead of being every 600 seconds its every second
  # Change names of graph name and x y axis on matplotlib for what they actually are (Some are in freq domain, others in mv)
  # Look into subplots
  # Make a plot for the raw data as well
  # Cubic Spline Interpolation or piecewise linear https://www.google.co.uk/search?q=piecewise+linear&client=opera&hs=9N0&source=lnms&tbm=isch&sa=X&ved=0ahUKEwifx8eq8-HhAhXFyaQKHS4tB6UQ_AUIDigB&biw=1496&bih=723
  # Add availability to when i can demonstrate my project
  # Can get rid of +'png' from all methods calling the save function and add it to the parameters of the save function
  # Write another method for finding the normal mean - Plot both the normal and the drifted one on a graph to show