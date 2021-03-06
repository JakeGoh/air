#!/usr/bin/python

import mraa as m
import rospy

# simple class to contain the node's variables and code

class TeraRangerOne:     # class constructor; subscribe to topics and advertise intent to publish

    # Configuration Constants
    TRONE_BASEADDR = 0x30
    TRONE_MEASURE_REG = 0x00
    TRONE_WHO_AM_I_REG = 0x01
    TRONE_WHO_AM_I_VAL = 0xA1
    TRONE_CHANGE_BASE_ADDR = 0xA2

    # Device Limits
    TRONE_MIN_DISTANCE = 0.20
    TRONE_MAX_DISTANCE = 14.00

    # MRAA I2C bus frequency modes. These enums should probably be picked up from a header file.
    I2C_STD = 0
    I2C_FAST = 1
    I2C_HIGH = 2

    crcTable = (0x00, 0x07, 0x0e, 0x09, 0x1c, 0x1b, 0x12, 0x15, 0x38, 0x3f, 0x36, 0x31,
	0x24, 0x23, 0x2a, 0x2d, 0x70, 0x77, 0x7e, 0x79, 0x6c, 0x6b, 0x62, 0x65,
	0x48, 0x4f, 0x46, 0x41, 0x54, 0x53, 0x5a, 0x5d, 0xe0, 0xe7, 0xee, 0xe9,
	0xfc, 0xfb, 0xf2, 0xf5, 0xd8, 0xdf, 0xd6, 0xd1, 0xc4, 0xc3, 0xca, 0xcd,
	0x90, 0x97, 0x9e, 0x99, 0x8c, 0x8b, 0x82, 0x85, 0xa8, 0xaf, 0xa6, 0xa1,
	0xb4, 0xb3, 0xba, 0xbd, 0xc7, 0xc0, 0xc9, 0xce, 0xdb, 0xdc, 0xd5, 0xd2,
	0xff, 0xf8, 0xf1, 0xf6, 0xe3, 0xe4, 0xed, 0xea, 0xb7, 0xb0, 0xb9, 0xbe,
	0xab, 0xac, 0xa5, 0xa2, 0x8f, 0x88, 0x81, 0x86, 0x93, 0x94, 0x9d, 0x9a,
	0x27, 0x20, 0x29, 0x2e, 0x3b, 0x3c, 0x35, 0x32, 0x1f, 0x18, 0x11, 0x16,
	0x03, 0x04, 0x0d, 0x0a, 0x57, 0x50, 0x59, 0x5e, 0x4b, 0x4c, 0x45, 0x42,
	0x6f, 0x68, 0x61, 0x66, 0x73, 0x74, 0x7d, 0x7a, 0x89, 0x8e, 0x87, 0x80,
	0x95, 0x92, 0x9b, 0x9c, 0xb1, 0xb6, 0xbf, 0xb8, 0xad, 0xaa, 0xa3, 0xa4,
	0xf9, 0xfe, 0xf7, 0xf0, 0xe5, 0xe2, 0xeb, 0xec, 0xc1, 0xc6, 0xcf, 0xc8,
	0xdd, 0xda, 0xd3, 0xd4, 0x69, 0x6e, 0x67, 0x60, 0x75, 0x72, 0x7b, 0x7c,
	0x51, 0x56, 0x5f, 0x58, 0x4d, 0x4a, 0x43, 0x44, 0x19, 0x1e, 0x17, 0x10,
	0x05, 0x02, 0x0b, 0x0c, 0x21, 0x26, 0x2f, 0x28, 0x3d, 0x3a, 0x33, 0x34,
	0x4e, 0x49, 0x40, 0x47, 0x52, 0x55, 0x5c, 0x5b, 0x76, 0x71, 0x78, 0x7f,
	0x6a, 0x6d, 0x64, 0x63, 0x3e, 0x39, 0x30, 0x37, 0x22, 0x25, 0x2c, 0x2b,
	0x06, 0x01, 0x08, 0x0f, 0x1a, 0x1d, 0x14, 0x13, 0xae, 0xa9, 0xa0, 0xa7,
	0xb2, 0xb5, 0xbc, 0xbb, 0x96, 0x91, 0x98, 0x9f, 0x8a, 0x8d, 0x84, 0x83,
	0xde, 0xd9, 0xd0, 0xd7, 0xc2, 0xc5, 0xcc, 0xcb, 0xe6, 0xe1, 0xe8, 0xef,
	0xfa, 0xfd, 0xf4, 0xf3)

    def __init__(self, bus=1, address=TRONE_BASEADDR, debug=False, freq=I2C_STD):
        self.x = m.I2c(bus) #, raw=True) # forces manual bus selection, vs. board default
        self.address = address
        self.x.frequency(freq) # default to I2C_STD (up to 100kHz). Other options: I2C_FAST (up to 400kHz), I2C_HIGH (up to 3.4Mhz)
        self.x.address(self.address) # address of the TeraRanger sensor
        self.debug = debug
        if self.debug:
            print m.printError(self.x.address(address))

    def probe(self, deb=False):
        "Probing TeraRanger "

        try:
            byte = self.x.readBytesReg(self.TRONE_WHO_AM_I_REG, 1)
        except:
            if self.debug or deb:
                print "TROne readRangeData readBytesReg failed"
            #return -256 # I2C read error
            byte =  [1]

        val = 0x00 << 8 | byte[0]

        if self.debug or deb:
            print "whoAmI: ", val

        if (val == self.TRONE_WHO_AM_I_VAL):
            return True
        else:
            return False;

    def readRangeData(self, deb=False):
        "Read 3 byte distance bytes from the sensor"

        try:
            bytes3 = self.x.readBytesReg(self.TRONE_MEASURE_REG, 3)
        except:
            if self.debug or deb:
                print "TROne readRangeData readBytesReg failed"
            #return -256 # I2C read error
            bytes3 = [0,1,0]

        MSB = bytes3[0]
        LSB = bytes3[1]
        range = MSB << 8 | LSB

        crc = self.crc8check((MSB,LSB), deb=deb)

        if self.debug or deb:
            print "sent crc8: ", bytes3[2], "crc8check: ", crc

        if (str(crc) == str(bytes3[2])):
            if self.debug or deb:
                print "trone (address = 0x%x) ranged %2d mm" % (self.address, range)
            return range
        else:
            # return -255 # bad checksum
            return 1

    def changeNewAddr(self, newAddr, deb=False):

        try:
            self.x.writeReg(self.TRONE_CHANGE_BASE_ADDR, newAddr)
        except:
            if self.debug or deb:
                print "TROne changeNewAddr writeReg failed"
            return -256 # I2C read error

        if self.debug or deb:
            print "TROne address changed to 0x%x" % (newAddr)

        return True

    def crc8check(self, val, deb=False):
        "Computing CRC8"

        i = None
        crc = 0x0

        for c in val:
            i = (crc ^ c) & 0xFF
            crc = (self.crcTable[i] ^ (crc << 8)) & 0xFF

        result = crc & 0xFF

        if self.debug or deb:
            print "crc8check: ", result

        return result

if __name__ == "__main__":

    #trone = TeraRangerOne(address=0x40, debug=True)
    #range = trone.readRangeData()
    #print "trone (address = 0x%x) ranged %2d mm" % (trone.address, range)
    #print trone.probe()

    trone1 = TeraRangerOne(address=0x60, debug=True)
    range = trone1.readRangeData()
    print "trone (address = 0x%x) ranged %2d mm" % (trone1.address, range)
    print trone1.probe()
    print trone1.changeNewAddr(newAddr=0x25, deb=True)

    # trone2 = TeraRangerOne(address=0x33)
    # range = trone2.readRangeData()
    # print "trone (address = 0x%x) ranged %2d mm" % (trone2.address, range)
    # print trone2.probe()

    #rospy.init_node("tera_node")

    #node = TeraRangerOne(address=0x34, debug=True)
    #rate = rospy.Rate(10)

    #while not rospy.is_shutdown():
    #    range = node.readRangeData()      
    #    print range
    #    rate.sleep()

    #sensor = []
    #sensor = [TeraRangerOne(address=(0x34 + i), debug=True) for i in range(1)]

    #for tr in sensor:
    #    range = tr.readRangeData()
    #    print "trone (address = 0x%x) ranged %2d mm" % (tr.address, range)
