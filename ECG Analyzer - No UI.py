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
            
            # Function to find zero crossings on the averaged signal in the data set
            self.findZeroCrossings(averagedSignalData, meanOfData, runningMeanDatapoints, folderLocation, fileName)
        
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
            if dataPoint > runningMeanDatapoints[zeroCrossingCounter-1] and lastDataPoint < runningMeanDatapoints[zeroCrossingCounter-1]:
                dataOver += 1
                # TODO - Testing
                plt.plot(zeroCrossingPlotArray)
                zeroCrossingPlotArray.clear()
                toDoWillyWonka = [np.nan] * zeroCrossingCounter
                zeroCrossingPlotArray.extend(toDoWillyWonka)
                
            # If data has gone below crossing point    
            elif dataPoint < runningMeanDatapoints[zeroCrossingCounter-1] and lastDataPoint > runningMeanDatapoints[zeroCrossingCounter-1]:
                dataUnder += 1
                # TODO - Testing 
                plt.plot(zeroCrossingPlotArray)
                zeroCrossingPlotArray.clear()
                toDoWillyWonka = [np.nan] * zeroCrossingCounter
                zeroCrossingPlotArray.extend(toDoWillyWonka)
                
                
                
            lastDataPoint = dataPoint # Set last datapoint to this data point
        
        print('Data Over = ' + str(dataOver) + ' And Data Under = ' + str(dataUnder))
        
        # plt.plot(averagedEcgData) # Plot ecg data
        
        y = []
       
        for x in range(1, 6001):
            y.append(x)
        
        # blah = interp1d(runningMeanDatapoints, y, kind='cubic')
        
        plt.plot(runningMeanDatapoints)
        
        # To add the mean of the data to the graph
        plt.plot(np.repeat(meanOfData, len(averagedEcgData)))
        
        folderToSaveTo = folderLocation +'/automatedGraphs/'
        
        # Make sure directory exists to save file to
        self.saveGraph(folderToSaveTo, fileName+'.png')
        
        #for csvData in ecgData:
         #   print("Data = " + str(ecgData))
         
    # Function to make a directory in python to save the graphs to     
    def saveGraph(self, folderToSaveTo, fileName):
        try:
            os.mkdir(folderToSaveTo)
            print('The Directory: ' + folderToSaveTo + ' Has Been Created. Saving Data')
        except:
            print('The Directory: ' + folderToSaveTo + ' Already Exists. Saving Data')
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