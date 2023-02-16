from Config import MIN_YEAR, MAX_YEAR

#############
# gpsToDict #
#############
# Input is printable raw output from AT+CGNSINF 
#
# Name                      Unit                Range                       Length
# ----                      ----                -----                       ------
# GNSS run status           --                  0-1                         1
# Fix status                --                  0-1                         1
# UTC date & Time           yyyyMMddhhmm        yyyy: [1980,2039]           18
#                           ss.sss          
#                                               MM : [1,12]
#                                               dd : [1,31]
#                                               hh : [0,23]
#                                               mm : [0,59]
#                                               ss.sss:[0.000,60.999]
# Latitude                  ±dd.dddddd          [-90.000000,90.000000]      10
# Longitude                 ±ddd.dddddd         [-180.000000,180.000000]    11
# MSL Altitude              meters                                          8
# Speed Over Ground         Km/hour             [0,999.99]                  6
# Course Over Ground        degrees             [0,360.00]                  6
# Fix Mode                  --                  0,1,2 [1]                   1
# Reserved1                                                         

# https://gisgeography.com/gps-accuracy-hdop-pdop-gdop-multipath/
# HDOP                      --                  [0,99.9]                    4
# PDOP                      --                  [0,99.9]                    4
# VDOP                      --                  [0,99.9]                    4

# Reserved2
# GNSS Satellites in View   --                  [0,99]                      2
# GPS Satellites Used       --                  [0,99]                      2
# GLONASS Satellites used   --                  [0,99]                      2
# Reserved3 
# C/N0 max                  dBHz                [0,55]                      2
# HPA [2]                   meters              [0,9999.9]                  6
# VPA [2]                   meters              [0,9999.9]                  6

#############
# gpsToDict #
#############
def gpsToDict(raw):

    err = False
    bad = "0:0,0,00000000000000.000,0.0000000,0.0000000,0.0,0.00,0.0,0,,0.0,0.0,0.0,,0.0,0,0,,0,,........"

    # Once in a while the raw gps data is blank
    if raw == '':
        raw = bad  

    # We expect an array of 21 fields
    try:
        splitString = raw.split(',')
        dummyTest = splitString[20]
        
    except:
        raw = bad
        splitString = raw.split(',')
        err = True

    # The first field contains the AT command: status and needs splitting
    try:
        status = splitString[0].split(":")
    except:
        status = ["0", "0"]
        err = True

    # Should be valid and clean
    gpsDict = {
        'GNSS_RUN_STATUS': status[1].strip(),
        'FIX_STATUS': splitString[1].strip(),
        'UTC_DATE_TIME': splitString[2].strip(),
        'LATITUDE': splitString[3].strip(),
        'LONGITUDE': splitString[4].strip(),
        'MSL_ALTITUDE': splitString[5].strip(),
        'SPEED_OVER_GROUND': splitString[6].strip(),
        'COURSE_OVER_GROUND': splitString[7].strip(),
        'FIX_MODE': splitString[8].strip(),
        'RESERVED_1': splitString[9].strip(),
        'HDOP': splitString[10].strip(),
        'PDOP': splitString[11].strip(),
        'VDOP': splitString[12].strip(),
        'RESERVED_2': splitString[13].strip(),
        'GNSS_SATELITES_IN_VIEW': splitString[14].strip(),
        'GPS_SATELITES_USED': splitString[15].strip(),
        'GLONASS_SATELITES_USED': splitString[16].strip(),
        'RESERVED_3': splitString[17].strip(),
        'C/N0_MAX': splitString[18].strip(),
        'HPA': splitString[19].strip(),
        'VPA': splitString[20].strip(),
        # Andy added these - the GSM modem doesn't return these
        'HDOP_RATING': "",
        'VDOP_RATING': "",
        'PDOP_RATING': "",
        'MEAN_DOP_RATING': "",
        'YEAR': "",
        'MONTH': "",
        'DAY': "",
        'HOUR': "",
        'MINUTE': "",
        'SECOND': "",
        'ERROR': False
    }

    # Rate the DOPs
    gpsDict['HDOP_RATING'] = dopRating(gpsDict['HDOP'])
    gpsDict['VDOP_RATING'] = dopRating(gpsDict['VDOP'])
    gpsDict['PDOP_RATING'] = dopRating(gpsDict['PDOP'])
    mean = meanDOP(gpsDict['HDOP'], gpsDict['VDOP'], gpsDict['PDOP'])
    # NOTE MEAN is probably meaningless use PDOP_RATING
    gpsDict['MEAN_DOP_RATING'] = dopRating(mean)

    y, mm, d, h, m, s, error = separateDateTime(gpsDict['UTC_DATE_TIME'])
    
    gpsDict['YEAR'] = y
    gpsDict['MONTH'] = mm
    gpsDict['DAY'] = d
    gpsDict['HOUR'] = h
    gpsDict['MINUTE'] = m
    gpsDict['SECOND'] = s

    # Hopefully not!
    if err or error:
        gpsDict['ERROR'] = error

    # Dictionary should be full
    return gpsDict

###########
# meanDOP #
###########
def meanDOP(hdopStr, vdopStr, pdopStr):

    # Utter rubbish could be passed in
    try:
        # Some way of generating a single metric from 3 DOPs, how else would you for DOPs?
        # NOTE Probably just use PDOP!
        avgDOP = (float(hdopStr) + float(vdopStr) + float(pdopStr)) / 3
        return str(round(avgDOP, 2))

    # Not interested in why it failed
    except:
        return "n/a"

#############
# dopRating #
#############
# https://en.wikipedia.org/wiki/Dilution_of_precision_(navigation)
def dopRating(dopStr):
    try:
        rating = ""
        dop = float(dopStr)
        if dop > 0.01 and dop < 1:
            rating = "ideal"
        elif dop >= 1 and dop < 2:
            rating = "excellent"
        elif dop >= 2 and dop < 5:
            rating = "good"
        elif dop >= 5 and dop < 10:
            rating = "moderate"
        elif dop >= 10 and dop < 20:
            rating = "fair"
        elif dop >= 20:
            rating = "poor"
        
        return rating

    except:
        rating = "n/a"

        return rating

###################
# separteDateTime #
###################
def separateDateTime(dt):

    # If not the right length time and date are wrong
    if len(dt) != 18:
        return ("0000", "00", "00", "00", "00", "00.000", True)

    try:
        y  = int(dt[:4])
        mm = int(dt[4:6])
        d  = int(dt[6:8])
        h  = int(dt[8:10])
        m  = int(dt[10:12])
        s  = float(dt[12:])

        year = y > (MIN_YEAR - 1) and y < (MAX_YEAR + 1)
        month = mm > 0 and mm < 13
        day = d > 0 and d < 32
        hour = h > -1 and h < 24
        minute = m > -1 and m < 60
        second = s > -1 and s < 60
    except:
        # Something is wrong
        year = False

    # If time or date have invalid numbers time & date are wrong
    if not (year and month and day and hour and minute and second):
        return ("0000", "00", "00", "00", "00", "00.000", True)

    # Can't be much wrong with date and time
    return (dt[:4], dt[4:6], dt[6:8], dt[8:10], dt[10:12], dt[12:], False)

    
    
    