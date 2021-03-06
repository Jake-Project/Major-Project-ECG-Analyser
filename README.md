# ECG Analyzer
This project is written using Python 3.7 and Spyder.

## Premise
As the final Capstone for my Bachelors at Aberystwyth University I researched Electrocardiograms and studyied the classification of PQRST-Waves. 

The software is comprised of a simple UI that allows the user to open a folder containing CSV files containing ECG data. These files must have followed the process outline in the Data Aquisition portion of this README.
The files are fed through a series of processes that remove the three main types of noise from the signal - Electromyographic Noise (noise caused by the muscles), Baseline Drift and Electromagnetic Noise caused by the ECG Electrodes and leads.

The PQRST-Waves are then calculated using peak and valley detection. Graphs are created throughout this process to illustrate the process.
After the PQRST-Waves have been extracted, the heartrate and heartrate zone can be identified.
The PQRST-Wave points are saved to a CSV file that could potentially used for medical diagnosis

![The Final Output Signal](https://github.com/Jake-Project/Major-Project-ECG-Analyser/blob/Feature-10---Code-Cleanup/Data/Jake%20ECG%20CSV%20Data%20Raw%20From%20ECG%20Toolkit%202.4/Graphs/Part%2011%20-%20PQRST%20Sections%20Plotted%20Against%20Processed%20Averaged%20ECG%20Signal/Jake%20Newall%20Laying%20Down%20-%204.png)

## Data Aquisition
Data was recorded on the Welch Allyn CardioPerfect Electrocardiograph at 600hz using a 10 lead setup
The data was then exported as a .scp file and imported into the ECG Toolkit 2.4 software.
The data was finally exported as a CSV file that this program can read.
The program takes the 8 leads which are exported from the CardioPerfect software and averages them to 1.

## Files
In total, there are 3 files which are to be used:
	ECG Analyzer Main
	Signal Processing
	Average Leads

#### Currently Implemented:
1. User can quit the application: File -> Quit/CNTL + W
2. User can open folders containing CSV Files: (File -> Open/CTRL + O) -> Browse Folders
3. Application takes the CSV data, sanitizes the data and outputs the sanitized data to a new file in a subfolder
4. PQRST-Waves are calculated and saved to a new file in a subfolder
5. The heartrate and heartrate zone is calculated and saved to a new file in a subfolder
6. Graphs are created throughout the process of calculating the PQRST-Waves to illustrate the steps and are saved to a new file in a subfolder

#### Needs Implementing:
The project was completed and handed into the University on the 3rd of May 2019

### Data Aquisition and CSV Formatter for ECG Toolkit 2.4
To gather the ECG data I have been using Welch Allyn hardware and software. Unfortunately the Welch Allyn software cannot export a data type that can be utilized.
I downloaded ECG Toolkit 2.4 which allows for .SCP data to be read and can export a .CSV File
The file that the ECG Toolkit 2.4 exports only has one collumn and the data is formatted incorrectly and needs to be sanitised the CSV data is sanitised by this software and saved in the correct format into a new subfolder.

#### PyQt5 Dependency:
1. Open Anaconda Prompt
2. Type "conda install pyqtgraph" - Installs pyqtgraph which is needed
3. If Spyder is already open, restart it

### Libraries Used
- [x] User Interface
 - [x] PyQt For Main User Interface
- [x] Backend 
  - [Scypy.signal] For user detecting peaks
