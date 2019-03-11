import pandas as panda # Library to enable east use of time series data

import sys
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QMainWindow, QLabel, QGridLayout, QWidget, QSizePolicy, QVBoxLayout, QPushButton
from PyQt5.QtCore import QSize   

import pyqtgraph as pg

# For peak detection
import scipy.signal as signal

import csv

# docLocation = ""
numRecords = 0
# Create a multidimensional array for the dataset.
# TODO May be best to not have this as global?
ecgDataset = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]



# Create a multidimensional array for the individual heartbeats that we find.
# TODO May be best to not have this as global?
heartbeatArray = [[0 for x in range(2)] for y in range(2)]

# Allows for program to continue running
runProgram = True

# Defining startup statement
print("Python ECG Detection Running")
print(__name__ + '\n')

# Defining UI Methods

# Boilerplate code - https://github.com/spyder-ide/spyder/wiki/How-to-run-PyQt-applications-within-Spyder
class createMainWindow(QMainWindow):
    
    # __init__ Is the constructor method for this class.
    # The object that we are constructing is QMainWindow which is part of PyQt
    # When createMainWindow is called we are creating the window in the constructor below
    # In summary self is the QMainWindow that we create that we are setting the variables for
    def __init__(self):
        QMainWindow.__init__(self)

        self.setMinimumSize(QSize(800, 600))    
        self.setWindowTitle("Electrocardiogram Analyzer") 
        
        centralWidget = QWidget(self)          
        self.setCentralWidget(centralWidget)   
 
        gridLayout = QGridLayout(self)     
        centralWidget.setLayout(gridLayout)  
 
        title = QLabel("Electrocardiogram Analyzer", self) 
        title.setAlignment(QtCore.Qt.AlignTop)
        gridLayout.addWidget(title, 0, 0)
        
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
        
        # Settings Menu Options
        settings = self.menuBar().addMenu('Settings')
        
        self.centralwidget = QWidget(self)
        self.graphicsView = pg.PlotWidget(self.centralwidget)
        gridLayout.addWidget(self.graphicsView)
        
        # Plot the dataset
        self.graphicsView.plot(ecgDataset)
        
        pybutton = QPushButton('Plot Dataset', self)
        pybutton.resize(100,32)
        pybutton.move(360, 550)        
        pybutton.clicked.connect(self.updatePlot)
        
        # For testing. Allows for me to view the main dataset and also the peaks found next to each other
        pybutton = QPushButton('Plot Peaks Next To Dataset', self)
        pybutton.resize(100,32)
        pybutton.move(360, 600)        
        pybutton.clicked.connect(self.findQrsComplex)
        
    def updatePlot(self, graphicsView):
            
        
       # gridLayout = self.centralWidget.layout()
       # gridLayout.removeWidget(self.graphicsView)
       # gridLayout.addWidget(self.graphicsView)
       self.graphicsView.clear()
       self.graphicsView.plot(ecgDataset)
       # self.hide()
       # self.show()
       
    
    # Function to detect QRS Complex
    def findQrsComplex(self, graphicsView):
        print("bladlsajdlksajldksajkofjlksklfjlkfja")
        signalPeaks = signal.find_peaks(ecgDataset, height=0, distance=100)
        print(signalPeaks[0])
    
        peaks = list()
    
        # Get data from index where we have found a peak because find_peaks gives us the index of peaks and not the actual peaks
        for dataIndex in signalPeaks[0]:
    
            peaks.append(ecgDataset[dataIndex])
            #print(ecgDataset[dataIndex])
            
            # Append peaks to ecg dataset to be shown. If this is left as is TODO remove peaks
            ecgDataset.append(ecgDataset[dataIndex])
        
        self.graphicsView.clear()
        self.graphicsView.plot(peaks)
    
    # Function that allows for a file to be imported into the program. File information is saved and ready for data to be imported
    def importFile(self):

        # Sets filter to stop anything except CSV and JSON files
        filter = "Data Files(*.csv *.json)"
        
        # Sets window name and directory to search in
        fileInformation = QtWidgets.QFileDialog.getOpenFileName(self, 'Choose A Data File To Import', '/ecgData', filter)
        
        #Retrieve the document name from the returned string
        fileName = QtCore.QFileInfo(fileInformation[0]).fileName()
        
    
        #If fileInformation[0] is populated (This is the file itself)
        if fileInformation[0]:
            
            docLocation = fileInformation[0]
            print('Location of document')
            print(docLocation)
            print('This is the name of the document to open')
            print(fileName)
        
            # Call method to check for file type and parse   
            detectFileType(fileName, docLocation)

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
def detectFileType(fileName, docLocation):
    print("Finding file type")
    print(fileName)
    if fileName.endswith('.csv'):
        parseCsv(docLocation)

    elif fileName.endswith('.json'):
        parseJson(docLocation)

    else:
        print("File does not end with '.CSV' or '.JSON'")

# Method to parse the CSV data
def parseCsv(docLocation):
    print("Parsing CSV data to an array")
    
    file = open(docLocation, 'r')

    with file:
        ecgData = file.read()
        print('There are ' + str(sum(1 for row in ecgData)) + ' Records in the CSV data')
        print(type(ecgData))
        
    # Remove old data from array
    ecgDataset.clear()
        
    # Convert String Data Into INT - Finds Newline - https://www.quora.com/How-do-I-convert-strings-in-CSV-into-integer-in-Python
    with open(docLocation, newline = "") as fileForCsvReader:
        reader = csv.reader(fileForCsvReader)
        #Go through row by row and convert to INT
        for row in reader:
            i = float(row[0])
            # print(i)
            # print(type(i))
            ecgDataset.append(i)
            
    print(ecgDataset)

# TODO NEED TO LOOK INTO THIS FULLY
# Method to parse the JSON data
def parseJson(docLocation):
    print("Parsing JSON data to an array")

    file = open(docLocation, 'r')

    with file:
        ecgData = file.read()
        print('There are ' + str(sum(1 for row in ecgData)) + ' Records in the JSON data')
        
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
    # Find normal amplitude range for different parts

# Method to calculate the heartrate using the R Peak from the PQRST data
def calculateHeartrate():
    print("Calculating the individuals heart rate")

# TODO work out what we need to do here. Detect jogging? Or health related issues?
def classifyHeartrate():
    print("Classifying the individuals heartrate")


# Call the main function
if __name__ == '__main__':
    # main()
    def run_gui():
        print("UI Running")
        # Boiler plate code - https://github.com/spyder-ide/spyder/wiki/How-to-run-PyQt-applications-within-Spyder
        app = QtWidgets.QApplication(sys.argv)
        mainWin = createMainWindow()
        mainWin.show()
        app.exec_()
    run_gui()
    
    
        # TODO Look into CSV library in order to read CSV data - https://docs.python.org/3/library/csv.html


# Boiler plate code for pyqt - https://github.com/spyder-ide/spyder/wiki/How-to-run-PyQt-applications-within-Spyder