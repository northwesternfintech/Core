import logging
import csv
from datetime import datetime
import os

class LoggingClass:
    def __init__(self,logDir):
        self.status = 0
        if os.path.isdir(logDir):
            self.logDirPath = logDir
        else:
            status = 1
         
    def generateLogFilePath(self, error=False):
        """
        Generates the abs path for the log file using the ISO timestamp of the current day appended onto the particular log dir. The error variable indicates which log dir must be employed - error or data. 
        """
        absPath = ""
        isoString = datetime.now().strftime('%Y-%m-%d')
        if error:
            absPath = self.logDirPath + "errorLogs/" + isoString
        else:
            absPath = self.logDirPath + "orderLogs/" + isoString
        return absPath

    def errorLog(self, message):
        """
        Logs any user error to the errorLogs folder
        """
        try:
            errorFilePath = self.generateLogFilePath(True)
            logging.basicConfig(filename=errorFilePath, filemode='w+', format='%(message)', level=logging.ERROR)
            logging.error(message)
            return 0
        except Exception as e:
            return 1
    
    def orderLog(self, orderStructure):
        """
        Logs the order object into the csv dir
        """
        try:
            orderLogPath = self.generateLogFilePath()
            file_exists = os.path.isfile(orderLogPath)
            with open("test.csv", 'w+', encoding='UTF8', newline='') as fhand:
                writer = csv.DictWriter(fhand, fieldnames=orderStructure.keys())
                if not file_exists:
                    writer.writeheader()
                writer.writerow(orderStructure)
            return 0

        except Exception as e:
            return 1