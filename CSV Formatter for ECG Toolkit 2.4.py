# -*- coding: utf-8 -*-
"""
Created on Mon Mar 11 21:23:59 2019

@author: rocke
"""

# File that was created in order to process the ECG data from the Welch Allyn System.
# Data aquisition Flow:
#   Welch Allyn -> Export To SCP -> Import to ECG Toolkit 2.4 -> 
#   Export As CSV -> Utilize this program to properly format CSV

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QMainWindow, QLabel, QGridLayout, QWidget, QSizePolicy, QVBoxLayout, QPushButton
from PyQt5.QtCore import QSize 

import sys
import csv
import numpy as np


ecgDataset = []
    

# Boilerplate code - https://github.com/spyder-ide/spyder/wiki/How-to-run-PyQt-applications-within-Spyder
class createMainWindow(QMainWindow):
    
    # __init__ Is the constructor method for this class.
    # The object that we are constructing is QMainWindow which is part of PyQt
    # When createMainWindow is called we are creating the window in the constructor below
    # In summary self is the QMainWindow that we create that we are setting the variables for
    def __init__(self):
        QMainWindow.__init__(self)

        self.setMinimumSize(QSize(800, 600))    
        self.setWindowTitle("ECG CSV Formatter for ECG Toolkit 2.4") 
        
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
        actionOpen.triggered.connect(self.importFile)
        # actionOpen = Action performed when button is pressed.
        # .triggered.connect causes the action to be performed
    
    # Function that allows for a file to be imported into the program. File information is saved and ready for data to be imported
    def importFile(self):

        # Sets filter to stop anything except CSV and JSON files
        filter = "Data Files(*.csv)"
        
        # Sets window name and directory to search in
        fileInformation = QtWidgets.QFileDialog.getOpenFileName(self, 'Choose A CSV file to format', '/ecgData', filter)
        
        #Retrieve the document name from the returned string
        fileName = QtCore.QFileInfo(fileInformation[0]).fileName()
        
    
        #If fileInformation[0] is populated (This is the file itself)
        if fileInformation[0]:
            
            docLocation = fileInformation[0]
            print('Location of document')
            print(docLocation)
            print('This is the name of the document to open')
            print(fileName)
        
            self.parseCsv(docLocation)
            
    # Method to parse the CSV data
    def parseCsv(self, docLocation):
        print("Parsing CSV data to an array")
        
        # Remove old data from array
        ecgDataset.clear()
    
        file = open(docLocation, 'r')

        # Read in the data
        with file:
            ecgData = file.read()
            print('There are ' + str(sum(1 for row in ecgData)) + ' Records in the CSV data')
            print(type(ecgData))
            print(ecgData)
            ecgDataLines = [] # To hold different lines because data comes as long string
            
            
            previousChars = []
            
            # Remove all white space and seperate the values
            for meshedData in ecgData: # For each character in the csv data
                
                if meshedData != "\n": # If meshed data is a new line, append all previous chars to said array
                    if meshedData != "\t":
                        previousChars.append(meshedData) # Add chars to new array
                    else:
                        previousChars.append(",")
                else:
                    ecgDataLines.append("".join(previousChars)) # Join list of chars into string
                    #print("Data Line")
                    #print(ecgDataLines)
                    previousChars.clear()
          
            #Save data to CSV
            np.savetxt(docLocation, ecgDataLines, delimiter=",", fmt='%s')
           

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