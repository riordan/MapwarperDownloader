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

def getLayerJSON(id):
	response = urllib2.urlopen('http://maps.nypl.org/warper/layers/%s/maps' %id)
	layerJSON = response.read()
	mjson = json.loads(layerJSON)

	if mjson['total_pages']>1:
		print "Aw SNAP! More than 50 items. Don't blame me, it's Topomancy's fault. \nI'll get the first 50 for you though"
	else:
		print "AWESOME! We can download the whole layer for ya."

	return (mjson, layerJSON)

def getMapIDs(layerJSON):
	mapIDs = []
	for map in layerJSON['items']:
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


layerID = getLayerID()
layerJSON, jsontext = getLayerJSON(layerID)
setCredentials()

# Save LayerJSON and folder

md = open('metadatalayer_%s.json'%layerID,'w')
md.write(jsontext)
md.close()


mapIDs = getMapIDs(layerJSON)

dlManager(mapIDs)
