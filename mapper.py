import sys, os, re

#Store gradients for ties
gradients = []

#Read the input file
def readData(filename='input.csv'):
    #Make sure the file exists first
    if (not os.path.exists(filename)):
        print('Error: file "' + filename + '" does not exist!')
        exit()

    section = None
    key = None
    colorValue = None
    fileData = {
        'SETTINGS': {},
        'COLORS': {},
        'CANDIDATES': {},
        'COUNTIES': {}
    }

    with open(filename, 'r') as f:
        lines = f.readlines()

        #Go through each line
        for l in range(len(lines)):
            line = lines[l]
            cells = line.strip('\n').split(',')

            #Go through each cell
            for c in range(len(cells)):
                cell = cells[c]

                #Skip empty cells
                if (cell == ''):
                    continue
                
                #Get the current section
                if (c == 0 and cell in fileData.keys()):
                    section = cell
                    break
                else:
                    #Get the current key
                    if (c == 0):
                        key = cell
                    #Set the value of the current key within the current section
                    elif (c == 1 and key != None):
                        if (section == 'COLORS'):
                            #For the color section, the 2nd value is the percent/margin
                            colorValue = cell
                        elif (section == 'COUNTIES'):
                            #Skip it, if it's outside the isolation
                            if ('Isolate' in fileData['SETTINGS'].keys() and cell not in fileData['SETTINGS']['Isolate']):
                                continue

                            #For the counties section, the 2nd value is the state and should be added to the key
                            key = key + ', ' + cell
                        else:
                            fileData[section][key] = cell
                    elif (c >= 2 and key != None):
                        if (section == 'COUNTIES'):
                            #Skip it, if it's outside the isolation
                            if ('Isolate' in fileData['SETTINGS'].keys() and key.split(', ')[-1] not in fileData['SETTINGS']['Isolate']):
                                continue

                            #Create the county dictionary, if it doesn't exist
                            if (key not in fileData[section].keys()):
                                fileData[section][key] = {}

                            #Add the candidate's votes
                            if (c - 2 < len(fileData['CANDIDATES'].keys())):
                                fileData[section][key][list(fileData['CANDIDATES'].keys())[c - 2]] = cell
                            #The last column should be the total, if using raw votes
                            elif (fileData['SETTINGS']['Vote type'].lower() == 'raw' and c - 2 == len(fileData['CANDIDATES'].keys())):
                                fileData[section][key]['total'] = cell
                        elif (section == 'COLORS' and c == 2 and colorValue != None):
                            #Create the color definition, if it doesn't exist
                            if (key not in fileData[section].keys()):
                                fileData[section][key] = []

                            #Add the color to the list
                            color = [colorValue, cell]
                            fileData[section][key].append(color)
    
    #Validate the settings
    if ('Filename' in fileData['SETTINGS'].keys()):
        if (fileData['SETTINGS']['Filename'] == ''):
            #Set the filename, if blank
            fileData['SETTINGS']['Filename'] = 'output'
    else:
        #Set the filename, if not provided
        fileData['SETTINGS']['Filename'] = 'output'

    if (re.search('[./\\<>:"|?*]', fileData['SETTINGS']['Filename'])):
        print('Error: invalid filename "' + fileData['SETTINGS']['Filename'] + '"!')
        exit()

    if ('Vote type' not in fileData['SETTINGS'].keys()):
        print('Error: please specify the vote type!')
        exit()

    if (fileData['SETTINGS']['Vote type'].lower() not in ['raw', 'percent']):
        print('Error: vote type must be raw or percent!')
        exit()

    if ('Color type' not in fileData['SETTINGS'].keys()):
        #Set the color type to margin by default
        fileData['SETTINGS']['Color type'] = 'Margin'

    if (fileData['SETTINGS']['Color type'].lower() not in ['margin', 'percent']):
        print('Error: color type must be margin or percent!')
        exit()

    #Remove spaces from isolate list
    if ('Isolate' in fileData['SETTINGS'].keys()):
        fileData['SETTINGS']['Isolate'] = fileData['SETTINGS']['Isolate'].split(' ')

    #Show borders by default
    if ('Borders' not in fileData['SETTINGS'].keys()):
        fileData['SETTINGS']['Borders'] = 'TRUE'

    #Show the separator by default
    if ('Separator' not in fileData['SETTINGS'].keys()):
        fileData['SETTINGS']['Separator'] = 'TRUE'

    return fileData

#Get a county's color based on the winner's share of the vote
def getColor(data, county):
    global gradients

    #Check if the user has told us to use NV or NA
    c1 = county[list(county.keys())[0]]
    if (c1 in ['NV', 'NA']):
        if (c1 == 'NV'):
            return '#cccccc'
        elif (c1 == 'NA'):
            return '#999999'

    #Get each candidate's vote share
    voteShare = {}
    for c in county.keys():
        if c != 'total':
            if (data['SETTINGS']['Vote type'].lower() == 'raw'):
                voteShare[c] = int(county[c]) / int(county['total'])
            elif (data['SETTINGS']['Vote type'].lower() == 'percent'):
                voteShare[c] = int(county[c])

    #Find the winner(s) and 2nd place
    winners = []
    winnerNames = []
    second = []
    secondNames = []
    for k in voteShare.keys():
        #Make the first option the winner by default
        if (len(winners) == 0):
            winners = [voteShare[k]]
            winnerNames = [k]

        #Replace the winner, if it's larger
        elif (voteShare[k] > winners[0]):
            second = winners
            secondNames = winnerNames
            winners = [voteShare[k]]
            winnerNames = [k]

        #Add the winner to the list, if they're the same (they tied)
        elif (voteShare[k] == winners[0]):
            winners.append(voteShare[k])
            winnerNames.append(k)

        #Just get the 2nd place
        elif (voteShare[k] < winners[0]):
            if (len(second) == 0 or voteShare[k] > second[0]):
                second = [voteShare[k]]
                secondNames = [k]
            elif (voteShare[k] == second[0]):
                second.append(voteShare[k])
                secondNames.append(k)

    #Get the color value number (-1 is a tie)
    value = 0
    if (len(winners) > 1):
        value = -1
    elif (data['SETTINGS']['Color type'].lower() == 'margin'):
        if (len(second) > 0):
            value = winners[0] - second[0]
        else:
            value = -1
    elif (data['SETTINGS']['Color type'].lower() == 'percent'):
        value = winners[0]

    #Get the winner's color
    if (value == -1):
        #Create a gradient
        gradient = []
        for i in range(len(winners)):
            colors = data['COLORS'][data['CANDIDATES'][winnerNames[i]]]
            if (data['SETTINGS']['Color type'].lower() == 'margin'):
                #If using margins, the middle color will be used, which is +20 by default
                v = int(colors[round(len(colors) / 2)][0])
            elif (data['SETTINGS']['Color type'].lower() == 'percent'):
                v = winners[i] * 100
            for c in colors:
                if (v >= int(c[0])):
                    if (i == 0):
                        wColor = c[1]
                    else:
                        wColor = c[1]
            gradient.append(wColor)
        gradients.append(gradient)

        #Set the color to be a reference to that gradient
        color = 'url(#linearGradient' + str(len(gradients)) + ')'
    else:
        colors = data['COLORS'][data['CANDIDATES'][winnerNames[0]]]
        for c in colors:
            if (value * 100 >= int(c[0])):
                color = '#' + c[1]
    return color

#Read the SVG file and output a modified version based on the data provided
def makeSVG(data):
    global gradients

    svgData = {}
    currentObjID = currentTitle = currentD = currentStyle = ''

    fStart = 2971
    fEnd = 24976
    bEnd = 24986
    sEnd = 24995
    gradientPos = 17

    #Open the blank map
    with open('map.svg') as f:
        lines = f.readlines()

        for l in range(fStart, fEnd):
            line = lines[l]

            #Close the object
            if line.strip() == '</path>':
                #Skip it, if it's not in the isolation
                if ('Isolate' in data['SETTINGS'].keys() and currentTitle.split(', ')[-1] not in data['SETTINGS']['Isolate']):
                    currentObjID = currentTitle = currentD = currentStyle = ''
                    continue

                if (currentObjID != '' and currentTitle != '' and currentD != '' and currentStyle != ''):
                    #Add the object to the dictionary
                    svgData[currentObjID] = {
                        'title': currentTitle,
                        'd': currentD,
                        'style': currentStyle
                    }
                currentObjID = currentTitle = currentD = currentStyle = ''
                continue

            #Get the object ID
            elif line.strip().startswith('id="'):
                match = re.search('".*"', line.strip())
                if (match == None):
                    continue
                else:
                    objID = match.group(0).strip('"')

                    #Set the title, if it's a title object
                    if (objID.startswith('title')):
                        tmatch = re.search('>.*<', line.strip())

                        if (tmatch == None):
                            continue
                        else:
                            currentTitle = tmatch.group(0).lstrip('>').rstrip('<')

                    #Set the current object ID
                    else:
                        currentObjID = objID

            #Get the object's d attribute
            elif (line.strip().startswith('d="')):
                dmatch = re.search('".*"', line.strip())
                if (dmatch == None):
                    continue
                else:
                    currentD = dmatch.group(0).strip('"')

            #Get the object's style
            elif (line.strip().startswith('style="')):
                smatch = re.search('".*"', line.strip())
                if (smatch == None):
                    continue
                else:
                    currentStyle = smatch.group(0).strip('"')

    #Go through each object in svgData and set the fill color
    for i in range(len(svgData.keys())):
        obj = svgData[list(svgData.keys())[i]]

        if (obj['title'] in data['COUNTIES'].keys()):
            #Get the county's color
            color = getColor(data, data['COUNTIES'][obj['title']])
            
            #Set the fill
            if (re.match('fill:[^;]*;', obj['style'])):
                obj['style'] = re.sub('fill:[^;]*;', 'fill:' + color + ';', obj['style'])
            else:
                obj['style'] = obj['style'] + 'fill:' + color + ';'

    #Create a new svg document
    newSVG = ''
    with open('map.svg') as f:
        lines = f.readlines()

        #Copy the first part
        for l in range(0, fStart):
            if (l == gradientPos):
                #Add the gradients before copying the line
                for g in range(len(gradients)):
                    gradient = gradients[g]
                    gradient = gradient + gradient + gradient + gradient

                    #Open the gradient
                    newSVG = newSVG + '''    <linearGradient
       inkscape:collect="always"
       id="linearGradient''' + str(g + 1) + '''"
       spreadMethod="repeat"
       x1="0%"
       y1="0%"
       x2="100%"
       y2="100%">'''

                    #Add all the colors
                    cWidth = 1 / (len(gradient) - 1) * 100 - 0.01
                    for c in range(len(gradient)):
                        color = gradient[c]
                        cStart = c / len(gradient)
                        newSVG = newSVG + '''
      <stop
         style="stop-color:#''' + color + ''';stop-opacity:1;"
         offset="''' + str(cStart * 100) + '''%"
         id="stop''' + str(c + 1) + '''" />
      <stop
         style="stop-color:#''' + color + ''';stop-opacity:1;"
         offset="''' + str(cStart * 100 + cWidth) + '''%"
         id="stop''' + str(c + 1) + '''b" />'''

                    #Close the gradient
                    newSVG = newSVG + '\n    </linearGradient>\n'

            newSVG = newSVG + lines[l]

        #Add the new county objects
        for k in svgData.keys():
            obj = svgData[k]
            newSVG = newSVG + '''    <path
       id="{id}"
       d="{d}"
       style="{style}">
      <title
         id="title-{id}">{title}</title>
    </path>
'''.format(id = k, d = obj['d'], style = obj['style'], title = obj['title'])

        #Copy the borders, if enabled
        if (data['SETTINGS']['Borders'].lower() == 'true'):
            for l in range(fEnd, bEnd):
                newSVG = newSVG + lines[l]
        else:
            #Close the g
            newSVG = newSVG + '''
      </g>'''

        #Copy the separator, if enabled
        if (data['SETTINGS']['Separator'].lower() == 'true'):
            for l in range(bEnd, sEnd):
                newSVG = newSVG + lines[l]
        else:
            #Close the SVG
            newSVG = newSVG + '''
    </svg>'''

    f = open(data['SETTINGS']['Filename'] + '.svg', 'w')
    f.write(newSVG)
    f.close()
    print('File written as ' + data['SETTINGS']['Filename'] + '.svg')

#Get the command line arguments
args = {}
for a in sys.argv:
    arg = a.partition('=')
    if (arg[1] != ''):
        args[arg[0]] = arg[2]

#Get the data
if ('-i' in args.keys()):
    #Read a specific file provided by the user
    data = readData(args['-i'])
else:
    #Read the default file
    data = readData()

#Make a new SVG
makeSVG(data)