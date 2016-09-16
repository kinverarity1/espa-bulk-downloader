#!/usr/bin/env python

"""
Author: David Hill
Date: 01/31/2014
Purpose: A simple python client that will download all available (completed) scenes for
         a user order(s).

Requires: Python feedparser and standard Python installation.     

Version: 1.0

Changes: 

30 June 2016: Guy Serbin added support for Python 3.x and download progress indicators.
24 August 2016: Guy Serbin added:
1. The downloads will now tell you which file number of all available scenes is being downloaded.
2. Added a try/except clause for cases where the remote server closes the connection during a download.

"""
import argparse
import base64
import feedparser
import os
import random
import shutil
import sys
import time

is_py3 = True if sys.version_info[0] == 3 else False

if is_py3:
    import urllib.request as ul
else:
    import urllib2 as ul


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

        auth_str = "%s:%s" % (self.user, self.passw)
        if is_py3:
            auth_str = auth_str.encode()

        feed = feedparser.parse(self.feed_url, request_headers={"Authorization": base64.b64encode(auth_str)})

        num_downloads = len(feed.entries)
        if orderid != 'ALL':
            num_downloads = len([i for i in feed.entries if orderid in i['id']])
        print('There are a total of %d files available for download.' % num_downloads)

        if feed.status == 403:
            print("user authentication failed")
            exit()

        if feed.status == 404:
            print("there was a problem retrieving your order. verify your orderid is correct")
            exit()

        for index, entry in enumerate(feed.entries):
            # description field looks like this
            # 'scene_status:thestatus,orderid:theid,orderdate:thedate'
            scene_order = entry.description.split(',')[1].split(':')[1]

            # only return values if they are in the requested order
            if orderid == "ALL" or scene_order == orderid:
                yield Scene(entry.link, scene_order, index+1, num_downloads)

                
class Scene(object):
    
    def __init__(self, srcurl, orderid, filenum, numfiles):
        self.srcurl = srcurl
        self.orderid = orderid
        
        parts = self.srcurl.split("/")
        self.filename = parts[len(parts) - 1]
        
        self.name = self.filename.split('.tar.gz')[0]
        self.filenum = filenum
        self.numfiles = numfiles
        
                  
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
            print('Scene already exists on disk, skipping.')
            return
                    
        download_directory = self.directory_path(scene)
        
        # make sure we have a target to land the scenes
        if not os.path.exists(download_directory):
            os.makedirs(download_directory)
            print ("Created target_directory: %s " % download_directory)

        req = ul.Request(scene.srcurl)
        req.get_method = lambda: 'HEAD'

        head = ul.urlopen(req)
        file_size = int(head.headers['Content-Length'])

        first_byte = 0
        if os.path.exists(self.tmp_scene_path(scene)):
            first_byte = os.path.getsize(self.tmp_scene_path(scene))

        print ("Downloading %s, file number %d of %d, to: %s" % (scene.name, scene.filenum,
                                                                 scene.numfiles, download_directory))

        while first_byte < file_size:
            # Added try/except to keep the script from crashing if the remote host closes the connection.
            # Instead, it moves on to the next file.
            try:
                first_byte = self._download(first_byte)
                time.sleep(random.randint(5, 30))
            except Exception as e:
                print(str(e))
                break
        if first_byte >= file_size:
            os.rename(self.tmp_scene_path(scene), self.scene_path(scene))

    def _download(self, first_byte):
        req = ul.Request(scene.srcurl)
        req.headers['Range'] = 'bytes={}-'.format(first_byte)

        with open(self.tmp_scene_path(scene), 'ab') as target:
            source = ul.urlopen(req)
            shutil.copyfileobj(source, target)

        return os.path.getsize(self.tmp_scene_path(scene))


if __name__ == '__main__':
    epilog = ('ESPA Bulk Download Client Version 1.0.0. [Tested with Python 2.7]\n'
              'Retrieves all completed scenes for the user/order\n'
              'and places them into the target directory.\n'
              'Scenes are organized by order.\n\n'
              'It is safe to cancel and restart the client, as it will\n'
              'only download scenes one time (per directory)\n'
              ' \n'
              '*** Important ***\n'
              'If you intend to automate execution of this script,\n'
              'please take care to ensure only 1 instance runs at a time.\n'
              'Also please do not schedule execution more frequently than\n'
              'once per hour.\n'
              ' \n'
              '------------\n'
              'Examples:\n'
              '------------\n'
              'Linux/Mac: ./download_espa_order.py -e your_email@server.com -o ALL -d /some/directory/with/free/space\n\n'
              'Windows:   C:\python27\python download_espa_order.py -e your_email@server.com -o ALL -d C:\some\directory\with\\free\space'
              '\n ')

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

    print 'Retrieving Feed'
    for scene in SceneFeed(args.email, args.username, args.password, args.host).get_items(args.order):
        print('\nNow processing scene %s.' % scene.name)
        storage.store(scene)

