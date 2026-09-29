inputFilePath = 'INPUT FILE HERE.sav'
outputFilePath = 'OUTPUT FILE HERE.sav'


def readModifyBinFile(inputFilePath, outputFilePath):
    try:
        with open(inputFilePath, 'rb') as inputFile:
            data = bytearray(inputFile.read())

        # Unlock Pokédex
        maxVal = 150              # Technical max is 159

        data[0x0C31] = maxVal     # Pokémon discovered
        data[0x0C32] = maxVal     # Pokémon captured
        data[0x0CC8] = maxVal     # Maximum seen in Pokédex

        # Set Pokédex data
        for i in range(0x0CB3, 0x0CC7):
            data[i] = 255

        # Calculate checksum
        checksum = 0
        c = 0

        for i in range(0x0C00, 0x1600):
            checksum = checksum + data[i] + c
            c = 0

            if checksum > 255:
                checksum = checksum & 255
                c = 1

        for i in range(0x1C00, 0x1C10):
            checksum = checksum + data[i]
            c = 0

            if checksum > 255:
                checksum = checksum & 255
                c = 1

        checksum = checksum & 255

        # Write new checksum
        data[0x1C20] = checksum

        with open(outputFilePath, 'wb') as outputFile:
            outputFile.write(data)

        print(f"File saved as {outputFilePath}")

    except IOError as e:
        print(f"Error occurred: {e}")


readModifyBinFile(inputFilePath, outputFilePath)