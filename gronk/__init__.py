"""
The init just contain versioning data.
"""

from collections import namedtuple

# get the raw PKG-INFO data
from pkg_resources import get_distribution
pkgInfo = get_distribution('gronk').get_metadata('PKG-INFO')

# parse it using email.Parser
from email import message_from_string
msg = message_from_string(pkgInfo)
inftuple = namedtuple('gronkinfo','author version year')
info = inftuple(msg['Author'],msg['Version'],'2018')
