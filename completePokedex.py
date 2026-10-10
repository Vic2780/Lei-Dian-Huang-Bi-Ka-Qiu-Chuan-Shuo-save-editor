inputFilePath = 'INPUT FILE HERE.sav'
outputFilePath = 'OUTPUT FILE HERE.sav'

def readModifyBinFile(inputFilePath, outputFilePath):
    try:
        with open(inputFilePath, 'rb') as inputFile:
            data = bytearray(inputFile.read())

        maxVal = 159 # target number of Pokédex entries
        data[0x0C31] = maxVal  # seen
        data[0x0C32] = maxVal  # caught, in a naturally completed save, this will instead be 156
        data[0x0CC8] = maxVal  # maximum seen

        # set Pokémon 1–152 as caught
        data[0x0C9F:0x0CB2] = b'\xFF' * 19
        # set Pokémon 153–159 as caught
        data[0x0CB2] = 0x7F #in a naturally completed save, this will instead be 0x0F

        # set Pokémon 1–152 as seen
        data[0x0CB3:0x0CC6] = b'\xFF' * 19
        # set Pokémon 153–159 as seen
        data[0x0CC6] = 0x7F

        # calculate checksum
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