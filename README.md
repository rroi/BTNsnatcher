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
python BTNsnatcher.py
from the directory where the script is stored.

*__Important note__*
If you don't care about downloading a little bit more data, you can safely ignore this. If you do care, please read below.

If you look in the script you will see a variable called start in the main() function. This variable determines on which page the parsing will start. Page 58 is the first place where 100 MB torrents start to appear so the start variable has been assigned a value of 58. It is a good idea to check [this link](https://broadcasthe.net/torrents.php?page=58&action=basic&order_by=size&order_dir=asc) and determine this value yourself. Apart from this the script doesn't have any configurations. 

What it does
====================
The script will ask you for your username and password (both of which are not stored anywhere or sent anywhere, so it is safe to use) and then will determine how many snatches you need to get to the 3000 snatches mark and start parsing the above link and going forwards from there until enough torrent information has been parsed. It currently groups downloaded torrents into folders so that when you move the torrents to a watch folder your client doesn't get overwhelmed. Currently, the script creates new folder every 300 hundred torrents, if you want to increase this, you can always modify this number at line 117.
When the script downloads enough torrents, it will report how many torrents it has downloaded and how much space you will need to download all of this information.

To Do
====================
* Code cleanup
* Ability to move torrents to a specified watch folder batch by batch
* Ability to predict how much time it will take for the user to accumulate enough points for the Master class.
* Any reasonable suggestions
