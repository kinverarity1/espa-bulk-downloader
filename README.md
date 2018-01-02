# espa-bulk-downloader

Automatically downloads all completed espa scenes.  Each scene is downloaded to the `--target_directory` and organized by order.

# Installation
* Note: These were tested with both python 2.7.13 and 3.6.5.

* Clone this repository:
```
git clone https://github.com/USGS-EROS/espa-bulk-downloader.git bulk-downloader
cd bulk-downloader
python ./download_espa_order.py -h
```
* Install with pip automatically:
```
pip install git+https://github.com/USGS-EROS/espa-bulk-downloader.git
download_espa_order.py -h
```
* Alternatively you can just download the stand alone zip file which only requires python to run

### Runtime options

Argument | Description
---|---
`-e or --email` | The email address used to submit the order
`-o or --order` | The order you wish to download.  (`ALL` or ESPA order-id)
`-d or --target_directory` | The local directory to store downloaded scenes
`-u or --username` | Your ERS username
`-p or --password` | Your ERS password
`-c or --checksum` | Download checksum files (will also compare the contents)

Linux/Mac Example: `python ./download_espa_order.py -e your_email@server.com -d /some/directory/with/free/space -u foo -p bar`

Windows Example: `C:\python27\python download_espa_order.py -e your_email@server.com -d C:\some\directory\with\free\space -u foo -p bar`

# Notes
Retrieves all completed scenes for the user/order
and places them into the target directory.
Scenes are organized by order.

It is safe to cancel and restart the client, as it will
only download scenes one time (per directory)
 
If you intend to automate execution of this script,
please take care to ensure only 1 instance runs at a time.
Also please do not schedule execution more frequently than
once per hour.


#### Support Information

This project is unsupported software provided by the U.S. Geological Survey (USGS) Earth Resources Observation and Science (EROS) Land Satellite Data Systems (LSDS) Project. For questions regarding products produced by this source code, please contact us at [custserv@usgs.gov][2].

#### Disclaimer

This software is preliminary or provisional and is subject to revision. It is being provided to meet the need for timely best science. The software has not received final approval by the U.S. Geological Survey (USGS). No warranty, expressed or implied, is made by the USGS or the U.S. Government as to the functionality of the software and related material nor shall the fact of release constitute any such warranty. The software is provided on the condition that neither the USGS nor the U.S. Government shall be held liable for any damages resulting from the authorized or unauthorized use of the software.


[2]: mailto:custserv@usgs.gov
    
