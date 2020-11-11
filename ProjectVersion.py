def getVersionNumber():
    try:
        with open('VersionNumber.txt', 'r') as versionFile:
            versionNumber = versionFile.read().rstrip()
            versionFile.close()
            return versionNumber
    except:
        print('File ' + str(logFileName) + ' not found.')
        return ''
