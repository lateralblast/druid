#!/usr/bin/env python

# Name:         druid (Dell Retrieve Update Information and Download)
# Version:      0.1.7
# Release:      1
# License:      CC-BA (Creative Commons By Attrbution)
#               http://creativecommons.org/licenses/by/4.0/legalcode
# Group:        System
# Source:       N/A
# URL:          http://lateralblast.com.au/
# Distribution: UNIX
# Vendor:       Lateral Blast
# Packager:     Richard Spindler <richard@lateralblast.com.au>
# Description:  Python script to get available firmware from Dell site and check iDRAC
#               http://www.dell.com/support/troubleshooting/us/en/19/ProductSelector/Select/FamilySelection?CategoryPath=all-products%2Fesuprt_ser_stor_net%2Fesuprt_poweredge&Family=PowerEdge&DisplayCrumbs=Product%2BType%40%2CServers%252c%2BStorage%2Band%2BNetworking%40%2CPowerEdge&rquery=na&sokey=solink

# Import modules

import urllib.request
import subprocess
import platform
import argparse
import requests
import urllib3
import time
import json
import sys
import os
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from os.path import expanduser

# Set some defaults

script_exe = sys.argv[0]
script_dir = os.path.dirname(script_exe)
home_dir   = expanduser("~")
def_dir    = home_dir+"/firmware"
results    = {}
models     = []

# Check we have pip installed

try:
  from pip._internal import main
except ImportError:
  os.system("easy_install pip")
  os.system("pip install --upgrade pip")

# install and import a python module

def install_and_import(package):
  import importlib
  try:
    importlib.import_module(package)
  except ImportError:
    command = "python3 -m pip install --user %s" % (package)
    os.system(command)
  finally:
    globals()[package] = importlib.import_module(package)

# Load selenium

try:
  from selenium import webdriver
except ImportError:
  install_and_import("selenium")
  from selenium import webdriver

# Load bs4

try:
  from bs4 import BeautifulSoup
except ImportError:
  install_and_import("bs4")
  from bs4 import BeautifulSoup

# Load lxml

try:
  import lxml
except ImportError:
  install_and_import("lxml")
  import lxml

from lxml import etree

# load wget

try:
  import wget
except ImportError:
  install_and_import("wget")
  import wget

# load paraminko

try:
  import paramiko
except ImportError:
  install_and_import("paramiko")
  import paramiko

# Load pexpect

try:
  import pexpect
except ImportError:
  install_and_import("pexpect")
  import pexpect

# Load redfish

try:
  import redfish
except ImportError:
  install_and_import("redfish")
  import redfish

# Print version

def print_version(script_exe):
  file_array = file_to_array(script_exe)
  version    = list(filter(lambda x: re.search(r"^# Version", x), file_array))[0].split(":")[1]
  version    = re.sub(r"\s+","",version)
  print(version)

# Print help

def print_help(script_exe):
  print("\n")
  command    = "%s -h" % (script_exe)
  os.system(command)
  print("\n")

# Read a file into an array

def file_to_array(file_name):
  file_data  = open(file_name)
  file_array = file_data.readlines()
  return file_array

# Print options

def print_options(script_exe):
  file_array = file_to_array(script_exe)
  opts_array = list(filter(lambda x:re.search(r"add_argument", x), file_array))
  print("\nOptions:\n")
  for line in opts_array:
    line = line.rstrip()
    if re.search(r"#",line):
      option = line.split('"')[1]
      info   = line.split("# ")[1]
      if len(option) < 8:
        string = "%s\t\t\t%s" % (option,info)
      else:
        if len(option) < 16:
          string = "%s\t\t%s" % (option,info)
        else:
          string = "%s\t%s" % (option,info)
      print(string)
  print("\n")

# Check IP

def check_valid_ip(ip):
  if not re.search(r"[a-z]",ip):
    try:
      socket.inet_pton(socket.AF_INET, ip)
    except AttributeError:
      try:
        socket.inet_aton(ip)
      except socket.error:
        return False
      return ip.count('.') == 3
    except socket.error:  # not a valid address
      return False
  else:
    return True

# Check host is up

def check_ping(ip):
  try:
    output = subprocess.check_output("ping -{} 1 {}".format('n' if platform.system().lower()=="windows" else 'c', ip), shell=True)
  except Exception:
    string = "Warning:\tHost %s not responding" % (ip)
    handle_output(options,string)
    return False
  return True 

# Handle output

def handle_output(options,output):
  if options['mask'] == True:
    if re.search(r"serial|address|host|id",output.lower()):
      if re.search(":",output):
        param  = output.split(":")[0]
        output = "%s: XXXXXXXX" % (param)
  print(output)
  return

# Execute command

def execute_command(options,command):
  process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, )
  output  = process.communicate()[0].decode()
  if options['verbose'] == True:
    string = "Output:\n%s" % (output)
    handle_output(options,string)

# Get document URLs

def print_document_urls(options):
  if options['model']:
    if re.search(r"[m,r][0-9]1[0-9]",options['model'].lower()):
      base_owners_url = "https://downloads.dell.com/manuals/all-products/esuprt_ser_stor_net/esuprt_%s/%s-" % (options['hwtype'], options['hwtype'])
      base_setup_url  = "https://downloads.dell.com/manuals/all-products/esuprt_ser_stor_net/esuprt_%s/%s-" % (options['hwtype'], options['hwtype'])
    else:
      base_owners_url = "https://dl.dell.com/topicspdf/%s-" % (options['hwtype'])
      base_setup_url  = "https://downloads.dell.com/manuals/all-products/esuprt_ser_stor_net/esuprt_%s/%s-" % (options['hwtype'], options['hwtype'])
  else:
    base_owners_url = "https://dl.dell.com/topicspdf/%s-" % (options['hwtype'])
    base_setup_url  = "https://downloads.dell.com/manuals/all-products/esuprt_ser_stor_net/esuprt_%s/%s-" % (options['hwtype'], options['hwtype'])
  if re.search(r"[m,r][0-9]1[0-9]", options['model'].lower()):
    if re.search(r"r610", options['model'].lower()):
      owners_url = "%s%s_owner%%27s%%20manual2_en-us.pdf" % (base_owners_url,options['model'])
    else:
      owners_url = "%s%s_owner%%27s%%20manual_en-us.pdf" % (base_owners_url,options['model'])
  else:
    owners_url = "%s%s_owners-manual_en-us.pdf" % (base_owners_url, options['model'])
  setup_url = "%s%s_setup%%20guide_en-us.pdf" % (base_setup_url, options['model'])
  string    = "%s %s:" % (options['hwupcase'], options['model'])
  handle_output(options, string)
  handle_output(options, owners_url)
  handle_output(options, setup_url)
  if options['download'] == True:
    for url in [ owners_url, setup_url ]:
      file = os.file.basename(url)
      file = "%s/%s" % (options['fwdir'], file)
      download_file(options,url, file)
      if re.search(r"owner", file):
        if not os.path.exists(file):
          options['hwtype'] = options['hwupcase'].downcase
          url = "http://topics-cdn.dell.com/pdf/%s-%s_Owner's%%20Manual_en-us.pdf" % (options['hwtype'], options['model'])
          string  = "Downloading %s to %s" % (url,file)
          command = "wget %s -O %s" % (url,file)
          handle_output(options, string)
          process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, )
  print()
  return

# Initiate web client

def start_web_driver():
  from selenium.webdriver.firefox.options import Options
  options = Options()
  options.headless = True
  driver = webdriver.Firefox(options=options)
  return driver

# Get list of models

def get_model_list(options):
  if re.search(r"poweredge",options['hwtype'].lower()):
    top_url = "https://www.dell.com/en-au/work/shop/dell-poweredge-servers/sc/servers"
  else:
    top_url = "https://www.dell.com/en-au/work/shop/data-storage-and-backup/sc/storage-products"
  driver = start_web_driver()
  driver.get(top_url)
  html_doc  = driver.page_source
  html_doc  = BeautifulSoup(html_doc, features='lxml')
  html_data = html_doc.find_all('li')
  for link in html_data:
    text = link.text
    text = re.sub(r"^\s+|\s+$","", text)
    if re.search(r"^Power[Edge,Vault]|^SC[0-9][0-9]|^[A-Z][0-9][0-9]", text):
      if re.search(r"^Power", text):
        model = text.split(" ")[1]
      else:
        model = text.split(" ")[0]
      models.append(model)
  return models

# Get Firmware info from website

def get_firmware_info(options,results):
  name   = ""
  link   = ""
  driver = start_web_driver()
  driver.get(options['modelurl'])
  time.sleep(5)
  if options['all'] == True:
    driver.find_element_by_id("_evidon-accept-button").click()
    driver.find_element_by_id("paginationRow").click()
    time.sleep(5)
  html_doc = driver.page_source
  html_doc = BeautifulSoup(html_doc, features='lxml')
  for section in html_doc.select("section"):
    for table in section.select("table"):
      for row in table.select("tr"):
        if not re.search(r"NameCategoryRelease", str(row)):
          for column in row.select("td"):
            if re.search(r"href",str(column)):
              if re.search(r"download", str(column)):
                link = str(column)
                link = link.split('href="')[1]
                link = link.split('  class="')[0]
                link = link.split('"')[0]
            else:
              if re.search(r"dl-desk-view", str(column)):
                name = str(column)
                name = name.split('dl-desk-view">')[1]
                name = name.split('<span')[0]
                name = re.sub(r"^\s+|\s+$", "", name)
                name = re.sub(r"\.$", "", name)
#              else:
#                if not name.find(column.text):
#                  name = "%s, %s" % (name,column.text)
          if re.search(r"[a-z,A-Z]", name):
            name = re.sub(r"\s+", " ", name)
            if re.search(r"list|all",options['type']) or name.lower().count(options['type'].lower()) > 0:
              results[name] = link
  return results

# Check iDRAC redfish support

def check_idrac_redfish(options, base_url):
  response = requests.get(base_url, verify=False, auth=(options['username'], options['password']))
  data = response.json()
  if response.status_code != 200:
    print("\nWARNING: iDRAC version installed does not support this feature using Redfish API\n")
    exit()


# Get iDRAC information

def get_idrac_info(options):
  if re.search(r"memory|tag|sku|power|model|bios|cpu|hostname",options['get'].lower()):
    rest_url = "/redfish/v1/Systems/System.Embedded.1"
  else:
    rest_url = "/redfish/v1"
  base_url = "https://%s%s" % (options['ip'],rest_url)
  response = requests.get(base_url, verify=False, auth=(options['username'], options['password']))
  data = response.json()
  if re.search(r"memory",options['get'].lower()):
    print("MemorySummary->TotalSystemMemoryGiB:", end=" ")
    print(data['MemorySummary']['TotalSystemMemoryGiB'])
  if re.search(r"tag|sku",options['get'].lower()):
    print("SKU:", end=" ")
    print(data['SKU'])
  if re.search(r"model",options['get'].lower()):
    print("Model", end=" ")
    print(data['Model'])
  if re.search(r"power",options['get'].lower()):
    print("PowerState:", end=" ")
    print(data['PowerState'])
  if re.search(r"bios",options['get'].lower()):
    print("BiosVersion:", end=" ")
    print(data['BiosVersion'])
  if re.search(r"hostname",options['get'].lower()):
    print("HostName:", end=" ")
    print(data['HostName'])

# Set iDRAC information

def set_idrac_info(options):
  if re.search(r"power", options['set'].lower()):
    rest_url   = "/redfish/v1/Systems/System.Embedded.1/Actions/ComputerSystem.Reset"
    reset_type = options['value'].lower()
    reset_type = re.sub(r"on","On", reset_type)
    reset_type = re.sub(r"off","ForceOff", reset_type)
    reset_type = re.sub(r"reset","GracefulRestart", reset_type)
    reset_type = re.sub(r"push|button","PushPowerButton", reset_type)
    payload    = {'ResetType': reset_type}
  else:
    return
  headers  = {'content-type': 'application/json'}
  base_url = "https://%s%s" % (options['ip'],rest_url)
  response = requests.post(base_url, data=json.dumps(payload), headers=headers, verify=False, auth=(options['username'], options['password']))
  status   = response.status_code
  if status == 204:
    print("\nPASS: status code %s returned, server power state successfully set to \"%s\"\n" % (status, options['value']))
  else:
    print("\nFAIL: Command failed, status code %s returned\n" % status)
    print(response.json())
    exit()

# Download file

def download_file(options,url,file):
  if options['download'] == True:
    if not os.path.exists(file):
      string  = "Downloading %s to %s" % (url,file)
      command = "wget %s -O %s" % (url,file)
      handle_output(options,string)

# Print results

def print_results(options,results):
  model_dir = "%s/%s" % (options['fwdir'], options['model'])
  for name,url in results.items(): 
    print()
    print(name)
    print(url)
    if options['download'] == True:
      if not os.path.exists(model_dir):
        os.mkdir(model_dir)
      file = os.file.basename(url)
      file = "%s/%s" % (model_dir, file)
      download_file(options, url, file)
  print()

# If we have no command line arguments print help

if sys.argv[-1] == sys.argv[0]:
  print_help(script_exe)
  exit()

# Get command line arguments

parser = argparse.ArgumentParser()
parser.add_argument("--ip", required=False)              # Specify IP of iDRAC
parser.add_argument("--get", required=False)             # Get Parameter
parser.add_argument("--set", required=False)             # Set Parameter
parser.add_argument("--type", required=False)            # Type e.g. BIOS (defaults to listing all)
parser.add_argument("--model", required=False)           # Model e.g. M610, R720, etc
parser.add_argument("--fwdir", required=False)           # Set a directory to download to
parser.add_argument("--search", required=False)          # Search for a term
parser.add_argument("--output", required=False)          # Output type, e.g. Text, HTML (defaults to Text)
parser.add_argument("--value", required=False)           # Used with set, to set a value, e.g. On for Power
parser.add_argument("--platform", required=False)        # Platform e.g. PowerEdge, PowerVault, etc (defaults to PowerEdge)
parser.add_argument("--username", required=False)        # Set Username
parser.add_argument("--password", required=False)        # Set Password
parser.add_argument("--all", action='store_true')        # Return all versions (by default only latest are returned)
parser.add_argument("--mask", action='store_true')       # Mask MAC addresses etc
parser.add_argument("--force", action='store_true')      # Ignore ping test etc
parser.add_argument("--version", action='store_true')    # Display version information
parser.add_argument("--options", action='store_true')    # Display options information
parser.add_argument("--download", action='store_true')   # Download file

options = vars(parser.parse_args())

# Handle version switch

if options['version']:
  script_exe = sys.argv[0]
  print_version(script_exe)
  exit()

# Handle options switch

if options['options']:
  script_exe = sys.argv[0]
  print_options(script_exe)
  exit()

# Handle download switch

if options["download"]:
  download = True
else:
  download = False

# Set default username

if not options['username']:
  options['username'] = "root"

# Set default password

if not options['password']:
  options['username'] = "calvin"

# Set default output type

if not options['output']:
  options['output'] = "text"

# Set default download directory

if not options['fwdir']:
  options['fwdir'] = def_dir

# Handle username switch

if not options['username']:
  options['username'] = "root"

# Handle password switch

if not options['password']:
  options['password'] = "calvin"

# Handle ip switch

if options['ip']:
  if not options['force'] == True:
    check_ping = check_ping(options['ip'])
    if check_ping == False:
      string = "Host %s not responding" % (options['ip'])
      exit()
  if options['get']:
    get_idrac_info(options)
  if options['set']:
    set_idrac_info(options)

# Handle platform switch and set default if not given

if not options['platform']:
  options['hwtype']   = "poweredge"
  options['hwupcase'] = "PowerEdge"
else:
  options['hwtype'] = options['platform'].lower()
  if re.search(r"vault",options['hwtype']):
    options['hwupcase'] = "PowerVault"
  else:
    options['hwupcase'] = options['hwtype'].capitalize()

if not options['type']:
  options['type'] = "list"

# Handle download switch and create download directory

if options['download'] == True:
  if not os.path.exists(options['fwdir']):
    os.mkdir(options['fwdir'])
  if options['model']:
    model_dir = options['fwdir']+"/"+options['model']
    if not os.path.exists(model_dir):
      os.mkdir(model_dir)

# Handle type switch

if re.search(r"manual|pdf",options['type']):
  print()
  if re.search(r"all",options['model']):
    models = get_model_list(options)
    for model_name in models: 
      options['model'] = model_name
      print_document_urls(options)
  else:
    print_document_urls(options)
  exit()

# Handle model switch

if options['model']:
  if re.search(r"all",options['model']):
    models = get_model_list(top_url)
    for model_name in models:
      options['model']    = model_name
      options['model']    = options['model'].lower()
      options['modelurl'] = "https://www.dell.com/support/home/en-au/product-support/product/%s-%s/drivers" % (options['hwtype'], options['model'])
      if options['type'] == "list":
        if len(options['model']) < 5:
          string = "%s %s:\t\t%s" % (options['hwupcase'], options['model'].upper(), options['modelurl'])
          handle_output(options,string)
        else:
          string = "%s %s:\t%s" % (options['hwupcase'], options['model'].upper(), options['modelurl'])
          handle_output(options, string)
      else:
        results = get_firmware_info(options, results)
        print_results(options, results)
  else:
    options['model']    = options['model'].lower()
    options['modelurl'] = "https://www.dell.com/support/home/en-au/product-support/product/%s-%s/drivers" % (options['hwtype'], options['model'])
    results = get_firmware_info(options, results)
    print_results(options, results)


