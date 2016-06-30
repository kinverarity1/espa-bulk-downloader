#!/usr/bin/env python

"""
Author: David Hill
Date: 01/31/2014
Purpose: A simple python client that will download all available (completed) scenes for
         a user order(s).

Requires: Python feedparser and standard Python installation.     

Version: 1.0
"""

import sys
import feedparser
if sys.version_info[0] !=3:
    import urllib2 as ul
else:
    import urllib.request as ul
import argparse
import shutil
import os
import time
import random
import base64


class SceneFeed(object):
    """SceneFeed parses the ESPA RSS Feed for the named email address and generates
    the list of Scenes that are available"""
    
    def __init__(self, email, username, password, host="http://espa.cr.usgs.gov"):
        """Construct a SceneFeed.
        
        Keyword arguments:
        email -- Email address orders were placed with
        host  -- http url of the RSS feed host
        """
        if not host:
            host = "http://espa.cr.usgs.gov"

        self.host = host
        self.email = email
        self.user = username
        self.passw = password

        self.feed_url = "%s/ordering/status/%s/rss/" % (self.host, self.email)

    def get_items(self, orderid='ALL'):
        """get_items generates Scene objects for all scenes that are available to be
        downloaded.  Supply an orderid to look for a particular order, otherwise all
        orders for self.email will be returned"""
        
        #yield Scenes with download urls

        auth_str = "%s:%s" % (self.user, self.passw)
        if sys.version_info[0] !=3:
            bauth = base64.b64encode(auth_str)
        else:
            bauth = base64.b64encode(auth_str.encode())

        feed = feedparser.parse(self.feed_url, request_headers={"Authorization": bauth})

        if feed.status == 403:
            print("user authentication failed")
            exit()

        if feed.status == 404:
            print("there was a problem retrieving your order. verify your orderid is correct")
            exit()

        for entry in feed.entries:

            #description field looks like this
            #'scene_status:thestatus,orderid:theid,orderdate:thedate'
            scene_order = entry.description.split(',')[1].split(':')[1]

            #only return values if they are in the requested order            
            if orderid == "ALL" or scene_order == orderid:
                yield Scene(entry.link, scene_order)
            
                
class Scene(object):
    
    def __init__(self, srcurl, orderid):
    
        self.srcurl = srcurl
    
        self.orderid = orderid
        
        parts = self.srcurl.split("/")
     
        self.filename = parts[len(parts) - 1]
        
        self.name = self.filename.split('.tar.gz')[0]
        
                  
class LocalStorage(object):
    
    def __init__(self, basedir):
        self.basedir = basedir

    def directory_path(self, scene):
        return ''.join([self.basedir, os.sep, scene.orderid, os.sep])
        
    def scene_path(self, scene):
        return ''.join([self.directory_path(scene), scene.filename])
    
    def tmp_scene_path(self, scene):
        return ''.join([self.directory_path(scene), scene.filename, '.part'])
    
    def is_stored(self, scene):        
        return os.path.exists(self.scene_path(scene))        
    
    def store(self, scene):
        
        if self.is_stored(scene):
            return
                    
        download_directory = self.directory_path(scene)
        
        #make sure we have a target to land the scenes
        if not os.path.exists(download_directory):
            os.makedirs(download_directory)
            print ("Created target_directory:%s" % download_directory)
        
        req = ul.Request(scene.srcurl)
        req.get_method = lambda: 'HEAD'

        head = ul.urlopen(req)
        file_size = int(head.headers['Content-Length'])

        if os.path.exists(self.tmp_scene_path(scene)):
            first_byte = os.path.getsize(self.tmp_scene_path(scene))
        else:
            first_byte = 0

        print ("Downloading %s to %s" % (scene.name, download_directory))

        while first_byte < file_size:
            first_byte = self._download(first_byte)
            time.sleep(random.randint(5, 30))

        os.rename(self.tmp_scene_path(scene), self.scene_path(scene))

    def _download(self, first_byte):
        req = ul.Request(scene.srcurl)
        req.headers['Range'] = 'bytes={}-'.format(first_byte)

        with open(self.tmp_scene_path(scene), 'ab') as target:
            source = ul.urlopen(req)
            shutil.copyfileobj(source, target)

        return os.path.getsize(self.tmp_scene_path(scene))


if __name__ == '__main__':
    e_parts = ['ESPA Bulk Download Client Version 1.0.0. [Tested with Python 2.7]\n']
    e_parts.append('Retrieves all completed scenes for the user/order\n')
    e_parts.append('and places them into the target directory.\n')
    e_parts.append('Scenes are organized by order.\n\n')
    e_parts.append('It is safe to cancel and restart the client, as it will\n')
    e_parts.append('only download scenes one time (per directory)\n')
    e_parts.append(' \n')
    e_parts.append('*** Important ***\n')
    e_parts.append('If you intend to automate execution of this script,\n')
    e_parts.append('please take care to ensure only 1 instance runs at a time.\n')
    e_parts.append('Also please do not schedule execution more frequently than\n')
    e_parts.append('once per hour.\n')
    e_parts.append(' \n')
    e_parts.append('------------\n')
    e_parts.append('Examples:\n')
    e_parts.append('------------\n')
    e_parts.append('Linux/Mac: ./download_espa_order.py -e your_email@server.com -o ALL -d /some/directory/with/free/space\n\n') 
    e_parts.append('Windows:   C:\python27\python download_espa_order.py -e your_email@server.com -o ALL -d C:\some\directory\with\\free\space')
    e_parts.append('\n ')
    epilog = ''.join(e_parts)
 
    parser = argparse.ArgumentParser(epilog=epilog, formatter_class=argparse.RawDescriptionHelpFormatter)
    
    parser.add_argument("-e", "--email", 
                        required=True,
                        help="email address for the user that submitted the order)")
                        
    parser.add_argument("-o", "--order",
                        required=True,
                        help="which order to download (use ALL for every order)")
                        
    parser.add_argument("-d", "--target_directory",
                        required=True,
                        help="where to store the downloaded scenes")

    parser.add_argument("-u", "--username",
                        required=True,
                        help="EE/ESPA account username")

    parser.add_argument("-p", "--password",
                        required=True,
                        help="EE/ESPA account password")

    parser.add_argument("-v", "--verbose",
                        required=False,
                        help="be vocal about process")

    parser.add_argument("-i", "--host",
                        required=False)


    args = parser.parse_args()
    
    storage = LocalStorage(args.target_directory)
    
    print('Retrieving Feed')
    for scene in SceneFeed(args.email, args.username, args.password, args.host).get_items(args.order):
        storage.store(scene)
