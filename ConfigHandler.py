import sys
import configparser

# ------------------------------------------------------------------------------
# User handler, adds users to the list and stores them persistent
class ConfigHandler:

    def __init__(self, configFileName, debugLogger = []):
        self.m_configFileName = configFileName
        self.m_debugLogger = debugLogger
        self.m_config = []
        self.__readFile()


    def optionFileFound(self):
        for section in self.m_config.sections():
            if 'DoorConfig' == section:
                return True
        return False

    def getOption(self, optionName):
        return self.m_config['DoorConfig'][optionName]


    def getOptionBool(self, optionName):
        opt = self.m_config['DoorConfig'][optionName]
        return opt == 'True'


    def __readFile(self):
        try:
            self.m_config = configparser.ConfigParser()
            readFile = self.m_config.read(self.m_configFileName)
        except:
            self.__printText('Config file not found: ' + self.m_configFileName)


    def __printText(self, text):
        if self.m_debugLogger:
            self.__printText(text)
        else:
            print(text)
