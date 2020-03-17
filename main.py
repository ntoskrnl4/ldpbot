from client import client
from key import token


# To load new modules, copy/paste the line below, uncommented, with X filled in for the name of your file
# from modules import X

from modules import about
from modules import exit
from modules import info
from modules import livepatch
from modules import markov
from modules import mc
from modules import message_log
from modules import music
from modules import ping
from modules import pingreact
from modules import server
from modules import stats
from modules import whitelist
client.run(token)
