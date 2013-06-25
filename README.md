Requirements
====================
This script depends on the following modules:
###requests
You can get the source code for requests on [Github](http://github.com/kennethreitz/requests).
Or you can install it on your system with 
> sudo pip install requests

###BeautifulSoup4
You can get the source code for [BeautifulSoup4](http://www.crummy.com/software/BeautifulSoup/bs4/download/).
Or you can install it on your system with
> sudo pip install beautifulsoup4

Usage
====================
Ideally you should run the script from an empty directory so that things don't get messy after the script runs to completion. You can run the script with
> python BTNsnatcher.py
from the directory where the script is stored.

*__Important note__*
If you want to be gentle on the site and want the script to take less time to complete operation, please set your torrents per page and snatches per page to the value of "100" from your profile editing page. 

The script will run even if you ignore this part

What it does
====================
The script will ask you for your username and password (both of which are not stored anywhere or sent anywhere, so it is safe to use) and then will determine how many snatches you need to get to the 3000 snatches mark. It will compile a list of all your snatches to date and will not download torrents that you have already snatched as those will not count towards your snatched count. It will ask you whether you want to downlaod extra torrents so that you don't get demoted to a lower class if some of the torrents you have downloaded are deleted from the site in the future. After determining the torrent IDs, it will prompt the user asking if it should start downloading the torrent files to a folder called "BTNsnatcher_torrents". After all torrents have been downloaded, it reports how much space you will need to download all of the torrent files.

New Features
====================
* Ability to get the snatched list from the site so that the script doesn't download the torrents that you have already snatched.
* Error handling for the most common problems. If the program ends unexpectedly due to parsing errors, the script will save the last page it visited in an html file called lastPage.html so that you can load it in your browser and see what the problem was.
* time.sleep() commands so that the errors received from the site are minimized. BTN doesn't allow browsing multiple pages in less than 1 second so there are now sleep commands in certain points in the script which will hopefully minimize the amount of errors received.
* Ability to work without any manipulation to the source code. (The first version of the script needed the user to predetermine a page number to start browsing but this has been removed and the script takes care of this by itself now.)

To Do
====================
* Code cleanup
* Ability to move torrents to a specified watch folder batch by batch
* Ability to predict how much time it will take for the user to accumulate enough points for the Master class.
* Any reasonable suggestions
