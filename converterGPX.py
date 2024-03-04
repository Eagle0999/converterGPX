import os
import io
import regex as re
#from transliterate import translit
from datetime import datetime
from dateutil import parser
def convertergpx():
    
    listOfPathsGPX = './invalid_gpx/'
    listOfFileNamesGPX = []
    for filename in os.listdir(listOfPathsGPX):
        if filename.endswith(".gpx"):
            listOfFileNamesGPX.append(filename)
    print(listOfFileNamesGPX)

    patterntime = r'(?<=<time>)(.+)(?=<\/time>)'

    for  indexfileGPX, fileGPX in enumerate(listOfFileNamesGPX):
        f = io.open(listOfPathsGPX + fileGPX, 'r', encoding='utf-8')
        data = f.read()
        f.close()
        dates = re.findall(patterntime, data)[1:]

        pourdiff = []
        patterntitle = r'(?<=<title>)(.+)(?=<\/title>)'
        nameTrack = str(re.findall(patterntitle,  data))
        print('file name - ', nameTrack)
        for  index, (prev, current, next) in enumerate(zip(dates,  dates[1:], dates[2:])):
            d1 = parser.isoparse(prev)
            d2 = parser.isoparse(current)
            diff = d2 - d1
            days, seconds = diff.days, diff.seconds
            hours = days * 24 + seconds // 3600
            minutes = (seconds % 3600) // 60

            if minutes >= 1  or hours >= 1 or days >= 1:
                pourdiff.append([prev,current,index])
            
        tmpGPX = []  
        for  index, (prev,current, next) in enumerate(zip(pourdiff,  pourdiff[1:], pourdiff[2:])):
            res = current[2] - prev[2]
            if res >= 15:
                tmpGPX.append(current[0])
            
        starttimes = tmpGPX[0::2] 
        endtimes = tmpGPX[1::2]
        #print(' length of starttimes = ', len(starttimes), '\n')
        #print(' starttimes = ', starttimes, '\n\n')
        #print(' length of endtimes = ', len(endtimes))
        #print(' endtimes = ', endtimes, '\n\n')
        for  index, item in enumerate(endtimes):
            patternstart =  r'<trkpt lat=\"\d+\.\d*\" +lon=\"\d+\.\d*\">\n[ \n\t]*<time>'+ starttimes[index]
            patternend = endtimes[index] + r'[\s \n\t]*?</time>([\t\n ]+<\w+>.+<\/\w+>[\t\n ]+){1,}[\t\n ]+<\/\w+>'
            pattermiddle = starttimes[index] + r'[\s\w\d<>\'\"=\[\] \.\t\n -:\/\\]+' + endtimes[index]    
            trksegOpen ='\n    <trkseg>\n      '
            trksegclose ='\n    </trkseg>\n'

            start = re.search(patternstart,  data)
            start = start.group(0).replace(starttimes[index],'')
            end =  re.search(patternend,  data).group(0).replace(endtimes[index],'')
            content = start + re.search(pattermiddle,  data).group(0) + end

            data = data.replace(content, (trksegclose + trksegOpen + content + trksegclose + trksegOpen))
            if index == 0:
                print(' start = ', start, '\n\n')
                print(' end = ', end, '\n\n')
                #print(' content = ', content, '\n\n')
            #print(' data = ', data, '\n\n')
            
        f = io.open('./valid_gpx/' + fileGPX, "w", encoding='utf-8')
        f.write(data)
        f.close()

if __name__ == '__main__':
    convertergpx()
