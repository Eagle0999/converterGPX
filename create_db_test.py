import os
import io
import regex as re
import psycopg2
from transliterate import translit


def sendSQLQuery(query,cur,conn):
    cur.execute(query)
    conn.commit()
def gpxparser():
    
    listOfPathsGPX = './valid_gpx/'
    listOfFileNamesGPX = []
    for filename in os.listdir(listOfPathsGPX):
        if filename.endswith(".gpx"):
            listOfFileNamesGPX.append(filename)

    patterntitle = r'(?<=<title>)(.+)(?=<\/title>)'
    patterngnss = r'(?<=<GNSS>)(.+)(?=<\/GNSS>)'
    patternlat = r'(?<=lat=")(\d+\.?\d*)(?=")'
    patternlon = r'(?<=lon=")(\d+\.?\d*)(?=")'
    patternpdop = r'(?<=<PDOP>)(\d+\.?\d*)(?=<\/PDOP>)'

    nameTracks = []
    nameTracks2 = []
    nameGNSSs = []
    nameGNSSs2 = []
    index = 0
    configconnect = "host=localhost port=5432 dbname=tst_map2 user=postgres password=root"
    conn = psycopg2.connect(configconnect)

    cur = conn.cursor()

   
    query = '''CREATE TABLE tracks(
            id SERIAL,
            trackName TEXT,
            tableName TEXT,
            typeGNSS TEXT,
            PRIMARY KEY(id)
            );'''
    sendSQLQuery(query,cur,conn)

    for  indexfileGPX, fileGPX in enumerate(listOfFileNamesGPX):
        f = io.open(listOfPathsGPX + fileGPX, 'r', encoding='utf-8')
        data = f.read()
        f.close()
        pattern = r'<trkseg>[\s\w\d<>\'\"=\[\] \.\t\n -:\/\\]+<\/trkseg>'
        
        nameGNSSs2.append(re.findall(patterngnss, data))
        nameGNSSs2[indexfileGPX] = (re.sub(r'[\[\]\.\'\!?:"]+', '', str(nameGNSSs2[indexfileGPX])))
        nameGNSSs2[indexfileGPX] = (re.sub(r'(GLN)|(gln)', 'ГЛОНАСС', str(nameGNSSs2[indexfileGPX])))
        nameGNSSs2[indexfileGPX] = (re.sub(r'(BDS)|(bds)', 'Beidou', str(nameGNSSs2[indexfileGPX])))
        nameGNSSs2[indexfileGPX] = (re.sub(r'(GAL)|(gal)', 'Galileo', str(nameGNSSs2[indexfileGPX])))

        nameGNSSs.append(re.findall(patterngnss, data))
        nameGNSSs[indexfileGPX] = (re.sub(r'[\[\]\.\'\!?:"]+', '', str(nameGNSSs[indexfileGPX])))
        
        nameTracks2.append(str(re.findall(patterntitle,  data)))
        nameTracks2[indexfileGPX] = re.sub(r'[\[\]\.\'\!?:"]+', '', nameTracks2[indexfileGPX])
        
        nameTracks.append(str(re.findall(patterntitle,  data)))
        nameTracks[indexfileGPX] = re.sub(r'[ ,()-]+', '_', translit(nameTracks[indexfileGPX], "ru", reversed=True))
        nameTracks[indexfileGPX] = re.sub(r'[\[\]\.\'\!?:"]+', '', nameTracks[indexfileGPX])
        nameTracks[indexfileGPX] = (nameTracks[indexfileGPX]+'_' + nameGNSSs[indexfileGPX] + '_' +str(indexfileGPX+1)).lower()
        
        tmpdata = []
        tmpdata = str(re.findall(pattern, data)).split('</trkseg>')[:-1]
        print('\n  type(tmpdata) - {0}\n  length of {0} - {1} \n\n'.format(type(tmpdata), len(tmpdata)))
        print(' {0}) {1}'.format(indexfileGPX+1, nameTracks[indexfileGPX]))
        

        query = '''INSERT INTO tracks(trackName, tableName, typeGNSS)
            VALUES ('{0}', '{1}', '{2}');'''.format(nameTracks2[indexfileGPX], nameTracks[indexfileGPX], nameGNSSs2[indexfileGPX])
        sendSQLQuery(query,cur,conn)
        
        query = '''CREATE TABLE {0}(
            id SERIAL,
            latitudes double precision,
            longitudes double precision,
            pdops double precision,
            tracks_ID INT not null,
            FOREIGN KEY (tracks_ID) REFERENCES tracks(id),
            subtrack_ID INT not null,
            PRIMARY KEY(id)
        );'''.format(nameTracks[indexfileGPX])
        sendSQLQuery(query,cur,conn)

        latitudes = []
        longitudes = []
        pdops = []
       
        for  indexTrack, item in enumerate(tmpdata):

            latitudes.append(re.findall(patternlat, item))
            longitudes.append(re.findall(patternlon, item))
            pdops.append(re.findall(patternpdop, item))

            for indexSubTrack, itemData in enumerate(latitudes[indexTrack]):
             
                query = '''INSERT INTO {0}( latitudes, longitudes, pdops, tracks_ID, subtrack_ID)
                    VALUES ('{1}', '{2}', {3}, {4}, {5});'''.format(nameTracks[indexfileGPX], latitudes[indexTrack][indexSubTrack], longitudes[indexTrack][indexSubTrack], pdops[indexTrack][indexSubTrack], indexfileGPX+1, indexTrack+1)
                sendSQLQuery(query,cur,conn)
            
            #index+=1
 

    for item in nameTracks:
        print(item)  


if __name__ == '__main__':
    gpxparser()
