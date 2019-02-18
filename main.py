import pandas as panda # Library to enable east use of time series data
import matplotlib.pyplot as matplot # Library to enable us to see graphs and charts

import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QLabel, QGridLayout, QWidget
from PyQt5.QtCore import QSize   

docLocation = ""
numRecords = 0
# Create a multidimensional array for the dataset.
# TODO May be best to not have this as global?
ecgDataset = [[0 for x in range(2)] for y in range(2)]

# Create a multidimensional array for the individual heartbeats that we find.
# TODO May be best to not have this as global?
heartbeatArray = [[0 for x in range(2)] for y in range(2)]

# Allows for program to continue running
runProgram = True

# Defining startup statement
print("Python ECG Detection Running")
print(__name__ + '\n')

# Defining the functions that we will be utilising

# Main Method that will call the rest of the code. The GUI will work with the main function to show user input to the user
def main():
    print("In main method")
    # While loop to keep the program running
    while runProgram == True:
    
        # If the document to test had been specified
        if docLocation != "":
            print("User has chosen document. Accessing data")

            while runProgram == True:
                detectFileType()
        
        # If no document has been specified
        elif docLocation == "":
            print("User needs to select document")
        

            # TODO GUI Stuff to change runProgram to false

# Method that looks for the filetype of the document that we are passing into the program so that we can correctly parse the data
def detectFileType():
    print("Finding file type")
    if docLocation.endswith('.CSV'):
        parseCsv()

    elif docLocation.endswith('.JSON'):
        parseJson()

    else:
        print("File does not end with '.CSV' or '.JSON'")

# Method to parse the CSV data
def parseCsv():
    print("Parsing CSV data to an array")

    # TODO Look into CSV library in order to read CSV data - https://docs.python.org/3/library/csv.html

# Method to parse the JSON data
def parseJson():
    print("Parsing JSON data to an array")

    # TODO Look into JSON library in order to read JSON data - https://docs.python.org/3/library/json.html

# Method to iterate through all of the data and pass data in sections to the detectSingleBeat method
# TODO - Is this needed or not? Would it not be better to detect each beat as we are iterating through the data?
def iterateThroughData():
    print("Iterating through the data")

# Method to allow us to segment the time series by each heartbeat for further analysis
def detectSingleBeat():
    print("Finding individual heart beats")

# Method to calculate the PQRST sections of the heart beat
def findPqrstSections():
    print("Splitting individual heart beats by the individual sections: P Q R S T ")

# Method to calculate the heartrate using the R Peak from the PQRST data
def calculateHeartrate():
    print("Calculating the individuals heart rate")

# TODO work out what we need to do here. Detect jogging? Or health related issues?
def classifyHeartrate():
    print("Classifying the individuals heartrate")


# Call the main function
if __name__ == '__main__':
    main()
    def run_gui():
        
    run_gui()

# Boiler plate code for pyqt - https://github.com/spyder-ide/spyder/wiki/How-to-run-PyQt-applications-within-Spyder