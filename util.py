# -*- coding: utf-8 -*-
"""
Created on Wed May  1 22:22:36 2019

@author: rocke
"""

class Util:
    
    # Function to make a directory in python to save the graphs to     
    def saveGraph(folderToSaveTo, fileName):
        try:
            os.mkdir(folderToSaveTo)
            print('The Directory: ' + folderToSaveTo + ' Has Been Created. Saving Data')
        except:
            print('The Directory: ' + folderToSaveTo + ' Already Exists. Saving Data')
        
        # Set X and Y Labels on the plot
        plt.xlabel('Time in 600ths of a second', fontsize = 14)
        plt.ylabel('Amplitude in Mv (Millivolts)', fontsize = 14)
        
        plt.show()
        
        # Save and clear the plot
        plt.savefig(folderToSaveTo + fileName)
        plt.cla() # Clear the plot
    
    
    # Method to find the individual beats 
    def findIndividualBeats(averagedEcgData, signalPeaks, folderLocation, fileName):
        
        # Array to hold the datapoints index's inbetween the peaks - Meaning the end of one beat and the start of the next
        startOfBeatArray = []
        
        # Counter for r sections iterated through
        rSectionCounter = 0
        
        # To remember the last section which we visited
        previousSection = 0
        
        # For the amount of peaks that we have, calculate midway point between peaks
        for signalLocation in signalPeaks[0]:
            # Add '0' to array because we need to start here (first peak doesnt have an obvious midpoint before it)
            if rSectionCounter == 0:
                startOfBeatArray.append(0)
                
                # Set the current section as the previous section
                previousSection = signalLocation
                # Add 1 to the counter
                rSectionCounter += 1
                
            # Find the midway point between this peak and the last peak and append to array.
            else:
                # Find difference between numbers and then divide by 2 and round up
                midwayPointDifference = int(round((signalLocation - previousSection) / 2))
                startOfBeatArray.append(signalLocation - midwayPointDifference)
                
                # if this is the last peak we can add 6000 to array because there are no obvious mid points past this location
                if rSectionCounter == len(signalPeaks[0]) - 1:
                    startOfBeatArray.append(len(averagedEcgData) - 1)
                
                # Set the current section as the previous section
                previousSection = signalLocation
                
                # Set the current section as the previous section
                previousSection = signalLocation
                # Add 1 to the counter
                rSectionCounter += 1
        
        print("This is the midway Peaks array" + str(startOfBeatArray))
        
        # Find data points at location given by the midwayPeaksArray in order to generate graph
        midRSectionValues = []
        for index in startOfBeatArray:
            midRSectionValues.append(averagedEcgData[index])
        
        plt.plot(averagedEcgData, '-', startOfBeatArray, midRSectionValues, 'o')
        plt.legend(['Averaged ECG Data - Drift Removed', 'Heart Beat Section Points'], loc='best')
        
        # Gives gaps inbetween subplots
        plt.tight_layout()
        
        folderToSaveTo = folderLocation +'/Graphs/Part 4 - Averaged ECG Data With Drift Removed Plotted With Individual Heart Beat Cuts/'
        Util.saveGraph(folderToSaveTo, fileName+'.png')
        
        return startOfBeatArray
        
    
    # Function to find zero crossings in data set
    def findZeroCrossings(averagedEcgData, meanOfData, runningMeanDatapoints, folderLocation, fileName):
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
            if dataPoint >= runningMeanDatapoints[zeroCrossingCounter-1] and lastDataPoint < runningMeanDatapoints[zeroCrossingCounter-1]:
                dataOver += 1
                # TODO - Testing
                plt.plot(zeroCrossingPlotArray, 'b')
                zeroCrossingPlotArray.clear()
                toDoWillyWonka = [np.nan] * zeroCrossingCounter
                zeroCrossingPlotArray.extend(toDoWillyWonka)
                
            # If data has gone below crossing point    
            elif dataPoint < runningMeanDatapoints[zeroCrossingCounter-1] and lastDataPoint > runningMeanDatapoints[zeroCrossingCounter-1]:
                dataUnder += 1
                # TODO - Testing 
                plt.plot(zeroCrossingPlotArray, 'r')
                zeroCrossingPlotArray.clear()
                toDoWillyWonka = [np.nan] * zeroCrossingCounter
                zeroCrossingPlotArray.extend(toDoWillyWonka)
                
                
                
            lastDataPoint = dataPoint # Set last datapoint to this data point
        
        print('Data Over = ' + str(dataOver) + ' And Data Under = ' + str(dataUnder))
        
        # plt.plot(averagedEcgData) # Plot ecg data
        
        # Is this needed?
        y = []
       
        for x in range(1, 6001):
            y.append(x)
        
        # blah = interp1d(runningMeanDatapoints, y, kind='cubic')
        
        plt.plot(runningMeanDatapoints)
        
        # To add the mean of the data to the graph
        plt.plot(np.repeat(meanOfData, len(averagedEcgData)))
        
        folderToSaveTo = folderLocation +'/Graphs/ECG Data plotted against Moving Point Average/'
        
        # Make sure directory exists to save file to
        Util.saveGraph(folderToSaveTo, fileName+'.png')
        
        #Probably remove from here and put elsewhere......
        #Fft.calculateFft(averagedEcgData, runningMeanDatapoints, folderLocation, fileName)
        #for csvData in ecgData:
         #   print("Data = " + str(ecgData))
        
     # TODO this is totally someone elses function. If it needs keeping then it needs to be deleted and rewritten
    def distance(a, b):
        if (a == b):
            return 0
        elif (a < 0) and (b < 0) or (a > 0) and (b > 0):
            if (a < b):
                return (abs(abs(a) - abs(b)))
            else:
                return -(abs(abs(a) - abs(b)))
        else:
            return math.copysign((abs(a) + abs(b)),b)
           
    # Formats and saves data to a CSV File
    def saveToCsv(dataToSave, folderToSaveTo, fileName):
        # Try to make a folder (Stops errors)
        try:
            os.mkdir(folderToSaveTo)
            print('The Directory: ' + folderToSaveTo + ' Has Been Created. Saving Data')
        except:
            print('The Directory: ' + folderToSaveTo + ' Already Exists. Saving Data')
        
        # Allow for file to be saved
        np.savetxt(folderToSaveTo + fileName, dataToSave, delimiter=",", fmt='%s')
        
    
    # TODO Explain how this only shows heart rate zones for a 25 year old (Will not work for other ages)
    # Even then its a guestimate. 
    # TODO - EXCERCISE ZONES TAKEN FROM HERE - https://commons.wikimedia.org/wiki/File:Exercise_zones.png
    # Calculates Heart Rate Zone
    def calculateHeartRateZone(heartRate):
        
        heartRateZone = ""
        
        if heartRate <= 80:
            heartRateZone = "Resting"
        elif heartRate > 80 and heartRate <= 98:
            heartRateZone = "Walking/Moving"
        elif heartRate > 98 and heartRate <= 117:
            heartRateZone = "Maintenance/Warm Up"
        elif heartRate > 117 and heartRate <= 137:
            heartRateZone = "Weight Control (Fitness/Fat Burn)"
        elif heartRate > 137 and heartRate <= 156:
            heartRateZone = "Aerobic Zone (Cardio Training/Endurance)"
        elif heartRate > 156 and heartRate <= 176:
            heartRateZone = "Anaerobic Zone"
        elif heartRate > 176 and heartRate <= 195:
            heartRateZone = "VO2 Max (Maximum Effort)"
            
        return heartRateZone
    #__init__.py