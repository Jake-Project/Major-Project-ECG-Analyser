# ECG Analyzer

This project is written using Python 3.7 and Spyder.

## Premise
As the final Capstone for my Bachelors at Aberystwyth University I am researching Electrocardiograms and studying heart rates.

## Data Aquisition
Talk about Welch Allyn - 600hz

## Programs and Code
There are 2 programs that I created during this project. The first program allows CSV data to be sanitised in order to be used for heart rate analysis.

### CSV Formatter for ECG Toolkit 2.4
To gather the ECG data I have been using Welch Allyn hardware and software. Unfortunately the Welch Allyn software cannot export a data type that can be utilized.
I downloaded ECG Toolkit 2.4 which allows for .SCP data to be read and can export a .CSV File
The file that the ECG Toolkit 2.4 exports only has one collumn and the data is formatted incorrectly and needs to be sanitised.

After the data has been exported:
1. open the CSV Formatter for ECG Toolkit 2.4 Python program.
2. Load the CSV File created by the ECG Toolkit 2.4 program.
3. Check the .CSV file. It should now be formatted correctly

The program saves the file to the original file which you use and overwrites this file and all of the data with sanitised data.


### Libraries Used
- [ ] User Interface
  - [ ] MatPlotLib for Graphs and Charts
  - [ ] PyQt For Main User Interface
- [ ] Backend 
  - [ ] ...
  - [ ] ...
