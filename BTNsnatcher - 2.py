import requests
import bs4
import time
import os
import shutil

class User(object):

	def __init__(self, uname, password, snatched = None, tlist = [], slist = []):
		self.loginDetails = {"username": uname, "password": password, "login": "Log In!", "keeplogged": "1"}
		self.headers = {"User-Agent": "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1"}
		self.username = uname
		self.password = password
		self.snatchedList = slist
		self.torrentList = tlist
		self.spaceNeeded = 0
		self.session = requests.session()
		self._login()
		### THIS MIGHT NEED TO CHANGE
		self.userID = self._getUserID()
		print "Successfully logged in to the site!\n"
		### THIS MIGHT NEED TO CHANGE
		self._getUserDetails()

	def _login(self):
		loginURL = "https://broadcasthe.net/login.php"
		self.page = self.session.post(loginURL, data = self.loginDetails, headers = self.headers)
		time.sleep(2)

	def _getUserID(self):
		self.page = self.session.get("https://broadcasthe.net/index.php").text
		soup = bs4.BeautifulSoup(self.page)
		info = soup.find(id = "userinfo_username")
		userID = info.li.a.get("href").split("=")[1]
		time.sleep(2)
		return userID

	def _getUserDetails(self):
		profileURL = "https://broadcasthe.net/user.php?id=%s" % self.userID
		self.page = self.session.get(profileURL).text
		soup = bs4.BeautifulSoup(self.page).find(id = "section2").div
		statistics = soup.find_all("div")[1]
		upDownStats = statistics.find_all("div")[2].ul
		uploadsSnatched = int(upDownStats.find_all("li")[2].string.split(":")[1].strip())
		seed = upDownStats.find_all("li")[4].string.split(":")[1].strip()
		downSnatched = int(upDownStats.find_all("li")[7].contents[0][:-1].split(":")[1].strip())
		snatched = uploadsSnatched + downSnatched
		seedNo = float(seed.split()[0].replace(",", ""))
		seedStr = seed.split()[1]
		if seedStr.lower() == "mb":
			seedSize = seedNo / 1024.0
		elif seedStr.lower() == "gb":
			seedSize = seedNo
		elif seedStr.lower() == "tb":
			seedSize = seedNo * 1024.0
		else:
			seedSize = 0
		first = statistics.find_all("div")[0].ul
		userClass = first.find_all("li")[1].string.split(":")[1].strip()
		bonusPoints = float(first.find_all("a")[0].string.replace(",", ""))
		bonusRate = float(first.find_all("li")[5].string.split(":")[1].strip().replace(",", ""))
		self.snatchedNumber = snatched
		self.seedSize = seedSize
		self.userClass = userClass
		self.bonusPoints = bonusPoints
		self.needed = 3000 - snatched
		self.bonusRate = float(bonusRate)
		time.sleep(2)

	def _getSnatchList(self):
		start = 1
		URL = "https://broadcasthe.net/torrents.php?page=%s&order_by=s3&order_way=DESC&type=snatched&userid=%s&foreign=2"
		self.page = self.session.get(URL % (start, self.userID)).text
		soup = bs4.BeautifulSoup(self.page)
		links = soup.find(id = "content").find_all(class_ = "linkbox")[0]
		last = int(links.find_all("a")[-1].get("href").split("&", 1)[0].split("=")[1])
		while start <= last:
			self.page = self.session.get(URL % (start, self.userID)).text
			soup = bs4.BeautifulSoup(self.page)
			torrentTable = soup.find(id = "torrent_table").find_all("tr")[1:]
			for torrent in torrentTable:
				torrentID = torrent.find_all("a")[3].get("href").split("=")[2]
				self.snatchedList.append(torrentID)
			start += 1
			time.sleep(2)

	def _getTorrentsPerPage(self):
		URL = "https://broadcasthe.net/user.php?action=edit&userid=%s" % self.userID
		self.page = self.session.get(URL).text
		self.page = self.page.replace('selected="selected"'," selected")
		soup = bs4.BeautifulSoup(self.page)
		perPageOption = soup.find(id = "torperpage")
		options = perPageOption.find_all("option")
		for option in options:
			if "selected" in str(option):
				return int(option.string)
		time.sleep(2)

	def _addToTorrentList(self, torrentTable):
		add = 0
		for i in torrentTable:
			data = i.find_all("td")
			links = data[2].find_all("a")
			torrentSize = float(data[4].string.split()[0])
			sizeUnit = data[4].string.split()[1].lower()
			torrentName = links[2].string
			torrentID = links[3].get("href").split("=")[2]
			if ((sizeUnit == "mb") and torrentSize <100) or torrentID in self.snatchedList:
				continue
			else:
				torrentSize = torrentSize * int(sizeUnit == "mb") / 1024.0 or torrentSize
				self.torrentList.append((torrentName, torrentSize, torrentID))
				self.needed -= 1
				add += 1
			if self.needed == 0:
				print "Added %s torrents to the TorrentList" % add
				return "done"
		return add

	def _getTorrentIDs(self):
		browseURL = "https://broadcasthe.net/torrents.php?page=%s&order_by=s4&order_way=ASC&searchstr=&searchtags=&excludesearchtags=&foreign=2"
		start = (2700 / self._getTorrentsPerPage()) + 1
		while True:
			print "Browsing page %s" % start
			self.page = self.session.get(browseURL % start).text
			soup = bs4.BeautifulSoup(self.page)
			torrentTable = soup.find(id = "torrent_table").find_all("tr")[1:]
			add = self._addToTorrentList(torrentTable)
			if add == "done":
				break
			print "Added %s torrents to the TorrentList" % add
			print self.needed
			start += 1
			time.sleep(2)

	def _downloadTorrents(self):
		downloadURL = "https://broadcasthe.net/torrents.php?action=download&id=%s"
		for name, torrent in enumerate(self.torrentList):
			filename = "BTN%s" % name + ".torrent"
			print "Downloading: %s --- Size: %0.3f GB" % (torrent[0], torrent[1])
			f = open(filename, "ab+")
			down = self.session.get(downloadURL % torrent[2])
			f.write(down.content)
			f.close()
			self.spaceNeeded += torrent[1]

	def _getInput(self):
		q = raw_input("Would you like to download extra torrents? (y/n) ")
		if q.lower() == "y" or q.lower() == "yes":
			extra = raw_input("How much more would you like to download? ")
			try:
				extra = int(extra)
				if extra > 1000:
					print "That is quite a large number, your extra download amount has been set to 500."
					extra = 500
			except ValueError:
				print "That is not an acceptable number"
				self._getInput()
		else:
			extra = 0
		return extra

	def bonus(self):
		userClasses = ("user", "member", "power user", "extreme user", "elite", "guru", "master")
		bonusReq = (0, 100000, 250000, 500000, 850000, 1500000, 3000000)
		currentClass = userClasses.index(self.userClass.lower())
		nextClass = currentClass + 1
		bonusNeed = bonusReq[nextClass] - self.bonusPoints
		for i in bonusReq[nextClass + 1:]:
			bonusNeed += i
		if bonusNeed <= 0:
			print "You already have enough points to be promoted to Master user class."
			return
		print "You need %s bonus points to get to the Master user class." % bonusNeed

		self.page = self.session.get("https://broadcasthe.net/bonus.php?action=rate").text
		soup = bs4.BeautifulSoup(self.page)
		seedTable = soup.find(id = "myTable").find_all("tr")[1:]
		episodeSize = 0
		episodePoint = 0
		seasonSize = self.seedSize
		for seed in seedTable:
			torrent = seed.find_all("td")
			if torrent[1].string == "Episode":
				size, unit = torrent[2].string.split()
				if unit.lower() == "mb":
					a = float(size.replace(",", "")) / 1024.0
				else:
					a = float(size.replace(",", ""))
				seasonSize -= float(a)
				episodeSize += float(a)
				episodePoint += float(torrent[-1].string.replace(",", ""))
			else:
				continue

		print "You are earning %s per month from episodes" % episodePoint
		print "You are earning %s per month from season packs." % (self.bonusRate - episodePoint)

		print seasonSize

		a = 1500 * .15 * seasonSize
		b = a + self.bonusRate
		c = -bonusNeed
		x = (-b + ((b**2 - (4 * a * c)) ** 0.5)) / (2 * a)

		print "At your current seeding size, you need %0.1f months (around %0.1f days) to get enough points for Master" % (x, x * 30)
		print
		print "If you have a number of months at the end of which you wish to have enough points please enter that number."
		while True:
			try:
				months = float(raw_input("Number of months at the end of which you will have enough points for Master: "))
				if months >= x:
					print "You are already seeding enough to accumulate points for Master user class in %s months." % months
				else:
					d = bonusNeed - (months * self.bonusRate) - ((months * months + months) * 0.15 * 1500 * seasonSize)
					e = (0.15 * 3000 * months + ((months * months + months) * 0.15 * 1500))
					new = d / e
					print "You will need to seed %0.1f GB more in SEASON packs in order to get enough points for Master user class in %s months. \n" % (new, months)
				ch = raw_input("Would you like to try with another number of months? (y/n)")
				if ch.lower() != "y":
					break
			except:
				print "You haven't entered a number.\n"

	def snatch(self):
		time.sleep(1)
		raw_input("Press return to begin the initialization process. ")
		if self.needed <= 0:
			print "You have already snatched enough torrents for the Master user class requirements."
			return
		print "*" * 50
		print ">>> You have snatched %s torrent(s) to date." % self.snatchedNumber
		print ">>> You need to snatch %s torrent(s) in order to meet the Master user class requirement." % self.needed
		print 
		print ">>> Now populating your snatch list so that we don't download torrents you have already snatched."
		print ">>> This may take a while depending on the size of your snatch list."
		print
		time.sleep(1)
		self._getSnatchList()
		print ">>> %s torrent(s) have been added to your snatch list." % len(self.snatchedList)
		print
		print ">>> When a torrent you have snatched is deleted from the site, your snatch count will decrease."
		print ">>> in order to protect yourself against this risk you can opt to download more than your current"
		print ">>> need. For this reason, it is suggested that you download a bit more than you need."
		print
		extra = self._getInput()
		self.needed += extra
		print "*" * 50
		print ">>> Now populating your to-download list with %s torrent(s)." % self.needed
		print ">>> This may take a while depending on your snatch requirement."
		self._getTorrentIDs()
		print ">>> %s torrent(s) have been added to your to-download list." % len(self.torrentList)
		print
		raw_input("Press return to begin downloading the torrent files. ")
		try:
			os.mkdir("BTNsnatcher_torrents")
		except OSError, err:
			if str(err) == "[Errno 17] File exists: 'BTNsnatcher_torrents'":
				os.chdir("BTNsnatcher_torrents")
				path = os.getcwd()
				os.chdir("..")
				shutil.rmtree(path)
				os.mkdir("BTNsnatcher_torrents")
				pass
			else:
				print "Please delete the 'BTNsnatcher_torrents' folder from the working directory and rerun the script."
		os.chdir("BTNsnatcher_torrents")
		self._downloadTorrents()
		print "*" * 50
		print
		print "Finished downloading %s torrents from BTN. You will need a total space of %0.3f GBs to download all of these torrents." % (len(self.torrentList), self.spaceNeeded)
		print
		print "*" * 50
		print "All done! Have a nice day!"


def main():
	try:
		print "Welcome to BTNsnatcher" 
		print "*" * 50
		username = raw_input("BTN username: ")
		password = raw_input("BTN password: ")
		print
		user = User(username, password)
		print "Your user ID: %s" % user.userID
		print
		print "What would you like to do?"
		print "Press 1 for time estimation to accumulate enough points for promotion to Master user class."
		print "Press 2 to snatch torrents."
		while True:
			ch = raw_input("Your choice? ")
			if ch == "1":
				print
				print "*" * 50
				user.bonus()
				print "*" * 50
				print
				ch2 = raw_input("Would you like to snatch torrents as well? (y/n) ")
				if ch2.lower() == "y":
					user.snatch()
				else:
					print "All done! Have a nice day!"
				break
			elif ch == "2":
				user.snatch()
				break
			else:
				print "That is not a valid choice, please choose 1 for the bonus point program"
				print "or choose 2 to snatch torrents."
	except AttributeError, err:
		print err
		print "Something has gone wrong."
		print "I'm saving the last page I visited in the same directory I'm running in."
		f = open("lastPage.html", "a+")
		f.truncate()
		f.write(user.page)
		f.close() 

if __name__ == "__main__":
	main()
