![alt tag](https://raw.githubusercontent.com/lateralblast/druid/master/druid.jpg)

DRUID
=====

Dell Retrieve Update Information and Download

Version: 0.4.2

A python script to parse Dell firmware page for a particular PowerEdge model to get the available firmware.
It can also automate the download of the firmware.

Previously this script used PhantomJS, it has been updated to use the Chrome headless driver in Selenium.

By default the script will fetch only the lastest driver information.
To fetch a full list the --all switch can be used.

If given a specific model it will parse the firmware page for that model, eg for the R610:

https://www.dell.com/support/home/en-au/product-support/product/poweredge-r610/drivers

Notice
------

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

Python:

```
$ ./druid.py --help
usage: druid.py [-h] [--ip IP] [--get GET] [--set SET] [--type TYPE] [--model MODEL] [--fwdir FWDIR] [--check CHECK] [--search SEARCH]
                [--output OUTPUT] [--value VALUE] [--method METHOD] [--workdir WORKDIR] [--platform PLATFORM] [--username USERNAME]
                [--password PASSWORD] [--servicetag SERVICETAG] [--all] [--ssh] [--json] [--mask] [--ping] [--text] [--force] [--print]
                [--tables] [--update] [--options] [--version] [--verbose] [--download] [--nonheadless]

options:
  -h, --help            show this help message and exit
  --ip IP
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
  --platform PLATFORM
  --username USERNAME
  --password PASSWORD
  --servicetag SERVICETAG
  --all
  --ssh
  --json
  --mask
  --ping
  --text
  --force
  --print
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

Download BIOS:

```
$ ./druid.py --model r630 --type BIOS --download --verbose

Dell Server PowerEdge BIOS R630/R730/R730XD Version 2.19.0
https://www.dell.com/support/home/en-us/drivers/driversdetails?driverid=km6p8
https://dl.dell.com/FOLDER11275494M/1/R730-021900C.efi
Downloading https://dl.dell.com/FOLDER11275494M/1/R730-021900C.efi to /home/user/druid/r630/R730-021900C.efi
```

List latest availabe firmware/software for R610:

```
$ ./druid.py --model r610

Dell Server BIOS R610 Version 6.6.0  UrgentDell Server BIOS R610 Version 6.6.0  Urgent, BIOS, 09 Jul 2018
https://dl.dell.com/FOLDER05012920M/2/BIOS_0YV9D_WN64_6.6.0_01.EXE

Intel 5500/5520 Chipset Software Installation UtilityIntel 5500/5520 Chipset Software Installation Utility, Chipset, 06 Feb 2012
https://dl.dell.com/FOLDER94260M/12/INTEL_5500-5520-CHIPSET-SOFT_A03_R295077.exe

Dell EMC SupportAssist Enterprise Version 2.0.50 Windows Management ServerDell EMC SupportAssist Enterprise Version 2.0.50 Windows Management Server, Diagnostics, 08 Apr 2020
https://dl.dell.com/FOLDER06194691M/1/SupportAssistEnterprise_2.0.50.32.exe

Dell Support Live Image Version 3.0Dell Support Live Image Version 3.0, Diagnostics, 08 May 2018
https://dl.dell.com/FOLDER04967352M/1/SLI_3.0.0_A00.iso

Dell 32 Bit Diagnostics, version 5162Dell 32 Bit Diagnostics, version 5162, Diagnostics, 18 Aug 2015
https://dl.dell.com/FOLDER02510268M/2/Diagnostics_Application_2MM6J_WN64_5162A0_5162.1.EXE

Dell Online Diagnostics, v.2.16.0.139, A00Dell Online Diagnostics, v.2.16.0.139, A00, Diagnostics, 12 Aug 2013
https://dl.dell.com/diags/dell-onlinediags-win32-2.16.0.139.exe

Dell System E-support Tool (DSET), v.2.1, A00Dell System E-support Tool (DSET), v.2.1, A00, Diagnostics, 03 Nov 2010
https://dl.dell.com/diags/Dell_DSET_2.1.0.113_A00.msi

Dell OS Driver PackDell OS Driver Pack, Drivers for OS Deployment, 24 Apr 2015
https://dl.dell.com/FOLDER02928583M/1/R610_Drivers-for-OS-Deployment_Application_VC4GP_WN64_15.04.00_A00.EXE

Dell OS Drivers Pack, v.6.1.1.6, A00Dell OS Drivers Pack, v.6.1.1.6, A00, Drivers for OS Deployment, 22 May 2013
https://dl.dell.com/LifecycleController/DRVPK_APP_WIN_R234246.EXE

Dell iDRAC Monolithic Release 2.92Dell iDRAC Monolithic Release 2.92, Embedded Server Management, 31 Jan 2019
https://dl.dell.com/FOLDER05421853M/1/ESM_Firmware_KPCCC_WN32_2.92_A00.EXE
```

List latest availabe BIOS firmware/software for R610:

```
$ ./druid.py --model r610 --type bios

Dell Server BIOS R610 Version 6.6.0  UrgentDell Server BIOS R610 Version 6.6.0  Urgent, BIOS, 09 Jul 2018
https://dl.dell.com/FOLDER05012920M/2/BIOS_0YV9D_WN64_6.6.0_01.EXE
```

List all available firmware/software for M620:

```
$ ./druid.py --model m620 --all

Dell Server BIOS PowerEdge M620 Version 2.2.10 (A00)
http://downloads.dell.com/FOLDER02212732M/1/M620-020210C.efi

CMC 4.5 (G00)
http://downloads.dell.com/FOLDER01846847M/1/CMC_4_5_A00.zip

Intel C600\/X79 Series Chipset Driver, Version G00 (1.0.7)
http://downloads.dell.com/FOLDER01817499M/19/Intel_C600_X79_Series_Chipset_G00_ZPE.exe

Dell PowerEdge M620 CPLD 1.0.7 (A00-00)
http://downloads.dell.com/FOLDER01987829M/3/M620_1.0.7_DOS_WINPE_Updated_ZPE.exe

Dell System E-Support Tool (DSET) 3.6 Windows (A01)
http://downloads.dell.com/FOLDER02201594M/1/Dell_DSET_3.6.0.266.exe

Dell Support Live Image Version 2.0 (4233.3)
http://downloads.dell.com/FOLDER01960516M/1/SLI20_A01.iso

Dell 64 Bit uEFI Diagnostics, version 4233 Installer Revision 7.3 (A00-00)
http://downloads.dell.com/FOLDER01790289M/1/DR4233A1.txt

Dell System E-Support Tool (DSET) Windows (A00)
http://downloads.dell.com/FOLDER01378061M/1/Dell_DSET_3.4.0.271.exe

Diagnostics Utility for WIndows (A01)
http://downloads.dell.com/FOLDER00757400M/1/dell-onlinediags-win32-2.21.0.12.exe

DELL,DSK PROG,DSET,3.2,A01 (A00)
http://downloads.dell.com/FOLDER00481709M/1/Dell_DSET_3.2.0.704_A01.exe

Dell OS Driver Pack, Version 7.4.1.10, A00 (A00)
http://downloads.dell.com/FOLDER01978669M/1/Drivers-for-OS-Deployment_Application_Y8H4F_WN64_7.4.1.10_A00.EXE

DELL iDRAC 1.57.57 (A00)
http://downloads.dell.com/FOLDER02177156M/1/iDRAC7__1.57.57__A00.exe

Dell iDRAC7 License Installation Utility (A00-00)
http://downloads.dell.com/FOLDER00946091M/1/iDRAC7_LocalLicense_Installation_Tool_A00_1.0.iso

Emulex Network and Fiber Channel Adapter Diagnostic Software. (A00-00)
http://downloads.dell.com/FOLDER01951395M/1/Elxflash.zip

Emulex Network and Fiber Channel Adapter Documentation. (A00-00)
http://downloads.dell.com/FOLDER02035442M/1/Documentation.zip

Emulex Network and Fiber Channel Adapter Drivers and Software Application. (A00-00)
http://downloads.dell.com/FOLDER01951696M/1/Fibre-Channel_Driver_Y8C1V_WN64_08.01.16_A00-00.EXE

Emulex Network and Fiber Channel Adapter Firmware. (6.0.0.8)
http://downloads.dell.com/FOLDER01951680M/1/Fibre-Channel_Firmware_P6GFD_WN64_01.03.10_A00-00.EXE

Dell Firmware DUP 6.0.0 for Qlogic 26XX series adapters. (6.0.0.8)
http://downloads.dell.com/FOLDER01740704M/1/release_isp24xx-25xx-81xx-83xx_firmware.txt

Dell Qlogic firmware DUP 6.0.0 for QLogic 24XX series of adapters (6.0.0.8)
http://downloads.dell.com/FOLDER01740709M/1/release_isp24xx-25xx-81xx-83xx_firmware.txt

Dell Qlogic firmware DUPs 6.0.0 for Qlogic 25XX series of adapters (A00-00)
http://downloads.dell.com/FOLDER01740681M/1/release_isp24xx-25xx-81xx-83xx_firmware.txt

Emulex Network and Fiber Channel Adapter Documentation. (A00)
http://downloads.dell.com/FOLDER01028427M/1/End_User_Documentation.zip

QLogic Fibre Channel Adapter Firmware (A01)
http://downloads.dell.com/FOLDER00396534M/1/QLogic_LAN_3.0.0_FC_Firmware_A00.exe

Emulex Network and Fiber Channel Adapter Documentation. (A03)
http://downloads.dell.com/FOLDER24788M/1/Emulex_Emulex-Family-of-Serv_A01_R317392.exe

Dell 11G Internal Dual SD Module, v.1.10, A03 (A00)
http://downloads.dell.com/FOLDER56628M/1/IDSDM_UpdateLiveCD_A03.iso

Non-Expander Storage Backplane Firmware (A00)
http://downloads.dell.com/FOLDER00232516M/9/Firmware_681JN_WN32_1.00_A00.EXE

Dell Lifecycle Controller LC2 1.4.2 (A00)
http://downloads.dell.com/FOLDER02185754M/1/LC2 1 4 2_A00_ReleaseNotes.pdf

Dell LifeCycle Controller LC2 1.4.2 Repair Package (A00)
http://downloads.dell.com/FOLDER02185766M/1/LC2 1 4 2_A00_ReleaseNotes.pdf

Dell Lifecycle Controller Integration 2.2 for Microsoft System Center Configuration Manager. (17.8c.4.3)
http://downloads.dell.com/FOLDER02073653M/1/Dell_Lifecycle_Controller_Integration_2.2.0_A00.zip

Broadcom NetXtreme I and NetXtreme II DOS Utilities for the 18.2.2 Family of Drivers release. (17.8c.4.3)
http://downloads.dell.com/FOLDER02014463M/1/Bcom_LAN_17.8c.4.3_DOSUtilities_18.2.0.51.exe

Broadcom Windows 64bit driver update for NetXtreme I and NetXtreme II Ethernet adapters for the 18.2.2 update. (02.30.51.60)
http://downloads.dell.com/FOLDER02014443M/1/Bcom_LAN_17.8c.4.3_Windows_64_18.2.0.51.exe

Mellanox ConnectX-3 Ethernet Adapter Firmware (1.0)
http://downloads.dell.com/FOLDER01855488M/1/Release.txt

Mellanox ConnectX-3 Ethernet Card, User Manual for Dell PowerEdge server (04.40.00)
http://downloads.dell.com/FOLDER01888026M/1/Manual.exe

Windows 64-bit Server Operating System drivers for Mellanox ConnectX-3 Ethernet adapters (A00)
http://downloads.dell.com/FOLDER01757586M/1/Release.txt

Intel NIC and NDCs Firmware Family Version 15.0.1 (6.0.0.8)
http://downloads.dell.com/FOLDER01899604M/1/Firmware_Release_Notes.txt

QLogic 8100 Series Firmware Flash Kits (6.0.0.00)
http://downloads.dell.com/FOLDER01740739M/1/QLogic_LAN_6.0.0_8100_Series_Flash_Kits_6.0.0.8.exe

QLogic Firmware DUP 6.0.0 for 82XX adapters (7.8.16)
http://downloads.dell.com/FOLDER01788040M/1/Dell_Release_Notes_4_16_17.txt

Broadcom NetXtreme I and II Network Device Firmware 7.8.0 (17.8.4.4)
http://downloads.dell.com/FOLDER01844859M/1/Release.txt

Broadcom NetXtreme I and NetXteme II Family of Adapters HTML Users Guide for the 18.2.0 update. (A00)
http://downloads.dell.com/FOLDER01835868M/1/Bcom_LAN_17.8.4.4_Manual_18.2.0.9.exe

Intel NIC DOS-based diag utility and Option ROMs. (A00)
http://downloads.dell.com/FOLDER01772896M/1/Intel_LAN_15.0.0_DOSUtilities_A00.exe

Intel NIC drivers for Windows Server 2008x64 and Windows Server 2012. (A00)
http://downloads.dell.com/FOLDER00993934M/1/Intel_LAN_14.0.0_W2K8_64_W2K12_A00.exe

Intel Server Adapter User Guide for Family version 15.0.0 (A00)
http://downloads.dell.com/FOLDER01772883M/1/Intel_LAN_15.0.0_Manual_A00.zip

Intel NIC drivers for Windows Server 2008x64 and Windows Server 2012. (17.6.0.12)
http://downloads.dell.com/FOLDER01453273M/1/Intel_LAN_14.5.0_W2K8_64_W2K12_A00.exe

Broadcom NetXtreme I and NetXteme II Family of Adapters HTML Users Guide for the 17.6 update. (5.0.0.11)
http://downloads.dell.com/FOLDER01480362M/1/Bcom_LAN_17.6.4.4_Manual_17.6.12.exe

Dell Firmware DUP 5.0.0 for Qlogic 26XX series adapters. (5.0.0.11)
http://downloads.dell.com/FOLDER01451293M/2/Network_Firmware_0W50M_WN64_02.02.17_5.0.0.11.EXE

Dell Qlogic firmware DUP 5.0.0 for QLogic 24XX series of adapters. (5.0.0.11)
http://downloads.dell.com/FOLDER01451309M/2/Network_Firmware_JMGYY_WN64_02.08.01_5.0.0.11.EXE

Dell Qlogic firmware DUPs 5.0.0 for Qlogic 25XX series of adapters (5.0.0.11)
http://downloads.dell.com/FOLDER01451301M/2/Network_Firmware_0V24X_WN64_02.65.05_5.0.0.11.EXE

QLogic 8100 Series Firmware Flash Kits (5.0.0.13)
http://downloads.dell.com/FOLDER01451253M/1/QLogic_LAN_5.0.0_8100_Series_Flash_Kits_5.0.0.11.exe

QLogic Drivers & Applications 5.0.0 (5.0.0.13)
http://downloads.dell.com/FOLDER01468967M/1/QLogic_LAN_5.0.0_Windows_Apps_5.0.0.13.exe

QLogic User's Guide 5.0.0 (4.0.0.17)
http://downloads.dell.com/FOLDER01469023M/1/QLogic_LAN_5.0.0_Manual_5.0.0.13.exe

QLogic 8100 Series Ethernet Adapter Firmware (4.0.0.17)
http://downloads.dell.com/FOLDER01113366M/1/QLogic_LAN_4.0.0_8100_Series_Flash_Kits_4.0.0.17.exe

QLogic User's Manual (A00)
http://downloads.dell.com/FOLDER00211427M/1/QLogic_LAN_2.0_Manual_A00.exe

Intel Server Adapter User Guide for Family version 14.5.0. (4.0.0.17)
http://downloads.dell.com/FOLDER00929735M/1/Intel_LAN_14.0.0_Manual_A00.zip

QLogic 8200 Series Utilities and Drivers (4.0.0.18)
http://downloads.dell.com/FOLDER00934424M/1/QLogic_LAN_4.0.0_DOSUtilities_4.0.0.17.exe

QLogic Ethernet and Fibre Channel Device Drivers (17.4.0.6)
http://downloads.dell.com/FOLDER00978453M/1/QLogic_LAN_4.0.0_Windows_Apps_4.0.0.18.exe

Broadcom HTML Users Guide for the 17.4.0 driver family update, for Q4 2011. (A00)
http://downloads.dell.com/FOLDER00983024M/1/Bcom_LAN_17.4.0_Manual_17.4.0.10.zip

Intel NIC DOS based diag utility and Option ROMs (A00)
http://downloads.dell.com/FOLDER00210609M/1/Intel_LAN_13.0.0_DOSUtilities_A00.exe

Intel Server Adapter User Guide for Family version 13.5.0 (A00)
http://downloads.dell.com/FOLDER00376500M/1/Intel_LAN_13.5.0_Manual_A00.zip

Broadcom NetXtreme I and NetXtreme II Network Adapters User Guide for the 17.2.0 Driver Set Release. (A00)
http://downloads.dell.com/FOLDER00475110M/1/Bcom_LAN_17.2.0_Manual_A00.exe

QLogic 8200 Series Utilities and Drivers (A00)
http://downloads.dell.com/FOLDER00210681M/1/QLogic_LAN_2.0_DOSUtilities_A00.exe

QLogic Ethernet and Fibre Channel Device Drivers (A00)
http://downloads.dell.com/FOLDER00234349M/3/Network_Driver_WCR4P_WN32_2.00.14_A00.EXE

Broadcom NetXtreme I and NetXtreme II User Guide for the Driver set version 17.0.1. (A00)
http://downloads.dell.com/FOLDER00251752M/1/Bcom_LAN_17.0.1_Manual_A00.exe

Intel Server Adapter User Guide for Family version 13.0.0 (A00)
http://downloads.dell.com/FOLDER00210619M/1/Intel_LAN_13.0.0_Manual_A00.exe

Seagate SAS vendor model number ST33000652SS. Firmware version RSFE (A00)
http://downloads.dell.com/FOLDER02170703M/1/SAS-Drive_Firmware_23TVX_WN64_RSFE_A00.EXE

Seagate SAS ST32000645SS and ST33000650SS RS16 (A12)
http://downloads.dell.com/FOLDER02170768M/1/SAS-Drive_Firmware_568C9_WN64_RS16_A00.EXE

Dell Nautilus Firmware Update Utility for SAS and SATA disk and solid state drives (A01)
http://downloads.dell.com/FOLDER02088744M/2/Nautilus_efi_A12_ZPE.exe

Hitachi HUC151414CSS600 and HUC151473CSS600 firmware version K772. (A00)
http://downloads.dell.com/FOLDER01996491M/1/SAS-Drive_Firmware_8R65X_WN64_K772_A01.EXE

Sandisk SAS LB206M, LB406M, LB806M, LB206S, LB406S, LB406R, LB806R and LB1606R firmware version D323 (A04)
http://downloads.dell.com/FOLDER01885040M/1/SAS-Drive_Firmware_WWDTT_WN64_D323_A00.EXE

Hitachi SAS HUC106030CSS600 and HUC106060CSS600 firmware version A360 (A07)
http://downloads.dell.com/FOLDER00435858M/4/SAS-Drive_Firmware_R1MYY_WN32_A360_A04.EXE

Seagate SAS ST91000640SS and ST9500620S firmware version AS09, dell version A07 (A04)
http://downloads.dell.com/FOLDER01350459M/5/SAS-Drive_Firmware_DVKMP_WN32_AS09_A07.EXE

Toshiba SAS AL13SEB300, AL13SEB600 and AL13SEB900 firmware version DE09 (A02)
http://downloads.dell.com/FOLDER01685171M/1/SAS-Drive_Firmware_5CX8G_WN64_DE09_A04.EXE

HGST SAS HUC101212CSS600 firmware version U5E0 (A04)
http://downloads.dell.com/FOLDER01707398M/1/SAS-Drive_Firmware_HWWCK_WN64_U5E0_A02.EXE

Dell Physical Disk Firmware Version Report (A04)
http://downloads.dell.com/FOLDER01747547M/3/hddfwver_ZPE.exe

Seagate SAS 300GB Hard Drive. Vendor model number ST9300453SS. Firmware version YSFA (A07)
http://downloads.dell.com/FOLDER01350436M/2/SAS-Drive_Firmware_FY10F_WN32_YSFA_A04.EXE

Seagate SAS ST91000640SS and ST9500620S firmware version AS09, dell version A07 (A06)
http://downloads.dell.com/FOLDER01350402M/2/SAS-Drive_Firmware_3JVY1_WN32_YS0A_A07.EXE

Western Digital SAS WD3001BKHG, WD6001BKHG and WD9001BKHG firmware version A06 (A02)
http://downloads.dell.com/FOLDER01490283M/2/SAS-Drive_Firmware_WD3HJ_WN64_D1S6_A06.EXE

Seagate SAS ST9146802SS and ST973402SS firmware version S22F (A06)
http://downloads.dell.com/FOLDER01468599M/1/SAS-Drive_Firmware_7TN7R_WN64_S22F_A02.EXE

HGST SAS drive models HUC109030CSS600, HUC109060CSS600 and HUC109090CSS600 firmware version N440 (A03)
http://downloads.dell.com/FOLDER01324126M/2/SAS-Drive_Firmware_F5NH4_WN32_N440_A06.EXE

Toshiba SAS MBF2300RC and MBF2600R firmware version DA0B. (A03)
http://downloads.dell.com/FOLDER01451138M/2/SAS-Drive_Firmware_0JYGF_WN64_DA0B_A03.EXE

Toshiba SAS MK1401GRRB and MK3001GRRB firmware version DB08 (A07)
http://downloads.dell.com/FOLDER01327398M/2/SAS-Drive_Firmware_G9CVG_WN32_DB08_A03.EXE

Seagate SAS ST9900805SS, ST9600205SS and ST9300605SS firmware version CS09 (A04)
http://downloads.dell.com/FOLDER01000171M/2/SAS-Drive_Firmware_6PM3Y_WN32_CS09_A07.EXE

Toshiba SAS model numbers MK1001GRZB, MK2001GRZB and MK4001GRZB firmware version A007 (A01)
http://downloads.dell.com/FOLDER01068008M/3/SAS-Drive_Firmware_8GMKG_WN32_A007_A04.EXE

Seagate SAS ST9500431SS firmware version DSF4. (A01)
http://downloads.dell.com/FOLDER01293899M/1/SAS-Drive_Firmware_VGYD2_WN32_DSF4_A01.EXE

Seagate SAS ST9146752SS firmware version HTF6. (A06)
http://downloads.dell.com/FOLDER00435800M/4/SAS-Drive_Firmware_VP540_WN32_HTF6_A01.EXE

Seagate SAS ST9500430SS firmware version DS66. (A03)
http://downloads.dell.com/FOLDER00881915M/1/SAS-Drive_Firmware_5WTTD_WN32_DS66_A06.EXE

Seagate SAS ST91000642SS firmware version ASF9. (A01)
http://downloads.dell.com/FOLDER00843440M/1/SAS-Drive_Firmware_NF2RT_WN32_ASF9_A03.EXE

Seagate SAS ST9146703SS and ST9300503SS firmware version FSF9 (A08)
http://downloads.dell.com/FOLDER00435847M/5/SAS-Drive_Firmware_PVD82_WN32_FSF9_A01.EXE

Seagate SAS ST9146803SS and ST9300603SS firmware version FS66. (A05)
http://downloads.dell.com/FOLDER00979743M/2/SAS-Drive_Firmware_XJ1HM_WN32_FS66_A08.EXE

Seagate SAS ST9600204SS firmware version FM0A. (A06)
http://downloads.dell.com/FOLDER00881806M/7/SAS-Drive_Firmware_41N5D_WN32_FM0A_A05.EXE

Seagate SAS ST973452SS and ST9146852SS firmware version HT66. (A03)
http://downloads.dell.com/FOLDER00876038M/3/SAS-Drive_Firmware_4VM2N_WN32_HT66_A06.EXE

Seagate SAS ST9900605SS firmware version CSF8 (A01)
http://downloads.dell.com/FOLDER00843651M/2/SAS-Drive_Firmware_3HFT8_WN32_CSF8_A03.EXE

Fujitsu\/Toshiba SAS MBD2147RC and MBD2300RC firmware version D80A. (A02)
http://downloads.dell.com/FOLDER00633504M/5/SAS-Drive_Firmware_F50FD_WN32_D80A_A01.EXE

Fujitsu \/ Toshiba SAS MBE2073RC and MBE2147RC firmware version D906. (A02)
http://downloads.dell.com/FOLDER00633579M/4/SAS-Drive_Firmware_TPF6G_WN32_D906_A02.EXE

Hitachi SAS HUC101473CSS300 and HUC101414CSS300 firmware version C590 (A05)
http://downloads.dell.com/FOLDER00500099M/4/SAS-Drive_Firmware_2X4NR_WN32_C590_A02.EXE

Dell PERC H710 Mini Blades firmware release 21.3.0-0009 (A05)
http://downloads.dell.com/FOLDER02192395M/2/SAS_RAID_H710MB_21.3.0-0009_A05_ZPE.exe

PERC H710P Mini Blades firmware release 21.3.0-0009 (A08)
http://downloads.dell.com/FOLDER02192484M/2/SAS_RAID_H710PB_21.3.0-0009_A05_ZPE.exe

DELL PERC H310 Mini Blades Firmware release 20.13.0-0007 (A05)
http://downloads.dell.com/FOLDER02192272M/2/SAS_RAID_H310MB_20.13.0-0007_A08_ZPE.exe

Microsoft Windows 2008 R2 SP1 64 Bit Driver for Dell PERC H310\/H710\/H710P\/H810\/SPERC8 Controllers (A05)
http://downloads.dell.com/FOLDER01968953M/26/SAS_RAID_Driver_R2_1HHG8_A05_6.802.19.0_ZPE.exe

Dell Backplane (A00)
http://downloads.dell.com/FOLDER83949M/1/DellBPA05.exe

Dell Systems Build and Update Utility, v2.4 (A00)
http://downloads.dell.com/secure//FOLDER02027124M/1/sbuu_2.4_866_A00.iso

Dell Systems Management Tools and Documentation DVD ISO, v.7.4 (A00)
http://downloads.dell.com/secure//FOLDER02027063M/1/OM_SMTD_740_A00.iso

Dell Systems Management Tools and Documentation DVD ISO, v.7.3.2 (This release of OMSA 7.3.2 is applicable only for 12G servers with latest Intel Xeon Processors E5-4600 , E5-2600 series and E5-1600 v2) (A12)
http://downloads.dell.com/secure//FOLDER02085222M/1/OM_SMTD_732_A00.iso

Dell Nautilus Firmware Update Utility for SAS and SATA Disk and Solid State Drive (A04)
http://downloads.dell.com/FOLDER02088796M/2/Nautilus_efi_A12_ZPE.exe

Dell Physical Disk Firmware Version Report (A01)
http://downloads.dell.com/FOLDER01747526M/3/hddfwver_ZPE.exe

Intel Wolfsville 3Gbps SATA SSD models SSDSC2BB160G4T, SSDSC2BB300G4T, SSDSC2BB480G4T, SSDSC2BB800G4T and firmware version DL10. (A09)
http://downloads.dell.com/FOLDER01523938M/2/Serial-ATA_Firmware_4N1N0_WN64_DL10_X01.EXE

Seagate SATA ST91000640NS, ST9500620NS and ST9250610NS firmware version AA09 (A05)
http://downloads.dell.com/FOLDER01478025M/2/Serial-ATA_Firmware_740GN_WN64_AA09_A09.EXE

Dell PowerEdge Express PCIe SSD (A04)
http://downloads.dell.com/FOLDER01873721M/1/Express_Flash_PCIe-SSD_FRMW_79J67_A05_B1490908.txt

Windows 2008 R2 64Bit Driver for Dell Poweredge Express Flash PCIe SSD. (A00)
http://downloads.dell.com/FOLDER01750981M/4/Express_Flash_PCIe-SSD_DRVR_WIN2K8R2_X81T1_A04_8.3.6874.0_ZPE.exe

Dell OpenManage Server Administrator Managed Node Patch (windows 32 bit) , v7.4.0.1 (A00)
http://downloads.dell.com/FOLDER02209455M/1/OM_7401_Sysmgmtx86_Patch.msp

Dell OpenManage Server Administrator Managed Node Patch (windows 64 bit) , v7.4.0.1 (A00)
http://downloads.dell.com/FOLDER02216804M/1/OM_7401_Sysmgmtx64_Patch.msp

Dell Connections License Manager, v.1.1 (A00)
http://downloads.dell.com/FOLDER02213015M/1/Dell_Connections_License_Manager_v1.1_A00.exe

Dell Server Management Pack for Microsoft System Center Operations Manager, v.5.2 (A00)
http://downloads.dell.com/FOLDER02166910M/1/Dell_Server_Management_Pack_Suite_v5.2_A00.exe

Dell OpenManage DTK (Windows) Patch v4.4.0.1 (A00)
http://downloads.dell.com/FOLDER02164465M/1/DTK4.4.0.1-WINPE-975.exe

Dell Repository Manager, v1.9 (A00)
http://downloads.dell.com/FOLDER02155461M/1/Dell_Repository_Manager_1.9.0.151.msi

Dell OpenManage Essentials 1.30 Security Patch (A01)
http://downloads.dell.com/FOLDER02142377M/1/OME-HOTFIX_HF1006.1.3_1542.exe

Dell Server Deployment Pack 2.1 for Microsoft System Center Configuration Manager (A00)
http://downloads.dell.com/FOLDER02105780M/1/Dell_Server_Deployment_Pack_v2.1_for_Configuration_Manager_A01.exe

Dell Server Deployment Pack 2.1 Service Pack 02 (2.1.0.2) for Microsoft System Center Configuration Manager (A00)
http://downloads.dell.com/FOLDER02099139M/1/Dell_Server_Deployment_Pack_v2.1_SP02.exe

Dell License Manager (A01)
http://downloads.dell.com/FOLDER02114876M/1/LicenseManager_1.1.0.exe

Dell OpenManage Essentials 1.3 (A00)
http://downloads.dell.com/FOLDER02088515M/1/OpenManageEssentials_1_3_A01.exe

Dell Server Update Utility. (A00)
http://downloads.dell.com/FOLDER02087154M/1/SUU_14.03.00_A00.iso

Dell Driver Pack For Windows OS. (A00)
http://downloads.dell.com/FOLDER02073387M/1/LCDRVPCK_Win_741_Q12014_A00.iso

Dell OpenManage Plug-in v1.0 for Oracle Enterprise Manager 12c (A00)
http://downloads.dell.com/FOLDER02085638M/1/dell.em.ome_12.1.0.1.0.zip

Dell Smart Plug-in (SPI) v4.0 for HP Operations Manager 9.0 for Microsoft Windows (A00)
http://downloads.dell.com/FOLDER02067331M/1/Dell_Smart_Plug-in_v4.0_x64_A00.exe

Dell Lifecycle Controller Integration 2.2 for Microsoft System Center Configuration Manager. (A00)
http://downloads.dell.com/FOLDER02073644M/1/Dell_Lifecycle_Controller_Integration_2.2.0_A00.zip

Dell OpenManage Active Directory Snap-in Utility (32bit),v7.4 (A00)
http://downloads.dell.com/FOLDER02022667M/1/OM-ADSnapIn-Dell-Web-WIN-7.4.0-866_A00.exe

Dell OpenManage BMC Utility,v7.4 (A00)
http://downloads.dell.com/FOLDER02022736M/1/OM-BMC-Dell-Web-WIN-7.4.0-866_A00.exe

Dell OpenManage Deployment Toolkit (Windows) v4.4 (A00)
http://downloads.dell.com/FOLDER02018365M/1/DTK4.4-WINPE-866_A00.exe

Dell OpenManage DRAC Tools, includes Racadm (32bit),v7.4 (A00)
http://downloads.dell.com/FOLDER02022762M/1/OM-DRAC-Dell-Web-WIN-7.4.0-866_A00.exe

Dell OpenManage MIBs for PowerEdge,v7.4 (A00)
http://downloads.dell.com/FOLDER01996273M/1/Dell-OM-MIBS-740_A00.zip

Dell OpenManage Server Administrator Managed Node (Windows - 32 bit),v7.4 (A00)
http://downloads.dell.com/FOLDER02020099M/1/OM-SrvAdmin-Dell-Web-WIN-7.4.0-866_A00.exe

Dell OpenManage Server Administrator Managed Node(windows - 64 bit) v.7.4 (A00)
http://downloads.dell.com/FOLDER02020149M/1/OM-SrvAdmin-Dell-Web-WINX64-7.4.0-866_A00.exe

Dell Server PRO Management Pack for Microsoft System Center 2012 Virtual Machine Manager, v.3.0.1 (A00)
http://downloads.dell.com/FOLDER01916027M/1/Dell_PROPack_v3.0.1_A00.exe

Dell PowerEdge Driver Maintenance Pack, v.7.4.0 (A00)
http://downloads.dell.com/FOLDER01907355M/1/OSDRIVERSET_w2011sbs_64_7.4_4177.exe

Dell iDRAC Service Module ,v1.0 (A00)
http://downloads.dell.com/FOLDER01879828M/1/OM-iSM-Dell-Web-X64-1.0.0_A00-429.zip

Dell SupportAssist 1.2.1 for OpenManage Essentials (A00-00)
http://downloads.dell.com/FOLDER01834941M/1/SupportAssist-plugin-1.2.1.exe

Dell OpenManage Power Center V2.0 (A00)
http://downloads.dell.com/FOLDER01793440M/1/PowerCenter_PKG_2_0_0_A00.exe

Dell OpenManage Connection v1.0 for IBM Tivoli Network Manager IP Edition 3.9 (A00)
http://downloads.dell.com/FOLDER01677878M/1/Dell-OpenManage-Connection-for-ITNM-1.0_A00.zip

Dell OpenManage Connection v2.1 for IBM Tivoli Netcool\/OMNIbus 7.3.1 and 7.4 (A00)
http://downloads.dell.com/FOLDER01677865M/1/Dell_OpenManage_Connection_for_OMNIbus_v2_1_A00.zip

Dell DRAC Tools, includes Racadm (64bit),v7.3.1 (A00)
http://downloads.dell.com/FOLDER01600032M/1/OM-DRAC-Dell-Web-WINX64-7.3.1-376.exe

Dell OpenManage Active Directory Snap-in Utility (64bit),v7.3 (A00)
http://downloads.dell.com/FOLDER01545634M/1/OM-ADSnapIn-Dell-Web-WINX64-7.3.0-350.exe

Dell OpenManage Server Administrator Managed Node (Windows - 32bit), v7.1 (A00)
http://downloads.dell.com/FOLDER00574377M/1/OM-SrvAdmin-Dell-Web-WIN-7.1.0-5304_A00.exe

Dell Windows OS install support pack (A00)
http://downloads.dell.com/FOLDER00651672M/1/CDUW_DVD_7.1.0-3.iso

Dell OpenManage Server Administrator Managed Node Patch (A00)
http://downloads.dell.com/FOLDER00979251M/1/SysMgmt_7001_patch.msp

Dell Driver Pack For Linux OS, v.7.1.0 (A00)
http://downloads.dell.com/FOLDER00798493M/1/OM710_SUU_DRVPKG_LIN.iso

Dell Windows Debugger Utility (A00)
http://downloads.dell.com/FOLDER00634763M/1/DWinDbg.msi

Dell Server PRO Management Pack for Microsoft System Center Virtual Machine Manager 2008, v.2.1 (A01)
http://downloads.dell.com/FOLDER75796M/1/Dell_PROPack_v2.1.0_A00.exe

Dell AIM Integration Pack for Microsoft System Center Orchestrator, v.2.0 (A00)
http://downloads.dell.com/FOLDER00583567M/1/IP_Orchestrator_Dell_AIM_2.0-24.exe

Dell DRAC Tools 1.1 (17_A00)
http://downloads.dell.com/FOLDER00318972M/1/ADSP.exe

Dell DVD ISO - Systems Service and Diagnostics Tools, v6.3 (A00)
http://downloads.dell.com/FOLDER69833M/1/sm_6.3.0-17_A00.3.iso

Dell OpenManage Connection for CA NSM, v3.4 (A00)
http://downloads.dell.com/FOLDER00220570M/1/Dell_OMC_for_CA_NSM_v3.4_A00.exe

Matrox Video Driver (Dell Version)
http://downloads.dell.com/FOLDER00247465M/1/A00_WIN64_G200eR_v2.4.1.0.exe
```

Get iDRAC hardware inventory in text format:

```
$ ./druid.py --get inventory --ip 192.168.11.233 --username root --password calvin --text --print
racadm hwinventory


-------------------------HARDWARE INVENTORY------------------------

[InstanceID: QuickSync.Integrated.1]
Device Type = SystemQuickSync
FWVersion = 0.0
Version = 0
ProductName = iDRAC Quick Sync
Manufacturer = Dell
DeviceDescription = Integrated Quick Sync 1
FQDD = QuickSync.Integrated.1
InstanceID = QuickSync.Integrated.1
-------------------------------------------------------------------

[InstanceID: RAID.Integrated.1-1]
Device Type = Controller
BootVirtualDiskFQDD = Disk.Virtual.0:RAID.Integrated.1-1
RealtimeCapability = Incapable
SupportControllerBootMode = Supported
SupportEnhancedAutoForeignImport = Supported
MaxAvailablePCILinkSpeed = Generation 3
MaxPossiblePCILinkSpeed = Generation 3
PatrolReadState = Unknown
DriverVersion = Not Applicable
CacheSizeInMB = 2048 MB
SupportRAID10UnevenSpans = Supported
T10PICapability = Supported
SlicedVDCapability = Sliced Virtual Disk creation supported
CachecadeCapability = Cachecade Virtual Disk not supported
EncryptionCapability = Local Key Management Capable
EncryptionMode = None
SecurityStatus = Encryption Capable
SASAddress = 51866DA0B6C3F400
ProductName = PERC H730P Mini
DeviceCardSlotType = Unknown
DeviceCardSlotLength = Unknown
DeviceCardDataBusWidth = Unknown
DeviceCardManufacturer = DELL
PCISubDeviceID = 1F47
PCIDeviceID = 5D
PCISubVendorID = 1028
PCIVendorID = 1000
Function = 0
Device = 0
Bus = 0
ControllerFirmwareVersion = 25.5.8.0001
PersistentHotspare = 0
PCISlot = 0
RollupStatus = Unknown
PrimaryStatus = Unknown
DeviceDescription = Integrated RAID Controller 1
FQDD = RAID.Integrated.1-1
InstanceID = RAID.Integrated.1-1
LastUpdateTime = 2021-11-26T13:30:50
LastSystemInventoryTime = 2021-11-26T13:31:09
-------------------------------------------------------------------
```

Get iDRAC hardware inventory in JSON format:

```
$ ./druid.py --get inventory --ip 192.168.11.233 --username root --password calvin --json --print

{
 "QuickSync.Integrated.1": {
  "Device Type": "SystemQuickSync",
  "FWVersion": "0.0",
  "Version": "0",
  "ProductName": "iDRAC Quick Sync",
  "Manufacturer": "Dell",
  "DeviceDescription": "Integrated Quick Sync 1",
  "FQDD": "QuickSync.Integrated.1",
  "InstanceID": "QuickSync.Integrated.1"
 },
 "RAID.Integrated.1-1": {
  "Device Type": "PCIDevice",
  "SlotType": "Unknown",
  "SlotLength": "Unknown",
  "DataBusWidth": "Unknown",
  "Description": "PERC H730P Mini",
  "Manufacturer": "Broadcom / LSI",
  "PCISubDeviceID": "1F47",
  "PCISubVendorID": "1028",
  "PCIDeviceID": "005D",
  "PCIVendorID": "1000",
  "FunctionNumber": "0",
  "DeviceNumber": "0",
  "BusNumber": "0",
  "DeviceDescription": "Integrated RAID Controller 1",
  "FQDD": "RAID.Integrated.1-1",
  "InstanceID": "RAID.Integrated.1-1",
  "LastUpdateTime": "2021-11-26T13:30:50",
  "LastSystemInventoryTime": "2021-11-26T13:31:09"
 },
 "AHCI.Embedded.1-1": {
  "Device Type": "PCIDevice",
  "SlotType": "Unknown",
  "SlotLength": "Unknown",
  "DataBusWidth": "Unknown",
  "Description": "C610/X99 series chipset sSATA Controller [AHCI mode]",
  "Manufacturer": "Intel Corporation",
  "PCISubDeviceID": "0601",
  "PCISubVendorID": "1028",
  "PCIDeviceID": "8D62",
  "PCIVendorID": "8086",
  "FunctionNumber": "4",
  "DeviceNumber": "23",
  "BusNumber": "0",
  "DeviceDescription": "Embedded AHCI 1",
  "FQDD": "AHCI.Embedded.1-1",
  "InstanceID": "AHCI.Embedded.1-1",
  "LastUpdateTime": "2021-10-21T14:23:42",
  "LastSystemInventoryTime": "2021-11-26T13:31:09"
 }
}
```