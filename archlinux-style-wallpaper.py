#import statements
import time, PIL, PIL.Image, PIL.ImageDraw, PIL.ImageFont, os, ctypes, datetime, sys, psutil, urllib.request
import json as JSON
from time import gmtime, strftime

#the main class for this program
class program:
    #a function to get the local time and format it into a new dict
    def localtime() -> dict:
        ENDTIMEDICT = {}
        LOCALTIME = time.localtime()
        for partition in range(len(LOCALTIME)):
            if (partition == 0):
                ENDTIMEDICT['year'] = LOCALTIME[partition]
            elif (partition == 1):
                ENDTIMEDICT['month'] = LOCALTIME[partition]
            elif (partition == 2):
                ENDTIMEDICT['day'] = LOCALTIME[partition]
            elif (partition == 3):
                ENDTIMEDICT['hour_24HR'] = LOCALTIME[partition]
                ENDTIMEDICT['hour_12HR'] = int(LOCALTIME[partition])
                if (int(ENDTIMEDICT['hour_24HR'] > 12)):
                    ENDTIMEDICT['hour_12HR'] = int(LOCALTIME[partition]) - 12
                if (int(ENDTIMEDICT['hour_24HR']) < 12):
                    ENDTIMEDICT['pm/am'] = 'am'
                else:
                    ENDTIMEDICT['pm/am'] = 'pm'
            elif (partition == 4):
                ENDTIMEDICT['minute'] = LOCALTIME[partition]
            elif (partition == 5):
                ENDTIMEDICT['second'] = LOCALTIME[partition]
            elif (partition == 6):
                ENDTIMEDICT['weekday'] = LOCALTIME[partition]
            elif (partition == 7):
                ENDTIMEDICT['yearday'] = LOCALTIME[partition]
            elif (partition == 8):
                ENDTIMEDICT['daylightsavingtime'] = bool(int(LOCALTIME[partition]))
        return ENDTIMEDICT
    #a function to convert strings like "%hour%:%minute%" into "12:34"
    def formatTimeString(string) -> str:
        timeNow = program.localtime()
        if (len(str(timeNow['second'])) == 1):
            timeNow['second'] = '0' + str(timeNow['second'])
        if (len(str(timeNow['minute'])) == 1):
            timeNow['minute'] = '0' + str(timeNow['minute'])
        weekday = datetime.datetime.now().strftime('%A').capitalize()
        monthname = datetime.datetime.now().strftime('%B').capitalize()
        timeOfDayName = ''
        hour = timeNow['hour_24HR']
        if (hour < 5):
            timeOfDayName = 'Night'
        elif (hour < 12):
            timeOfDayName = 'Morning'
        elif (hour < 18):
            timeOfDayName = 'Afternoon'
        elif (hour < 20):
            timeOfDayName = 'Evening'
        else:
            timeOfDayName = 'Night'
        replaceWith = [
            ['%year%', timeNow['year']],
            ['%month%', timeNow['month']],
            ['%day%', timeNow['day']],
            ['%hour%', timeNow['hour_12HR']],
            ['%hour24%', timeNow['hour_24HR']],
            ['%pm/am%', timeNow['pm/am']],
            ['%minute%', timeNow['minute']],
            ['%second%', timeNow['second']],
            ['%weekday%', timeNow['weekday']],
            ['%yearday%', timeNow['yearday']],
            ['%dst%', timeNow['daylightsavingtime']],
            ['%weekdayname%', weekday],
            ['%monthname%', monthname],
            ['%timeofdayname%', timeOfDayName]
        ]
        for each in range(len(replaceWith)):
            string = string.replace(str(replaceWith[each][0]), str(replaceWith[each][1]))
        return string
    #a function to get the data from the manifest file
    def getPresetData(presetsFilePath = './manifest.json') -> dict:
        data = str(open(presetsFilePath).read())
        data = JSON.loads(data)
        return data
    #the main function where the image is generated
    def main() -> None:
        manifestData = program.getPresetData()
        image = PIL.Image.open(manifestData['data']['image-path'])
        weatherData = {'location':manifestData['data']['closest-city'], 'weather-get-success':True, 'temperature':0, 'weather':0}
        try:
            dataForWeatherData = JSON.loads(str(urllib.request.urlopen('http://api.openweathermap.org/data/2.5/weather?q={}&APPID={}&units=imperial'.format(manifestData['data']['closest-city'], manifestData['data']['owm-api-key'])).read().decode()))
            weatherData['weather'] = dataForWeatherData['weather'][0]['main'].capitalize()
            weatherData['temperature'] = dataForWeatherData['main']['temp']
        except Exception as error:
            print ('Error while getting weather information: {}'.format(error))
        columns = {
            'Time':[str(program.formatTimeString('%hour%:%minute%%pm/am%')), str(program.formatTimeString('%timeofdayname%')).lower().capitalize()],
            'Day':[str(program.formatTimeString('%weekdayname%')), str(program.formatTimeString('%monthname% %day%'))],
            'System':[str(sys.platform), str('Cpu: {}%'.format(str(psutil.cpu_percent()))), str('Mem: {}%'.format(psutil.virtual_memory().percent))]
        }
        topicsAlphabeticallySorted = ['Day', 'System', 'Time'] #fix this so it automatically sorts and you dont have to hardcode it
        if (weatherData['weather-get-success'] and manifestData['data']['owm-api-key'] != ''):
            topicsAlphabeticallySorted.append('Weather')
            columns['Weather'] = [str(weatherData['location']).capitalize(), str('Temperature: {}°F'.format(str(weatherData['temperature']))), str('Weather: {}'.format(str(weatherData['weather'])))]
        marginWidth = 10
        seperatorLineWidth = 1
        columnHeights = int(image.size[1] / 8)
        marginLeft = int((image.size[0] / 4) / 2)
        marginBottom = int((image.size[1] - columnHeights) / 2)
        imageFreeContentAreaWidth = int(image.size[0] - (marginLeft * 2))
        image = image.rotate(-90, expand = 1)
        draw = PIL.ImageDraw.Draw(image)
        index = 0
        xCoordinates = []
        for column in topicsAlphabeticallySorted:
            descriptionFont = PIL.ImageFont.truetype(manifestData['data']['font-path'], int(columnHeights / 5))
            textSize = draw.textsize(column, font = descriptionFont)
            topCoords = int((imageFreeContentAreaWidth / len(columns)) * index) + marginLeft
            draw.text([marginBottom, topCoords], column, manifestData['data']['text-color'], font = descriptionFont)
            topCoords += textSize[1] + marginWidth
            draw.line([marginBottom, topCoords, marginBottom + columnHeights, topCoords], fill = manifestData['data']['text-color'], width = seperatorLineWidth)
            topCoords += marginWidth
            xCoordinates.append(topCoords)
            index += 1
        image.save('./output.png')
        image = PIL.Image.open('./output.png')
        image = image.rotate(90, expand = 1)
        draw = PIL.ImageDraw.Draw(image)
        index = 0
        for column in topicsAlphabeticallySorted:
            rows = len(columns[column])
            infoFont = PIL.ImageFont.truetype(manifestData['data']['font-path'], int((columnHeights / 1.5) / rows))
            for row in range(rows):
                topCoords = marginBottom + (int(columnHeights / rows) * row)
                draw.text([xCoordinates[index], topCoords], columns[column][row], manifestData['data']['text-color'], font = infoFont)
            index += 1
        image.save('./output.png')
        ctypes.windll.user32.SystemParametersInfoW(20, 0, os.path.normpath(os.getcwd() + '/output.png'), 0)

while (1):
    program.main()
    time.sleep(20)