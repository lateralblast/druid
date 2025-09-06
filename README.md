![alt tag](https://raw.githubusercontent.com/lateralblast/druid/master/druid.jpg)

DRUID
=====

Dell Retrieve Update Information and Download

Version: 0.4.9

A python script to parse Dell firmware page for a particular PowerEdge model to get the available firmware.
It can also automate the download of the firmware.

Previously this script used PhantomJS, it has been updated to use the Chrome headless driver in Selenium.

By default the script will fetch only the lastest driver information.
To fetch a full list the --all switch can be used.

If given a specific model it will parse the firmware page for that model, eg for the R610:

https://www.dell.com/support/home/en-au/product-support/product/poweredge-r610/drivers

License
-------

CC BY-SA: https://creativecommons.org/licenses/by-sa/4.0/

Fund me here: https://ko-fi.com/richardatlateralblast

Notice
------

Since the recent website update the servicetag feature is no longer working.
This requires further investigation as it requires clicking on a hidden element
with a javascript(void) function, and none of the usual methods work.

I'm adding redfish support to the script to get information from the iDRAC.
The Ruby redfish client module does not have all the features I need,
therefore I am depricating the Ruby script and moving to Python.

Requirements
------------

I've added code to install chromedriver automatically, but if there are issues on MacOS
you can try installing it manually. 

Required applications:

- chromedriver

On Mac OS, you may need to disable quarantine on the executable. e.g.:

```
brew install --cask chromedriver
xattr -d com.apple.quarantine /opt/homebrew/bin/chromedriver
```

Required standard Python modules:

- urllib.request
- subprocess
- platform
- argparse
- time
- sys
- os
- re

Required additional Python modules:

- terminaltables 
- paraminko
- pygments
- selenium
- pexpect
- lxml
- wget
- bs4

If not installed, the script will attempt to install the required modules.

License
-------

This software is licensed as CC-BA (Creative Commons By Attrbution)

http://creativecommons.org/licenses/by/4.0/legalcode

Usage
-----

```
$ ./druid.py --help
usage: druid.py [-h] [--ip IP] [--ext EXT] [--get GET] [--set SET] [--type TYPE] [--model MODEL] [--fwdir FWDIR] [--check CHECK]
                [--search SEARCH] [--output OUTPUT] [--value VALUE] [--method METHOD] [--workdir WORKDIR] [--driverid DRIVERID]
                [--platform PLATFORM] [--username USERNAME] [--password PASSWORD] [--servicetag SERVICETAG] [--all] [--ssh] [--json] [--list]
                [--mask] [--ping] [--text] [--force] [--print] [--quiet] [--tables] [--update] [--options] [--version] [--verbose]
                [--download] [--nonheadless]

options:
  -h, --help            show this help message and exit
  --ip IP
  --ext EXT
  --get GET
  --set SET
  --type TYPE
  --model MODEL
  --fwdir FWDIR
  --check CHECK
  --search SEARCH
  --output OUTPUT
  --value VALUE
  --method METHOD
  --workdir WORKDIR
  --driverid DRIVERID
  --platform PLATFORM
  --username USERNAME
  --password PASSWORD
  --servicetag SERVICETAG
  --all
  --ssh
  --json
  --list
  --mask
  --ping
  --text
  --force
  --print
  --quiet
  --tables
  --update
  --options
  --version
  --verbose
  --download
  --nonheadless
  ```

Examples
--------

Get ServiceTag warranty information:

```
$ ./druid.py --servicetag XXXXXX

Warranty
Expires  28 OCT. 2027
```

Get ServiceTag config (creates a CSV file in the default directory with the service tag, e.g. XXXXXXX.csv, then formats it):

```
$ ./druid.py --servicetag XXXXXXX --get config

800-12254 : Country Info Mod (AUSTRALIA)
1x  0P216 MOD,INFO,AUS,SPEC,APCC
0x  9N534 INFO,COUNTRY,AUSTRALIA,APCC
780-13169 : C3 - RAID 1 for H710p/H710/H310 (2 HDDs)
1x  YPV38 Module,Information,C3,MSSR1,R720
0x  7FHF9 INFO,PER720,CONFIG3,MSSR1
770-12962 : ReadyRails 2U Sliding Rails
1x  26P86 Module,Rack Rail,Ready Rails,2U,Slide,Slim Form Factor,V3
770-12959 : 2U Cable Management Arm
1x  44F09 Module,Rack Rail,Cable Management Arm,2U,Long,V3
696-10323 : Optional DAPC(Dell Active Power Controller) Power Savings BIOS Setting
1x  7X7C7 Module,Information,DAPC,ENBL  PWR SAVINGS
0x  HNR52 INFO,DAPC,ENBL PWR SAVINGS MD
0x  HNR52 INFO,DAPC,ENBL PWR SAVINGS MD
611-10043 : No Operating System
1x  KD483 Module,Software,NO-OS
0x  1U112 SRV,SW,DELL,NULL-OS
0x  1U112 SRV,SW,DELL,NULL-OS
...
```

Get ServiceTag config and output in table format:

```
$ ./druid.py --servicetag XXXXXX --get config --tables
┌───────────┬───────┬───────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Qty/Item  │ P/N   │ Description                                                                                                   │
├───────────┼───────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 800-12254 │ ----- │ Country Info Mod (AUSTRALIA)                                                                                  │
├───────────┼───────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 1x        │ 0P216 │ MOD,INFO,AUS,SPEC,APCC                                                                                        │
├───────────┼───────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 0x        │ 9N534 │ INFO,COUNTRY,AUSTRALIA,APCC                                                                                   │
├───────────┼───────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 780-13169 │ ----- │ C3 - RAID 1 for H710p/H710/H310 (2 HDDs)                                                                      │
├───────────┼───────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 1x        │ YPV38 │ Module,Information,C3,MSSR1,R720                                                                              │
├───────────┼───────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 0x        │ 7FHF9 │ INFO,PER720,CONFIG3,MSSR1                                                                                     │
├───────────┼───────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 770-12962 │ ----- │ ReadyRails 2U Sliding Rails                                                                                   │
├───────────┼───────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 1x        │ 26P86 │ Module,Rack Rail,Ready Rails,2U,Slide,Slim Form Factor,V3                                                     │
├───────────┼───────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
...
```

Get the available M630 BIOS firmware:

```
$ ./druid.py --model r630 --type bios

Dell Server PowerEdge BIOS R630/R730/R730XD Version 2.17.0
https://dl.dell.com/FOLDER09857656M/1/BIOS_MC31G_WN64_2.17.0.EXE

Dell Server PowerEdge BIOS R630/R730/R730XD Version 2.17.0 - A GnuPG file which contains a cryptographic signature
https://dl.dell.com/FOLDER09857653M/1/BIOS_MC31G_LN64_2.17.0.BIN.sign

Dell Server PowerEdge BIOS R630/R730/R730XD Version 2.17.0 - A self-extracting file for use in 64-bit machines
https://dl.dell.com/FOLDER09783485M/1/R730-021700.efi

Dell Server PowerEdge BIOS R630/R730/R730XD Version 2.17.0 - An archive of PDF files to provide help and procedural information to the customers
https://dl.dell.com/FOLDER09892754M/2/R730_R730XD_R630_BIOS_2.17.0.pdf

Dell Server PowerEdge BIOS R630/R730/R730XD Version 2.17.0 - Update Package for Red Hat Linux
https://www.dell.com/learn/us/en/uscorp1/terms-of-sale-consumer-license-agreements

```

List all types of BIOS downloads:

```
./druid.py --model r630 --type BIOS --list

Dell Server PowerEdge BIOS R630/R730/R730XD Version 2.19.0
https://www.dell.com/support/home/en-us/drivers/driversdetails?driverid=km6p8
https://dl.dell.com/FOLDER11275684M/1/BIOS_KM6P8_WN64_2.19.0.EXE
https://dl.dell.com/FOLDER11275686M/1/BIOS_KM6P8_LN64_2.19.0.BIN.sign
https://dl.dell.com/FOLDER11275494M/1/R730-021900C.efi
https://dl.dell.com/FOLDER11294778M/1/R730_R730XD_R630_BIOS_2.19.0.pdf
https://dl.dell.com/FOLDER11275682M/1/BIOS_KM6P8_LN64_2.19.0.BIN
```

List all types of BIOS downloads with efi extensions:

```
Dell Server PowerEdge BIOS R630/R730/R730XD Version 2.19.0
https://www.dell.com/support/home/en-us/drivers/driversdetails?driverid=km6p8
https://dl.dell.com/FOLDER11275494M/1/R730-021900C.efi
```

Search for EFI related firmware in all results:

```
$ ./druid.py --model r630 --search efi

Dell Server PowerEdge BIOS R630/R730/R730XD Version 2.17.0 - A self-extracting file for use in 64-bit machines
https://dl.dell.com/FOLDER09783485M/1/R730-021700.efi
```

Get available R630 documentation:

```
$ ./druid.py --model r630 --type manual

PowerEdge r630:
https://dl.dell.com/topicspdf/poweredge-r630_owners-manual_en-us.pdf
https://downloads.dell.com/manuals/all-products/esuprt_ser_stor_net/esuprt_poweredge/poweredge-r630_setup%20guide_en-us.pdf

```

Download EFI BIOS update for R630:

```
$ ./druid.py --model r630 --type BIOS --ext efi --download

Dell Server PowerEdge BIOS R630/R730/R730XD Version 2.19.0
https://www.dell.com/support/home/en-us/drivers/driversdetails?driverid=km6p8
https://dl.dell.com/FOLDER11275494M/1/R730-021900C.efi
Downloading https://dl.dell.com/FOLDER11275494M/1/R730-021900C.efi to /home/user/druid/r630/R730-021900C.efi
```
