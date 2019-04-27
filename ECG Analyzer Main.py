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
from signalProcessing import PeakDetection
from signalProcessing import Fft
from signalProcessing import Util



import os # Needed for folders
import sys
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
        
        fileName = fileName.replace(".csv", "") # Removes the .csv part
        
        # Read in the data
        with file:
            ecgData = file.read()
            print('There are ' + str(sum(1 for row in ecgData)) + ' Records in the CSV data')
            
            rawDataLines = [] # To hold all of the data for all 8 leads
            averagedSignalData = [] # To hold only the data for the averaged signal
            
            previousChars = []
            
            # This for loop Removes all white space from the data and seperate the values
            # The average signal data is also created
            for meshedData in ecgData: # For each character in the csv data
                
                # If CSV data isn't a new line check if it is a tab
                if meshedData != "\n": 
                    # If CSV data is a tab, add to array
                    if meshedData != "\t":
                        previousChars.append(meshedData) # Add chars to new array
                    else:
                        previousChars.append(",") # Get rid of tabs and add ',' to make CSV File
                
                # Add average of data to the end of the array before adding the line
                else:
                    # Stops the first line which is made up from chars from being accepted (samplenr is first thing in data when exported as csv)
                    if previousChars[0] != 's': 
                        
                        # create the averaged signal from the other 8 leads for this row of data
                        averagedSignal = AverageEcgLeads.createAveragedSignal("".join(previousChars))

        
                        # TODO WHAT DOES THIS DO
                        previousChars.append("," + str(averagedSignal))
                        
                        # To save to the averaged signal list
                        averagedSignalData.append(averagedSignal)
                        
                    rawDataLines.append("".join(previousChars)) # Join list of chars into string
                    #print("Data Line")
                    #print(rawDataLines)
                    previousChars.clear()

            # The overall mean of the data without any more processing
            meanOfData = AverageEcgLeads.calculateMeanOfData(averagedSignalData)
            
            # The running mean datapoints which are needed for cubic interpolation.
            runningMeanDatapoints = AverageEcgLeads.calculateRunningMean(averagedSignalData, 400)
            
            # Calculate Cubic Interpolation
            # Uses the running average sections previously calculated to find the moving average
            cubiclyInterpolatedDatapoints = AverageEcgLeads.calculateCubicInterpolation(averagedSignalData, runningMeanDatapoints, folderLocation, fileName)
            
            # Removes the drift from the averaged signal, which makes the data uniform
            averagedEcgDriftRemoved = AverageEcgLeads.removeDrift(averagedSignalData, cubiclyInterpolatedDatapoints, meanOfData, folderLocation, fileName)
            
            # TODO POSSIBLY REMOVE
            # IF THIS WORKS (THEN GREAT) BUT IF IT DOESNT, TAKE THE RUNNINGMEANMAX VARIABLE AND PUT IT BACK TO 400 IN SIGNAL PROCESSING. IF THIS DOES WORK WE WILL NEED CUBIC INTERPOLATION TO FILL IN GAPS
            averagedEcgDriftRemoved = AverageEcgLeads.calculateRunningMean(averagedEcgDriftRemoved, runningMeanMaxDatapoints = 10)
            averagedEcgDriftRemoved = AverageEcgLeads.calculateCubicInterpolationNumberTwo(averagedEcgDriftRemoved, averagedEcgDriftRemoved, folderLocation, fileName)
            
            # To calculate the individual frequencies in the signal and remove frequencies that arent viable
            Fft.calculateFft(averagedEcgDriftRemoved, runningMeanDatapoints, folderLocation, fileName)
            
            # Finds the R-Peaks in the signal
            rPeaks = PeakDetection.findQrsComplex(averagedEcgDriftRemoved, folderLocation, fileName)
            
            # To find individual beats
            startEndOfBeats = Util.findIndividualBeats(averagedEcgDriftRemoved, rPeaks, folderLocation, fileName)
            
            # To try and find the P and T Peaks within the individual beats
            PeakDetection.findPeaks(averagedEcgDriftRemoved, startEndOfBeats, folderLocation, fileName)
            
            # TODO Can add this again - But need to make a new folder for it possibly
            # Function to find zero crossings on the averaged signal in the data set
            # QrsDetection.findZeroCrossings(averagedSignalData, meanOfData, runningMeanDatapoints, folderLocation, fileName)
            
            
            # Save data to CSV
            # np.savetxt(docLocation, rawDataLines, delimiter=",", fmt='%s')
  
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