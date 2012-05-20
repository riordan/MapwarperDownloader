import urllib2, json, sys, base64, time


def getLayerID():
	print "Enter Map Layer ID:"
	layerID = int(raw_input())
	if isinstance(layerID, int):
		return layerID
	else:
		sys.exit("Layer ID not a number")

def setCredentials():
	print "Enter NYPL Map Warper username:"
	global username
	global password

	username = raw_input()

	print "Enter NYPL Map Warper Password:"

	password = raw_input()

	print "Thank you"

def getLayerJSON(id, currentpage=0, totalpages=None, allLayers = []):
	
	#Recursive end case
	if currentpage >= totalpages and totalpages != None:
		return allLayers

	currentpage +=1

	response = urllib2.urlopen('http://maps.nypl.org/warper/layers/%s/maps.json?page=%s' %(id, currentpage))
	layerJSON = response.read()
	
	#Figure out how many pages there actually are if this is a first pass
	if totalpages == None:
		print "Assigning actual number of pages"
		totalpages = json.loads(layerJSON)['total_pages']

	allLayers.append(layerJSON)

	return getLayerJSON(id,currentpage,totalpages, allLayers)


def getMapIDs(layerJSONs):
	mapIDs = []
	for layer in layerJSONs:
		for map in layer['items']:
			mapIDs.append(map['id'])
	return mapIDs

def dlGeoTiff(mapID):


	url = "http://maps.nypl.org/warper/maps/export/%s?format=tif" %mapID

	file_name = "%s.tif" %mapID
	request = urllib2.Request(url)
	base64string = base64.encodestring('%s:%s' %(username,password)).replace('\n', '')
	request.add_header("Authorization", "Basic %s" % base64string)   

	u = urllib2.urlopen(request)
	f = open(file_name, 'wb')
	meta = u.info()
	file_size = int(meta.getheaders("Content-Length")[0])
	print "Downloading: %s Bytes: %s" % (file_name, file_size)

	file_size_dl = 0
	block_sz = 8192
	while True:
	    buffer = u.read(block_sz)
	    if not buffer:
	        break

	    file_size_dl += len(buffer)
	    f.write(buffer)
	    status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
	    status = status + chr(8)*(len(status)+1)
	    print status,

	f.close()


def dlManager(idList):
	print "There are %s maps in this layer." % len(idList)
	i = 0
	for map in idList:
		i += 1
		print "DOWNLOADING MAP # %s OF %s" %(i, len(idList))
		dlGeoTiff(map)
		if i < len(idList):
			print "Waiting 30 seconds to not murder the map server"
			time.sleep(30)

def stringstoJSONs(stringArray):
	jsonArray = []
	for js in stringArray:
		jsonArray.append(json.loads(js))
	return jsonArray



#Takes paginated JSON and writes to file
def writeMetadata(jsonLayers, layerID):
	count = 1
	for layer in jsonLayers:
		md = open('metadatalayer_%s_%s.json'%(count,layerID),'w')
		md.write(layer)
		md.close()
		count += 1

layerID = getLayerID()
layersStrings = getLayerJSON(layerID)

writeMetadata(layersStrings, layerID)

layersJSONs = stringstoJSONs(layersStrings)

mapIDs = getMapIDs(layersJSONs)

setCredentials()

dlManager(mapIDs)
