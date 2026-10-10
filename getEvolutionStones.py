inputFilePath = 'INPUT FILE HERE.sav'
outputFilePath = 'OUTPUT FILE HERE.sav'

def readModifyBinFile(inputFilePath, outputFilePath):
    try:
        with open(inputFilePath, 'rb') as inputFile:
            data = bytearray(inputFile.read())
        
        # set evolution stones to 20 (can technically be 255 but three digit has bad visual impact)
        for i in range(0x0CE2, 0x0CE7):
            data[i] = 20

        #calculate checksum
        checksum = 0
        c = 0   #carry bit
        for i in range(0x0C00, 0x1600):
            checksum = checksum + data[i] + c
            c = 0
            if (checksum > 255):
                checksum = checksum & 255
                c = 1
        for i in range(0x1C00, 0x1C10):
            checksum = checksum + data[i]
            c = 0
            if (checksum > 255):
                checksum = checksum & 255
                c = 1
        checksum = checksum & 255
        oldchecksum = data[0x1C20]
        data[0x1C20] = checksum

        with open(outputFilePath, 'wb') as outputFile:
            outputFile.write(data)

        print(f"File saved as {outputFilePath}")
    except IOError as e:
        print(f"Error occurred: {e}")

readModifyBinFile(inputFilePath, outputFilePath)
