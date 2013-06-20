import requests
import bs4
import os

def login(URL, data, headers):
	loginURL = URL + "/login.php"
	s.post(loginURL, data = data, headers = headers)

def getUserID():
	soup = bs4.BeautifulSoup(s.get(baseURL + "/index.php").text)
	info = soup.find(id = "userinfo_username")
	userID = info.li.a.get("href").split("=")[1]
	return userID

def getSnatchCount(userID):
	profileURL = baseURL + "/user.php?id=" + userID
	html = s.get(profileURL).text
	soup = bs4.BeautifulSoup(html).find(id = "section2").div
	statistics = soup.find_all("div")[1]
	upDownStats = statistics.find_all("div")[2].ul
	uploadsSnatched = int(upDownStats.find_all("li")[2].string.split(":")[1].strip())
	downSnatched = int(upDownStats.find_all("li")[7].contents[0][:-1].split(":")[1].strip())
	return uploadsSnatched + downSnatched

def getTorrentsPerPage(userID):
	URL = "https://broadcasthe.net/user.php?action=edit&userid=%s" % userID
	html = s.get(URL).text
	html = html.replace('selected="selected"'," selected")
	soup = bs4.BeautifulSoup(html)
	perPageOption = soup.find(id = "torperpage")
	options = perPageOption.find_all("option")
	for option in options:
		if "selected" in str(option):
			return option.string

def constructTorrentList(torrentTable):
	returnList = []
	for i in torrentTable:
		data = i.find_all("td")
		links = data[2].find_all("a")
		torrentSize = float(data[4].string.split()[0])
		sizeUnit = data[4].string.split()[1].lower()
		torrentName = links[2].string
		torrentID = links[3].get("href").split("=")[2]

		for char in '\/:*?"<>|':
			if char in torrentName:
				torrentName.replace(char, "-")

		if (sizeUnit == "mb" and torrentSize > 100):
			torrentSize = torrentSize / 1024
			returnList.append((torrentName, torrentSize, torrentID))
		elif sizeUnit == "gb":
			returnList.append((torrentName, torrentSize, torrentID))
		else:
			continue
	return returnList

def getTorrentIDs(page, limit = None):
	html = s.get(browseURL % str(page)).text
	soup = bs4.BeautifulSoup(html)
	torrentTable = soup.find(id = "torrent_table").find_all("tr")[1:]
	if limit == None:
		return constructTorrentList(torrentTable)
	else:
		return constructTorrentList(torrentTable[:limit])

def downloadTorrents(downloadList):
	for no, i in enumerate(downloadList):
		filename = str(no) + ".torrent"
		print("Downloading: %s --- Size: %0.3f GB" % (i[0], i[1]))
		f = open(filename, "ab+")
		f.write(s.get(downloadURL % i[2]).content)
		f.close()

def main():

	global s, baseURL, browseURL, downloadURL

	baseURL = "https://broadcasthe.net"
	browseURL = "https://broadcasthe.net/torrents.php?page=%s&action=basic&order_by=size&order_dir=asc"
	downloadURL = "https://broadcasthe.net/torrents.php?action=download&id=%s"
	
	### IMPORTANT ###
	### Start value might change in the future, check the forum topic for more information
	start = 58

	username = input("BTN Username: ")
	password = input("BTN Password: ")

	print("-" * 80)

	s = requests.session()

	loginDetails = {"username": username, "password": password, "login": "Log In!", "keeplogged": "1"}
	headers = {"User-Agent": "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1"}

	login(baseURL, loginDetails, headers)
	userID = getUserID()
	remaining = 3000 - getSnatchCount(userID)
	torrentsPerPage = getTorrentsPerPage(userID)
	group = 1
	os.mkdir("BTN - " + str(group))
	os.chdir("BTN - " + str(group))
	groupDownload = []
	groupTorrentNumber = 0
	groupTorrentSize = 0

	totalDown = 0
	totalSize = 0

	report = []

	while True:
		if groupTorrentNumber > 299 or groupTorrentSize > 50 or remaining <= 0:
			totalDown += groupTorrentNumber
			totalSize += groupTorrentSize
			downloadTorrents(groupDownload)
			print("-" * 100)
			print("Changing directories and creating another group")
			print("-" *100)
			print("Stats for folder BTN - %s:" % group)
			print("Torrents in this group: ", groupTorrentNumber)
			print("Total size of this group: ", groupTorrentSize)
			report.append((groupTorrentNumber, groupTorrentSize))
			print("-" * 100)
			groupDownload = []
			groupTorrentSize = 0
			groupTorrentNumber = 0
			group += 1
			if remaining > 0:
				os.chdir("..")
				os.mkdir("BTN - " + str(group))
				os.chdir("BTN - " + str(group))

		if remaining <= 0:
			break

		if remaining > torrentsPerPage:
			torrentList = getTorrentIDs(start)
			for ID in torrentList:
				groupDownload.append(ID)
				groupTorrentNumber += 1
				groupTorrentSize += ID[1]
			remaining -= len(torrentList)

		else:
			torrentList = getTorrentIDs(start, limit = remaining)
			for ID in torrentList:
				groupDownload.append(ID)
				groupTorrentNumber += 1
				groupTorrentSize += ID[1]
			remaining -= len(torrentList) 
		start += 1

	for i, j in enumerate(report):
		print("Stats for folder BTN - %s:" % (i + 1))
		print("Torrents in this group: ", j[0])
		print("Total size of this group: ", j[1])

	print("Downloaded %s torrents." % totalDown)
	print("Total space needed: %s GB" % totalSize)

if __name__ == "__main__":
	main()

