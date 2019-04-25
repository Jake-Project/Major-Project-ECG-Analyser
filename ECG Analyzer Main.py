# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 17:39:52 2019

@author: rocke
"""

# File that was created in order to process the ECG data from the Welch Allyn System.
# Data aquisition Flow:
#   Welch Allyn -> Export To SCP -> Import to ECG Toolkit 2.4 -> 
#   Export As CSV -> Utilize this program to analyze CSV

# Code flow:
#   User opens this program initially.
#   This program calls the signalProcessing file and its multiple classes
#   Each class in signalProcessing deals with a different aspect of the signal

# For the User Interface
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QMainWindow, QLabel, QGridLayout, QWidget, QSizePolicy, QVBoxLayout, QPushButton
from PyQt5.QtCore import QSize 

# To plot Graphs of data
import matplotlib.pyplot as plt

from signalProcessing import AverageEcgLeads
from signalProcessing import QrsDetection



import os # Needed for folders
import sys
import csv
import numpy as np


# Boilerplate code - https://github.com/spyder-ide/spyder/wiki/How-to-run-PyQt-applications-within-Spyder
class createMainWindow(QMainWindow):
    
    # __init__ Is the constructor method for this class.
    # The object that we are constructing is QMainWindow which is part of PyQt.
    # When createMainWindow is called we are creating the window in the 
    # constructor below.
    # In summary self is the QMainWindow that we create that we are setting 
    # the variables for.
    def __init__(self):
        QMainWindow.__init__(self)

        self.setMinimumSize(QSize(800, 600))    
        self.setWindowTitle(
                "Please select a window containing all of the data you want "
                "to test in CSV format") 
        
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
        # .triggered.connect causes the action to be performed.
        
        
        
        
    # Function that allows for files to be imported into the program.
    # The user chooses a folder. The CSV Files in this folder are then 
    # imported into the program.
    # This calls the parseCsv function that takes the CSV data and turns it 
    # into a standard that allows for the data to be processed.
    def importFiles(self):
        
        # Sets window name and directory to search in
        # Allows user to choose a directory containing ecg data
        folderInformation = QtWidgets.QFileDialog.getExistingDirectory(
                self, "Choose a folder which you want to test the data for", 
                r'C:\Users\rocke\Sandbox\ECG\Major-Project-ECG-Analyser\Data', 
                QtWidgets.QFileDialog.ShowDirsOnly)
        
        #If folderInformation[0] is populated, user has selected a folder with files
        if folderInformation[0]:
            
            # Gets all files which are found in the location which the user selected
            for file in os.listdir(folderInformation):
                # Only allows files ending with .csv
                if file.endswith(".csv"):
                    # Prints the files that have been found to the user
                    print("\nFile to open: " + str(folderInformation + '/' + file)) 

                    # Calls the parseCsv method which takes this instance of the file to iterate through.
                    self.processSignals(folderInformation, file)
            
            
            
            
    # Method to parse the CSV data so that it can be used. 
    # Takes the data and calls methods on the data in order to produce graphs
    # Takes the location of the folder which the data is stored as well as the 
    # name of the file which we are currently reading
    def processSignals(self, folderLocation, fileName):
        print("Parsing CSV data to an array")
        # Opens the folderLocation and fileName to read.
        file = open(folderLocation + '/' + fileName, 'r')

        # Read in the data
        with file:
            ecgData = file.read()
            print('There are ' + str(sum(1 for row in ecgData)) + ' Records in the CSV data')
            
            ecgDataLines = [] # To hold all of the data for all 8 leads including the averaged signal
            averagedSignalData = [] # To hold only the data for the averaged signal
            
            # for calculating the total mean of the data
            ecgMean = 0.0
            ecgMeanCounter = 0
            
            # TODO Change variable names if they make no sense - Also this isnt a test anymore
            # Test for zero crossings - Uses rolling average
            ecgRunningMean = 0.0
            ecgRunningMeanCounter = 0
            runningMeanDatapoints = []
            runningMeanMaxDatapoints = 400
            
            # For testing the Cubic Interpolation - TODO May be wrong... could possibly remove
            runningMeanDatapointsForCubicInterpolation = []
            
            previousChars = []
            
            # Remove all white space from the data and seperate the values
            for meshedData in ecgData: # For each character in the csv data
                
                # If CSV data is a new line check if it is a tab
                if meshedData != "\n": 
                    # If CSV data is a tab, add to array
                    if meshedData != "\t":
                        previousChars.append(meshedData) # Add chars to new array
                    else:
                        previousChars.append(",") # Get rid of tabs and add ',' to make CSV File
                
                # Add average of data to the end of the array before adding the line
                else:
                    # Stops the first line which is made up from chars from being accepted
                    if previousChars[0] != 's': 
                        # create the averaged signal from the other 8 leads
                        averagedSignal = AverageEcgLeads.createAveragedSignal("".join(previousChars))

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
            cubiclyInterpolatedDatapoints = AverageEcgLeads.calculateCubicInterpolation(averagedSignalData, runningMeanDatapointsForCubicInterpolation, runningMeanDatapoints, folderLocation, fileName)
            
            # Removes the drift from the averaged signal, which makes the data uniform
            AverageEcgLeads.removeDrift(averagedSignalData, cubiclyInterpolatedDatapoints, folderLocation, fileName)
            
            
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


# Call the main function
if __name__ == '__main__':
  def run_gui():
        print("UI Running")
        # Boiler plate code - https://github.com/spyder-ide/spyder/wiki/How-to-run-PyQt-applications-within-Spyder
        app = QtWidgets.QApplication(sys.argv)
        mainWin = createMainWindow()
        mainWin.show()
        app.exec_()
  run_gui()