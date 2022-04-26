
from PIL import Image, ImageFont, ImageDraw 
import time
import os

#Colors for the various water and wasteland types from the default.map
generalProvinceColor = (255,255,255,255)    #normal provinces (IR/CK3)
impassableSeaColor = (15,15,100,255)        #seas that can't be sailed on (IR/CK3)
seaColor = (30,30,150,255)                  #normal seas (IR/CK3)
riverColor = (100,100,250,255)              #normal rivers (IR/CK3)
lakeColor = (150,150,200,255)               #lakes (IR/CK3)
wastelandColor = (50,50,50,255)             #wastelands (CK3) / uncolorable wastelands (IR)
unihabitableColor = (185,185,185,255)       #traversable wastelands (IR)
impassableColor = (95,95,95,255)            #colorable wastelands (IR)
borderColor = (0,0,0,255)

textColor = (200,50,50,255)

drawBorders = True      #wether or not to draw province borders (True/False)
boldBorders = False     #borders are 2 pixels thick instead of 1 (True/False)

writeIDs = False             #writes the prov id for each prov to the blank map (True/False)
ignoreWaterIDs = True       #when writing IDs does not write IDs for Water provs (True/False)
ignoreWastelandIDs = True   #when writing IDs does not write IDs for Wasteland provs (True/False)




class ProvinceDefinition:
    def __init__(self):
        self.id = 0
        self.red = 0
        self.green = 0
        self.blue = 0
        self.name = ""
        self.coords = []
        self.center = (0,0)
    def getRGBA(self):
        return((self.red,self.green,self.blue,255))
    def getRGB(self):
        return((self.red,self.green,self.blue))
    def __str__(self):
        return("%i - %s"%(self.id,self.name))
    def calcCenter(self):
        l = len(self.coords)
        totalX = 0
        totalY = 0
        if l>0:
            for c in self.coords:
                totalX+=c[0]
                totalY+=c[1]
            self.center = (int(totalX/l),int(totalY/l))



provList = []
mapDefinition = open("Input/definition.csv", encoding="utf8")
def readProvinceDeff():
    for province in mapDefinition:
        if province.strip().startswith("#"):
            pass
        else:
            tmpline = province.strip().split(';')
            try:
                province = ProvinceDefinition()
                province.red = int(tmpline[1])
                province.id = int(tmpline[0].lstrip("#"))
                province.green = int(tmpline[2])
                province.blue = int(tmpline[3])
                province.name = tmpline[4]
                provList.append(province)
            except:
                pass
    pass



def getRangeList(line, tmpList):
    tmpline = line.replace("{", " ")
    tmpline = tmpline.replace("}", " ")
    tmpline = tmpline.replace("#", " # ")
    words = tmpline.split(" ")
    if "RANGE" in line:
        x1=0
        x2=0
        for word in words:
            if "#" in word:
                break
            else:
                try:
                    if x1 == 0:
                        x1 = int(word)
                    elif x2 == 0:
                        x2 = int(word)
                except:
                    pass
        for i in range(x1,x2+1):
            tmpList.append(i)
    elif "LIST" in line:
        for word in words:
            if "#" in word:
                break
            else:
                try:
                    tmpList.append(int(word))
                except:
                    pass
    pass


seaList = []
riverList = []
lakeList = []
wastelandList = []
uninhabitableList = []
impasableterrainList = []
impassableSeaList = []
def parssDefaultMap():
    defaultMap = open("Input/default.map")
    for line in defaultMap:
        if line.strip().startswith("#"):
            pass
        else:
            if line.strip().lower().startswith("sea_zones"):
                getRangeList(line, seaList)
            if line.strip().lower().startswith("river_provinces"):
                getRangeList(line, riverList)
            if line.strip().lower().startswith("lakes"):
                getRangeList(line, lakeList)
            if line.strip().lower().startswith("wasteland") or line.strip().lower().startswith("impassable_mountains"):
                getRangeList(line, wastelandList)
            if line.strip().lower().startswith("uninhabitable"):
                getRangeList(line, uninhabitableList)
            if line.strip().lower().startswith("impassable_terrain"):
                getRangeList(line, impasableterrainList)
            if line.strip().lower().startswith("impassable_seas"):
                getRangeList(line, impassableSeaList)
    pass


drawColorList = [generalProvinceColor,impassableSeaColor,seaColor,riverColor,lakeColor,wastelandColor,unihabitableColor,impassableColor]
def drawMat(deffProvList):
    try:
        if os.path.exists("Input/provinces.png"):
            provMap = Image.open("Input/provinces.png")
        else:
            provMap = Image.open("Input/provinces.bmp")
    except:
        print("Unable to read provinces image file, would you kindly open and resave it.")
        input('')
        os._exit(0)
    provMap.putalpha(255)
    xRange= range(0,provMap.size[0],1)
    yRange= range(0,provMap.size[1],1)
    drawReader = provMap.load()
    drawingMap = Image.new("RGBA", (provMap.size[0],provMap.size[1]), color = drawColorList[0])
    #drawingMap.putalpha(0)
    riverMat = drawingMap.load()

    colorIndex = []
    if writeIDs:
        for p in provList:
            colorIndex.append(p.getRGBA())

    print("Compressing Image")
    tmpMapColor = []
    ColorLength = []
    for y in yRange:
        mapLine = []
        ColorlengthLine = []
        length = 1
        color = drawReader[0,y]
        if y%512 ==0:
            print("\t%g%%"%(y*100/provMap.size[1]))
        for x in xRange:
            if drawReader[x,y] == color:
                length+=1
            else:
                mapLine.append(color)
                ColorlengthLine.append(length)

                length=1
                color = drawReader[x,y]
        mapLine.append(color)
        ColorlengthLine.append(length)

        tmpMapColor.append(mapLine)
        ColorLength.append(ColorlengthLine)
        #print(mapLine[5])

    print("Drawing Water, Wasteland, and Vertical Borders")

    for y in yRange:
        #print(drawReader[5,y])
        if y%256 ==0:
            print("\t%g%%"%(y*100/provMap.size[1]))
        tx = 0
        for x in range(0,len(tmpMapColor[y])):
            if writeIDs:
                if tmpMapColor[y][x] in colorIndex:
                    p = provList[colorIndex.index(tmpMapColor[y][x])]
                    #print(p)
                    p.coords.append((int((tx+tx+ColorLength[y][x])/2),y)) #center of compressed line
                    #for i in range(tx,tx+ColorLength[y][x]):
                    #    p.coords.append((y,i))

            j=1
            for l in deffProvList:
                #print(l)
                if tmpMapColor[y][x] in l:
                    for i in range(0,ColorLength[y][x]):
                        try:
                            riverMat[tx+i,y] = drawColorList[j]
                        except:
                            pass
                    break
                j+=1
            tx+=ColorLength[y][x]
            #draw ver borders
            if drawBorders:
                if not tx == provMap.size[0]:
                    try:
                        riverMat[tx-1,y] = borderColor
                    except:
                        pass
                    if boldBorders:
                        riverMat[tx-2,y] = borderColor
                    
    
            
    #draw hor borders
    if drawBorders:
        print("Drawing Horizontal Borders")
        for x in xRange:
            if x%512 ==0:
                print("\t%g%%"%(x*100/provMap.size[0]))
            color = drawReader[x,0]
            for y in yRange:
                if drawReader[x,y] == color:
                    pass
                else:
                    riverMat[x,y] = borderColor
                    if boldBorders and not y < 1:
                        riverMat[x,y-1] = borderColor
                    
                    color = drawReader[x,y]

    if writeIDs:
        print("drawing ProvIDs")
        font = ImageFont.truetype("Input\\OpenSans-Semibold.ttf",8)
        draw = ImageDraw.Draw(drawingMap)
        for p in provList:
            if ignoreWaterIDs and (p.getRGBA() in deffProvList[0] or p.getRGBA() in deffProvList[1] or p.getRGBA() in deffProvList[2] or p.getRGBA() in deffProvList[3]):
                pass
            elif ignoreWastelandIDs and (p.getRGBA() in deffProvList[4] or p.getRGBA() in deffProvList[5] or p.getRGBA() in deffProvList[6]):
                pass
            else:
                p.calcCenter()
                draw.text(p.center,"%i"%p.id,textColor,font=font,anchor="mm")
            

    drawingMap.save("BlankMap.png")
    drawingMap.show()

ts1 = time.time()
readProvinceDeff()
parssDefaultMap()

deffProvList = []
impassableProvSea = []
riverProvList = []
seaProvList = []
lakeProvList = []
wastelandProvList = []
uninhabitableProvList = []
impasableterrainProvList = []
for prov in provList:
    if prov.id in impassableSeaList or (prov.id in seaList and prov.id in wastelandList):
        impassableProvSea.append(prov.getRGBA())
    elif prov.id in riverList:
        riverProvList.append(prov.getRGBA())
    elif prov.id in seaList:
        seaProvList.append(prov.getRGBA())
    elif prov.id in lakeList:
        lakeProvList.append(prov.getRGBA())
    elif prov.id in wastelandList:
        wastelandProvList.append(prov.getRGBA())
    elif prov.id in uninhabitableList:
        uninhabitableProvList.append(prov.getRGBA())
    elif prov.id in impasableterrainList:
        impasableterrainProvList.append(prov.getRGBA())
deffProvList.append(impassableProvSea)
deffProvList.append(seaProvList)
deffProvList.append(riverProvList)
deffProvList.append(lakeProvList)
deffProvList.append(wastelandProvList)
deffProvList.append(uninhabitableProvList)
deffProvList.append(impasableterrainProvList)


drawMat(deffProvList)
ts2 = time.time()
print("%g Seconds"%(ts2 - ts1))