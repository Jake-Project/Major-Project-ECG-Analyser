# ECG Analyzer

This project is written using Python 3.7 and Spyder.

## Premise
As the final Capstone for my Bachelors at Aberystwyth University I am researching Electrocardiograms and studying heart rates.

## Data Aquisition
Data was recorded on the Welch Allyn CardioPerfect Electrocardiograph at 600hz
The data was then exported as a .scp file and imported into the ECG Toolkit 2.4 software.
The data was finally exported as a CSV file that this program can read.

## Code
In total, there are 3 files:
	ECG Analyzer Main
	Signal Processing
	Average Leads

### CSV Formatter for ECG Toolkit 2.4
To gather the ECG data I have been using Welch Allyn hardware and software. Unfortunately the Welch Allyn software cannot export a data type that can be utilized.
I downloaded ECG Toolkit 2.4 which allows for .SCP data to be read and can export a .CSV File
The file that the ECG Toolkit 2.4 exports only has one collumn and the data is formatted incorrectly and needs to be sanitised.

#### Currently Implemented:
1. User can quit the application using the X, File -> Quit, CNTL + W
2. User can open files using File -> Open, CTRL + O -> Browse File
3. Application automatically scans the file and saves over the original file with the newly sanitised data

#### Needs Implementing:
TODO

#### After the data has been exported:
1. open the CSV Formatter for ECG Toolkit 2.4 Python program.
2. Load the CSV File created by the ECG Toolkit 2.4 program.
3. Check the .CSV file. It should now be formatted correctly

The program saves the file to the original file which you use and overwrites this file and all of the data with sanitised data.

### ECG Analyser
This program allows the user to load in sanitised ECG data to view information about the signal.

#### Currently Implemented:
1. Shows Heart Rate in console
2. Shows ECG Signal data in application window
3.
4. User can quit the application using the X, File -> Quit, CNTL + W
5. User can open files using File -> Open, CTRL + O

#### Needs Implementing:
1. Code broken down into multiple classes
2. Better detection for peaks
3. Calculate Heart Rate Zones
4. Show Heart Rate Zones and Heart Rate to user
5. Make Applicaiton look better
6. Attempt to break down PQRST Wave in more detail

#### To get Spyder to show the ECG Analyser software:
1. Open Anaconda Prompt
2. Type "conda install pyqtgraph" - Installs pyqtgraph which is needed
3. If Spyder is already open, restart it

### Libraries Used
- [x] User Interface
  - [x] PyQtGraphs for Graphs and Charts
  - [x] PyQt For Main User Interface
- [x] Backend 
  - [Scypy.signal] For user detecting peaks
