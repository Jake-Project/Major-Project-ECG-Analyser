# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 17:39:52 2019
@author: Jake Newall


The Main python file that was created in order to process the ECG data from the Welch Allyn System.
Data aquisition Flow:
  Welch Allyn -> Export To SCP -> Import to ECG Toolkit 2.4 -> 
  Export As CSV -> Utilize this program to analyze CSV
  
# Code flow:
#   User opens this program initially.
#   This program calls the signalProcessing.py and averageLeads.py files and their multiple classes
#   Each class in signalProcessing.py and averageLeads.py deals with a different aspect of the signal
"""

# For the User Interface
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QMainWindow, QLabel, QGridLayout, QWidget, QSizePolicy, QVBoxLayout, QPushButton
from PyQt5.QtCore import QSize 

from averageLeads import SingleSignal 
from signalProcessing import PeakValleyDetection
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
        self.setWindowTitle("ECG Analyzer")
        
        central_widget = QWidget(self)          
        self.setCentralWidget(central_widget)   
 
        grid_layout = QGridLayout(self)     
        central_widget.setLayout(grid_layout)  
        
        # Create textbox and set paragraph
        paragraph = QLabel()
        paragraph.setText("Welcome to ECG Analyzer! \nPress 'Cntrl + O' or 'File -> Open' to search for a folder containing ECG data." +
                          "\nPress 'Cntrl + W', 'Cntrl + Q' or 'File -> Quit' to quit the software. " +
                          "\n\n1. Select a folder containing ECG data in CSV format which has been exported from" +
                          " ECG Toolkit 2.4." +
                          "\n2. Open the folder" +
                          "\n3. The software will iterate through the files inside of this folder and save graphs" +
                          " showing the different processes that the ECG data is going through. \n4. These graphs will" +
                          " be saved inside of folder called 'Graphs' where the original data is located." +
                          "\n5. Another folder will also be generated called 'Results' which contains the" +
                          " individual PQRST sections along with the Heartrate and Excercise zone found from the data" +
                          "\n6. Finally, another folder will be created called 'CSV Formatted' which contains the " +
                          "original CSV data and the averaged data but formatted correctly")
        grid_layout.addWidget(paragraph, 0, 0)
        
        # File Menu options
        file = self.menuBar().addMenu('File')
        action_quit = file.addAction('Quit')
        action_quit.setShortcut('Ctrl+Q')
        action_quit.setShortcut('Ctrl+W')
        action_quit.triggered.connect(QtWidgets.QApplication.quit)
        
        action_open = file.addAction('Open File')
        action_open.setShortcut('Ctrl+O')
        action_open.setStatusTip('Import File')
        action_open.triggered.connect(self.importFiles)
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
        folder_information = QtWidgets.QFileDialog.getExistingDirectory(
                self, "Choose a folder which you want to test the data for", 
                r'C:\Users\rocke\Sandbox\ECG\Major-Project-ECG-Analyser\Data', 
                QtWidgets.QFileDialog.ShowDirsOnly)
        
        #If folderInformation[0] is populated, user has selected a folder with files
        if folder_information[0]:
            
            # Gets all files which are found in the location which the user selected
            for file in os.listdir(folder_information):
                # Only allows files ending with .csv
                if file.endswith(".csv"):
                    # Prints the files that have been found to the user
                    print("\nFile to open: " + str(folder_information + '/' + file)) 

                    # Calls the parseCsv method which takes this instance of the file to iterate through.
                    self.processCsvData(folder_information, file)
            
            
            
            
    # Method to parse the CSV data so that it can be used. 
    # Takes the data and calls methods on the data in order to produce graphs
    # Takes the location of the folder which the data is stored as well as the 
    # name of the file which we are currently reading
    def processCsvData(self, folder_location, file_name):
        # Make initial folders (Graphs, Results and CSV Formatted)
        Util.createMainFolders(folder_location)
        
        print("Parsing CSV data to an array")
        # Opens the folderLocation and fileName to read.
        file = open(folder_location + '/' + file_name, 'r')
        
        file_name = file_name.replace(".csv", "") # Removes the .csv part
        
        # Read in the data
        with file:
            ecg_data = file.read()
            print('There are ' + str(sum(1 for row in ecg_data)) + ' Records in the CSV data')
            
            raw_data_lines = [] # To hold all of the data for all 8 leads
            averaged_signal_data = [] # To hold only the data for the averaged signal
            
            previous_chars = []
            
            # This for loop Removes all tabs from the data and seperates the values
            # The average signal data is also created
            for meshed_data in ecg_data: # For each character in the csv data
                
                # If CSV data isn't a new line check if it is a tab
                if meshed_data != "\n": 
                    # If CSV data is a tab, add to array
                    if meshed_data != "\t":
                        previous_chars.append(meshed_data) # Add chars to new array
                    else:
                        previous_chars.append(",") # Get rid of tabs and add ',' to make CSV File
                
                # Add average of data to the end of the array before adding the line
                else:
                    # Stops the first line which is made up from chars from being accepted 
                    # (samplenr is first thing in data when exported as csv)
                    if previous_chars[0] != 's': 
                        
                        # create the averaged signal from the other 8 leads for this row of data
                        averaged_signal = SingleSignal.createAveragedSignal("".join(previous_chars))

        
                        # TODO WHAT DOES THIS DO
                        previous_chars.append("," + str(averaged_signal))
                        
                        # To save to the averaged signal list
                        averaged_signal_data.append(averaged_signal)
                        
                    raw_data_lines.append("".join(previous_chars)) # Join list of chars into string
                    #print("Data Line")
                    #print(rawDataLines)
                    previous_chars.clear()
                    
            # Save the formatted CSV incuding the averaged data out to a file for easier readability
            Util.saveToCsv(raw_data_lines, folder_location + "/CSV Formatted/", file_name + " Formatted")

            # The overall mean of the data without any more processing
            mean_of_data = Util.calculateMeanOfData(averaged_signal_data)
            
            # The running mean datapoints which are needed for cubic interpolation.
            running_mean_datapoints = SingleSignal.calculateRunningMean(averaged_signal_data, 400)
            
            # Calculate Cubic Interpolation
            # Uses the running average sections previously calculated to find the moving average
            cubicly_interpolated_datapoints = SingleSignal.calculateInterpolation(averaged_signal_data, 
                                                                                  running_mean_datapoints, 
                                                                                  'cubic', folder_location, 
                                                                                  file_name)
            
            # Removes the drift from the averaged signal, which makes the data uniform
            averaged_ecg_drift_removed = SingleSignal.removeDrift(averaged_signal_data, 
                                                                  cubicly_interpolated_datapoints, 
                                                                  mean_of_data, folder_location, file_name)
            
            # TODO POSSIBLY REMOVE (running mean max datapoints = 10?)
            # IF THIS WORKS (THEN GREAT) BUT IF IT DOESNT, TAKE THE RUNNINGMEANMAX VARIABLE AND PUT IT 
            # BACK TO 400 IN SIGNAL PROCESSING. IF THIS DOES WORK WE WILL NEED CUBIC INTERPOLATION TO FILL IN GAPS
            averaged_ecg_drift_removed = SingleSignal.calculateRunningMean(averaged_ecg_drift_removed, 
                                                                           running_mean_max_datapoints = 10)
            averaged_ecg_drift_removed = SingleSignal.calculateInterpolation(averaged_ecg_drift_removed, 
                                                                             averaged_ecg_drift_removed, 
                                                                             'linear', folder_location, 
                                                                             file_name)
            
            # TODO - Doesnt return anything???
            # To calculate the individual frequencies in the signal and remove frequencies that arent viable
            Fft.calculateFft(averaged_ecg_drift_removed, running_mean_datapoints, folder_location, file_name)
            
            #TODO rename this to something based on r and not qrs. 
            # Finds the R-Peaks in the signal
            r_peaks = PeakValleyDetection.findQrsComplex(averaged_ecg_drift_removed, folder_location, file_name)
            
            # To find individual beats
            start_end_of_beats = Util.findIndividualBeats(averaged_ecg_drift_removed, r_peaks, folder_location, file_name)
            
            # To try and find the P and T Peaks within the individual beats
            PeakValleyDetection.findPeaks(averaged_ecg_drift_removed, start_end_of_beats, folder_location, file_name)
            
            # TODO Can add this again - But need to make a new folder for it possibly
            # Function to find zero crossings on the averaged signal in the data set
            # QrsDetection.findZeroCrossings(averaged_signal_data, mean_of_data, running_mean_datapoints, folder_location, file_name)
            
            
        # TODO where should i used this function?
        # Function to find zero crossings for the averaged signal of the dataset using the 
        #Util.findZeroCrossings(averaged_signal_data, 0, y_new, folder_location, file_name)
        
  
  # Call the main function
if __name__ == '__main__':
  def run_folder_selector_ui():
        print("UI Running - User can now select the folder containing their data")
        # Boiler plate code - https://github.com/spyder-ide/spyder/wiki/How-to-run-PyQt-applications-within-Spyder
        app = QtWidgets.QApplication(sys.argv)
        main_win = createMainWindow()
        main_win.show()
        app.exec_()
  
  # Allows for the document selector method to run
  run_folder_selector_ui()
      
  # DONE
     # Average leads file is clean. 
     
     
   ## TODO- Delete this list
   # Make sure all errors are resolved
   # Make sure all graph folders numbers are correct and graphs are named properly
     # Change names of graph name, legend and x y axis on matplotlib for what they actually are (Some are in freq domain, others in mv)
   # Check for TODOS and swears
   # signalProcessing.py is a mess - clean it
   # Change readme to explain how to use this program compared to the other programs
   # Search for question marks
   # Make sure code is in right order for how it is called

  # Find rough amount of time that pqrst sections should last for dependant on heart rate and calculate this
  # Write tests for the code