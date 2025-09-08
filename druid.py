#!/usr/bin/env python
"""Python script to get available firmware from Dell site and check iDRAC"""

# pylint: disable=C0103
# pylint: disable=C0209
# pylint: disable=C0301
# pylint: disable=C0413
# pylint: disable=C0415
# pylint: disable=R0912
# pylint: disable=R0914
# pylint: disable=R0915
# pylint: disable=R1702
# pylint: disable=W0311
# pylint: disable=W0611
# pylint: disable=W0621
# pylint: disable=W0718

# Name:         druid (Dell Retrieve Update Information and Download)
# Version:      0.5.0
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
import importlib
import platform
import argparse
import socket
import time
import json
import csv
import sys
import os
import re

from os.path import expanduser
from io import BytesIO

# Set some defaults

script  = {}
results = {}
models  = []

script['name'] = "druid"
script['file'] = sys.argv[0]  
script['path'] = os.path.dirname(script['file'])
script['home'] = expanduser("~")
script['work'] = f"{script['home']}/{script['name']}"

try:
  from pip._internal import main
except ImportError:
  os.system("easy_install pip")
  os.system("pip install --upgrade pip")

def install_and_import(package):
  """Install and import a python module"""
  try:
    importlib.import_module(package)
  except ImportError:
    command = f"python3 -m pip install --user {package}"
    os.system(command)
  finally:
    globals()[package] = importlib.import_module(package)

try:
  import requests
except ImportError:
  install_and_import("requests")
  import requests

try:
  import urllib3
except ImportError:
  install_and_import("urllib3")
  import urllib3

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
  import pycurl
except ImportError:
  install_and_import("pycurl")
  import pycurl 

try:
  from selenium import webdriver
except ImportError:
  install_and_import("selenium")
  from selenium import webdriver

try:
  from webdriver_manager.chrome import ChromeDriverManager
except ImportError:
  install_and_import("webdriver_manager")
  from webdriver_manager.chrome import ChromeDriverManager

try:
  from selenium.webdriver.common.by import By
except ImportError:
  install_and_import("selenium")
  from selenium.webdriver.common.by import By

try:
  from selenium.webdriver.support.ui import WebDriverWait
except ImportError:
  install_and_import("selenium")
  from selenium.webdriver.support.ui import WebDriverWait

try:
  from selenium.webdriver.support import expected_conditions as EC
except ImportError:
  install_and_import("selenium")
  from selenium.webdriver.support import expected_conditions as EC

try:
  from bs4 import BeautifulSoup
except ImportError:
  install_and_import("bs4")
  from bs4 import BeautifulSoup

try:
  import lxml
except ImportError:
  install_and_import("lxml")
  import lxml

from lxml import etree

try:
  import wget
except ImportError:
  install_and_import("wget")
  import wget

try:
  import paramiko
except ImportError:
  install_and_import("paramiko")
  import paramiko

try:
  import pexpect
except ImportError:
  install_and_import("pexpect")
  import pexpect

try:
  import redfish
except ImportError:
  install_and_import("redfish")
  import redfish

try:
  from terminaltables import SingleTable
except ImportError:
  install_and_import("terminaltables")
  from terminaltables import SingleTable

try:
  from pygments import highlight
except ImportError:
  install_and_import("pygments")
  from pygments import highlight

from pygments.formatters.terminal256 import Terminal256Formatter
from pygments.lexers.web import JsonLexer

def print_version(file_name):
  """Print version"""
  file_array = file_to_array(file_name)
  version    = list(filter(lambda x: re.search(r"^# Version", x), file_array))[0].split(":")[1]
  version    = re.sub(r"\s+","",version)
  print(version)

def print_help(file_name):
  """Print help"""
  print("\n")
  command = f"{file_name} -h"
  os.system(command)
  print("\n")

def file_to_array(file_name):
  """Read a file into an array"""
  with open(file_name, encoding="utf-8") as file:
    file_array = file.readlines()
  return file_array

def print_options(file_name):
  """Print options"""
  file_array = file_to_array(file_name)
  opts_array = list(filter(lambda x:re.search(r"add_argument", x), file_array))
  print("\nOptions:\n")
  for line in opts_array:
    line = line.rstrip()
    if re.search(r"#",line):
      option = line.split('"')[1]
      info   = line.split("# ")[1]
      if len(option) < 8:
        o_string = f"{option}\t\t\t{info}"
      else:
        if len(option) < 16:
          o_string = f"{option}\t\t{info}"
        else:
          o_string = f"{option}\t{info}"
      print(o_string)
  print("\n")


def check_valid_ip(ip):
  """Check IP"""
  if not re.search(r"[a-z]",ip):
    try:
      socket.inet_pton(socket.AF_INET, ip)
    except AttributeError:
      try:
        socket.inet_aton(ip)
      except socket.error:
        return False
      return ip.count('.') == 3
    except socket.error:
      return False
  else:
    return True
  return False

def check_ping(ip):
  """Check host is up"""
  try:
    output = subprocess.check_output("ping -{} 1 {}".format('n' if platform.system().lower()=="windows" else 'c', ip), shell=True)
    return output
  except Exception:
    string = f"Warning:\tHost {ip} not responding"
    handle_output(options,string)
    return False

def handle_output(options, output):
  """Handle output"""
  if options['mask'] is True:
    if re.search(r"serial|address|host|id",output.lower()):
      if re.search(":",output):
        param  = output.split(":")[0]
        output = f"{param}: XXXXXXXX"
  print(output)

def execute_command(options, command):
  """Execute command"""
  with subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, ) as process:
    output = process.communicate()[0].decode()
  if options['verbose'] is True:
    string = f"Output:\n{output}"
    handle_output(options,string)

def print_document_urls(options):
  """Get document URLs"""
  if options['model']:
    if re.search(r"[m,r][0-9]1[0-9]",options['model'].lower()):
      base_owners_url = f"https://downloads.dell.com/manuals/all-products/esuprt_ser_stor_net/esuprt_{options['hwtype']}/{options['hwtype']}-"
      base_setup_url  = f"https://downloads.dell.com/manuals/all-products/esuprt_ser_stor_net/esuprt_{options['hwtype']}/{options['hwtype']}-"
    else:
      base_owners_url = f"https://dl.dell.com/topicspdf/{options['hwtype']}-"
      base_setup_url  = f"https://downloads.dell.com/manuals/all-products/esuprt_ser_stor_net/esuprt_{options['hwtype']}/{options['hwtype']}-"
  else:
    base_owners_url = f"https://dl.dell.com/topicspdf/{options['hwtype']}-"
    base_setup_url  = f"https://downloads.dell.com/manuals/all-products/esuprt_ser_stor_net/esuprt_{options['hwtype']}/{options['hwtype']}-"
  if re.search(r"[m,r][0-9]1[0-9]", options['model'].lower()):
    if re.search(r"r610", options['model'].lower()):
      owners_url = f"{base_owners_url}{options['model']}_owner%27s%20manual2_en-us.pdf"
    else:
      owners_url = f"{base_owners_url}{options['model']}_owner%27s%20manual_en-us.pdf"
  else:
    owners_url = f"{base_owners_url}{options['model']}_owners-manual_en-us.pdf"
  setup_url = f"{base_setup_url}{options['model']}_setup%20guide_en-us.pdf"
  string    = f"{options['hwupcase']} {options['model']}:"
  if options['quiet'] is False:
    handle_output(options, string)
    handle_output(options, owners_url)
    handle_output(options, setup_url)
  if options['download'] is True:
    for url in [ owners_url, setup_url ]:
      file = os.path.basename(url)
      file = f"{options['fwdir']}/{file}"
      download_file(options, url, file)
      if re.search(r"owner", file):
        if not os.path.exists(file):
          options['hwtype'] = options['hwupcase'].downcase
          url = f"http://topics-cdn.dell.com/pdf/{options['hwtype']}-{options['model']}_Owner's%20Manual_en-us.pdf"
          download_file(options, url, file)
  if options['quiet'] is False:
    print()

def start_web_driver():
  """Initiate web client"""
  from selenium import webdriver
  from selenium.webdriver.chrome.options import Options
  browser_options = Options()
  browser_options.add_experimental_option("excludeSwitches", ["enable-automation"])
  browser_options.add_experimental_option('useAutomationExtension', False)
  browser_options.add_argument('--disable-blink-features=AutomationControlled')
  browser_options.add_argument("--disable-extensions")
  browser_options.add_experimental_option("prefs", {
  "download.default_directory": options['fwdir']
  })
  if options['headless'] is True:
    browser_options.add_argument("--headless")
  driver = webdriver.Chrome(options = browser_options)
  driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36'})
  driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
  return driver

def get_model_list(options):
  """Get list of models"""
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

def process_servicetag_csv(options):
  csv_file = f"{options['fwdir']}/{options['servicetag']}.csv"
  if options['tables'] is True:
    tables = []
    table_data = []
  if options['tables'] is True:
    table_row = [ "Qty/Item", "P/N", "Description" ]
    table_data.append(table_row)
  with open(csv_file, encoding="utf-8") as file:
    reader = csv.reader(file)
    for row in reader:
      test = row[0]
      if not re.search("Component", test):
        if re.search(r"[0-9]", test):
          component = test
          if options['tables'] is True:
            headers = re.split(" : ", component)
            table_row = [ headers[0], "-----", headers[1] ]
            table_data.append(table_row)
          else:
            print(component)
        part_num = row[1]
        part_des = row[2]
        part_qty = row[3]
        if options['tables'] is True:
          part_qty  = f"{part_qty}x"
          table_row = [ part_qty, part_num, part_des ]
          table_data.append(table_row)
        else:
          string = f"{part_qty}x\t{part_num}\t{part_des}"
          print(string)
    if options['tables'] is True:
      table = SingleTable(table_data)
      table.inner_row_border = True
      print(table.table)

def get_servicetag_info(options, results):
  """Get Service Tag info from website"""
  name   = ""
  info   = ""
  driver = start_web_driver()
  html_file = f"{options['fwdir']}/{options['servicetag']}.html"
  conf_file = f"{options['fwdir']}/{options['servicetag']}_config.html"
  csv_file  = f"{options['fwdir']}/{options['servicetag']}.csv"
  if options['get'] == "config":
    if not os.path.exists(csv_file) or options['update'] is True:
      response_data = []
      def write_callback(data):
        response_data.append(data)
        return len(data)
      c = pycurl.Curl()
      try:
        c.setopt(c.URL, "https://www.dell.com/support/product-details/en-au/reviewspecs/export/8G5Q6Z2")
        c.setopt(c.POST, 1)
        c.setopt(c.POSTFIELDS, "")
        headers = [
          "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:142.0) Gecko/20100101 Firefox/142.0",
          "Accept: */*",
          "Accept-Language: en-US,en;q=0.5",
          "Accept-Encoding: gzip, deflate, br, zstd",
          "Referer: https://www.dell.com/support/product-details/en-au/servicetag/0-RHB1WndvOGZoSnZPVFBMK2ttVGxKUT090/overview",
          "X-Requested-With: XMLHttpRequest",
          "X-Robots-Tag: noindex",
          "Origin: https://www.dell.com",
          "Connection: keep-alive",
          "Cookie: akGD=%7B%22country%22%3A%22AU%22%2C%22region%22%3A%22VIC%22%7D; bm_ss=ab8e18ef4e; _abck=8772D1AD71F05E4A31958D0B93FA7891~-1~YAAQIe5UuAWZ0fWYAQAARiHfIQ4wuxhLhVDIvMgAu3eGYaBec6j2oP4Zb+p+EmDsma9noeyGEkXVohFfLTkYiRWzhM1n+2WzqscqVZeFQbDDyq/vy66ni79OhoFjjLx0q/Jora0/BBRdRHE+Sii7kKV9kSRZU87nXDXGUGZu+UzTThy2Qoi+RBASaOxEugnIn2FUth1EFcBIPtNQgjqynuA57gyRU08S7kDj2PoWH1w+TC2ltNfvSCor/U1wNx89woJPKEdyeplyo1mD4Xfwx2G28kVs6uqYIFm9wZCNOeccWJWRBeZoYTehZr6n92jow5ZtPBL59+vNrZxp8IDoYdSpNV4cqSsRjOvWIGH1yOJoCnvX3ZGgPAAFxIS4HUXo86Hl3vZkBW/yNlFM7UZRGLdttQvI+6G4ioANRTq+kSRoWbTNVoOKza8GMPt3MmXfTENhou5qBJ2diWU2q4dOmgAykQFHGVp5iEvO9527L39JW/QR71p+y8JTzogwbT1UatBQl7XDjxJlmVumEhv0Aq/A861BlvWp+KZr/ERJe4nUyHvxWMFnnp2SeHIDE/B4I5NNhQ/fd+j78NKX2NmifyX56ZDaJw8hVhqG514rCDmnBC9BaIbQ4mGcjMoM0m8VQ1U1RUuCAKFbnxb+oxZJn6NmnGzGfenK4DjLJ4wN3HM4YHcWTorl8OTENtwd97zZgpAbmOW9RaWSOMCKc2tZBbnpYADrWZBW+xmo/0Me8dR6k9kqfdQBSceC4CIjUsENAYZPdbVSAchmxftK2o/AT5ImulvV0C8bFCzKfq1FSp90kjgmDVgrRSh3+nDfCWPtdrHXvm5bGpRvA1uByzpe5SAr5h5ocXnY3RR9Y8/vGXlBcy/d771N/4KSjBJeYrAOYws6h9p6iYzTIEwHS6x4GWB0~0~-1~-1~~; bm_s=YAAQIe5UuAaZ0fWYAQAARiHfIQTobTwVIwjwenAavP67jMAexwTOlNR8CY2uiNYQ0kb6ZHAsk3KLA5fee2zZ96QLU/CKX7dqI65srDy/t7kvbRi9O71ykaLo8ccPqO1AYb2ZHjixGpWslkXnZpNxhufLpBl41fAmf7vfrrJg7J8z0RU3DVxz1+BJkpb/mab22/AH7Zqj0bEfgXqneA0hRe5KRU95f/5NvFy8FmxBX5mzdKH6vMVxak9SwGAHvjc5ZVwX9FeA0z5kVB7+h02FXMdaV5UQNaQ/LatwYu0PwBOcZrX3bDm3wckjuQZNMjV8mDAmOfWsbeQyNs8HN3KP3BN0Rg8jCQIGeKPxzdxTjwSTISo1PTVDDqvaTIxLuHbtoV8BzGkw7z0rfVqAJyBiBiIA0JIjPkFtl3J//eYFtxrqpUKOsvs67MX0pxiBs7DhvYPVWxr037GV6JDWsclbg+GW9I2xXDHQOq2yNY1YBTfo0+RwRpnoPqRbpuZ8hibkaVIwB9FDpFshjDdeZdr8734qywUEpT7rENB3z+Kn7bh/QHgSmCUcsJpGqi7eaCTEmd3kjza7Sr8=; bm_sz=B7BA06D5BD24BFA3D98B898CF85D2B48~YAAQIe5UuAeZ0fWYAQAARiHfIR1Dfm5/Bkh0BzAfpaNE9j7j1PMB2kvl3CudUdVET/O/x+CB+0sMyJLcvgZqzIgbasvFAtq+o9ACDACdaH2t7Hlw29sZC4G/HAXbcb0Mort7bGK3x5iogDRrBrUCqjQPLPVbPdjmLL+k+YSVIWfR1GG+VSokpH2BfjXqAqD+GO9A1rxFkuJiiGG0xb9TjHndPZ7RFi/xa3LFXN8RqMydCSd5bE10sfSapiNsQ/83fF0//7F8907fDD7/ergwyrAZ9yYO65TARa+n9dWKVVRy+2nH1OI//MZMaKMABKkEvVeaxuyiS5LfaaT69tQ+dHI1/T+UNSMuIx1qadwHq97aKTcOFJKfcD2qrHB8vkROVZX4CyaEhDNVHjIQtjEiNsO/9VvTAc5BEX9zrKyVDc62LRfHnfs+CANP7nnM18XG+6iliOfdlcDJf4iEE2kFFDliwEtMLeELYLQ+H0diNmzk4tSPDCtUbSkexYqzxgjWU/VjC+yElBg51/Zq1TkYRUB5/J3BKci3ypkecSv2U+ZAep4YXYM4ng==~3552323~3748659; eSupId=SID=ee30d2cb-41b8-4f2c-82ee-7575c302e694&apc=optiplex-7070-desktop; lwp=c=au&l=en&s=bsd&cs=aubsd1; OLRProduct=OLRProduct=8G5Q6Z2|; ak_bmsc=17323E9FC29F0BAF20B8E56EB7C12BCD~000000000000000000000000000000~YAAQIe5UuAyyzvWYAQAAsEGwIR3iS21xO1qdCJWmZYWqaY8c8DUpmRh5fjNY4RFgLha8E5V2Arb9tItUwxB7lDSTMQwxeWi5YohVXDQSyiOfYZjZHzSf3CK8PPj42ruaf92Jp36UP0M3QA+F6q9MWddy863WkDlYi/63IM6YT64inxv18KXYjL9nyEcsWmjKTfPYIY9ixdGjUEkjjMQtO35C4C0tAaC1YoXbB3kphshwwY9/MX29WpCCxGgTVgAp85fGaWoaEJesgyrBGMEOat5T1YzPBmyDRgKc+s5iTjOCSvdAsWbbujKsbpuGxlkT7JdMOpOWN5D4XBHyjmrdW0czciG3wtiwOG9g+rpPWdKiwLIxmm2Kg4BkfGKB7B7RCrs+9iM8cxwAMDhcVnbi6yh40asPOmbqtNAGxEAj9dHRys7IDjQwRH+4JjhCV8yod4q7YVtI2d8VRwBL90kZU6D13+RG68mt+1meBwCwnz+SQT5Jp6W6o5fGsxVSoQcuaCOshPa6tB0gpV57jA==; bm_so=F30A2B636B11FFA88B2375C1FD1B595DA4E4D38956DCF3B12CE3EE353A8DA8DD~YAAQHe5UuCmsKuyYAQAAKwbfIQQqgSYKWVfuq2e/MJrBYoePirNRaGdIOHV8/rWjbsnRpL/GreEfG0y9QteGuYURpmqd67lzSrEqfbwxVHVHIJ2LkU3CucQ31VhYgMA9Ss6R/KfdYmRVto5jRRP1LNWxaHZHqkaVAQICPRJ1HxyFDt0+RU5IraxlehJt/YVUjffPJFK9eqj7rSxlhb6E4JWUT6Sd+BeCqJvJJEtwDAyrQO4FVCO4atS/stndwgpWEKUNW5SiA0GUqcHogFNfWypWm3FTdZxxvswNZyQXkoktHJqTH21kSRJ6uTvUlGK2QU6Si5fRQGkS44RtjIYd0FR+YWxCF8bt5XHDR/TMul9/HWEppzPpg3YN1bYax3jjcSc/uJF05YSHcUxtcpUqllgE+bAGuAPyVBBb4yo0v21jAk+tjdvSY7Zihdypu2pIOi4+hwS7UZqqJX1Eqg==; bm_lso=F30A2B636B11FFA88B2375C1FD1B595DA4E4D38956DCF3B12CE3EE353A8DA8DD~YAAQHe5UuCmsKuyYAQAAKwbfIQQqgSYKWVfuq2e/MJrBYoePirNRaGdIOHV8/rWjbsnRpL/GreEfG0y9QteGuYURpmqd67lzSrEqfbwxVHVHIJ2LkU3CucQ31VhYgMA9Ss6R/KfdYmRVto5jRRP1LNWxaHZHqkaVAQICPRJ1HxyFDt0+RU5IraxlehJt/YVUjffPJFK9eqj7rSxlhb6E4JWUT6Sd+BeCqJvJJEtwDAyrQO4FVCO4atS/stndwgpWEKUNW5SiA0GUqcHogFNfWypWm3FTdZxxvswNZyQXkoktHJqTH21kSRJ6uTvUlGK2QU6Si5fRQGkS44RtjIYd0FR+YWxCF8bt5XHDR/TMul9/HWEppzPpg3YN1bYax3jjcSc/uJF05YSHcUxtcpUqllgE+bAGuAPyVBBb4yo0v21jAk+tjdvSY7Zihdypu2pIOi4+hwS7UZqqJX1Eqg==1757209888817; AMCV_4DD80861515CAB990A490D45%40AdobeOrg=179643557%7CMCIDTS%7C20339%7CMCMID%7C13316711671072964334141885059090447352%7CMCAID%7CNONE%7CvVersion%7C5.5.0; s_vnc365=1788745888434%26vn%3D2; bm_mi=C92A52003222658E28CBDE4058754629~YAAQIe5UuCqqzvWYAQAAXtCvIR0aIpD39vRltc1f8xh+cN624eQx0QtO4hDuo7TWAG1OD4bZIfzAobbR5DPc0/7IwF9zUgvDTRzTyv9tr7OyytzQxwvAWOM3Ff70PqeJ1WEzE0TY48FdlQTmPD8wiBselUUVXOYw/eD/CHcN/wjrEEWbRW61EHYLHry55NnJB1cbi7Q72khKb9XOeR9CDFMjvrVmA1GRvQHjd+xQsrZr+Q5Tqjeg3xZf1YarYfhc0LbEWFyzgJgS3daCx/6ObR1JCUOPXtKbsqKf24buStTOA/0DG/xD7wCYUwH5keQAIyhRswq3yLRmNe0Ckji9uBrKLsmQJ/UFNoAFIGrrr7rqvFa20asB+VsojXsWwqUXnosWOYTGhzMEGHnt2frPfrLyigHKbhzZZ658ATt5QC2M~1; bm_sv=937C455442C97A77CEC40A71F157A276~YAAQIe5UuP2rzvWYAQAAK+mvIR1a9jFiHIZZ+/mBUDq+HqzluIlasH538RACAaI3JUEMGGQwm0MGTTQwRnQBqf/raxo3EEOQVblCqi/0Q3ia1BfoTl1kxlxWJqlVuTJjpkwN6KKGzRL4KmOT0qbMRj0KPncRQzqUWDQMbADhuJTY1gOA5dButrRD/BeFtLfpOGUXXnzE/rVnvbWlDf+f4p4GPx8uBOZN7lvlxQQ21RUPyW9upsIXrZ+GZQBpta4=~1; txUid=Co+qL2i82Olb26uABda5Ag==; VOCAAS_STICKY_SESSION=C957E01CA33C4C716EDE2999C48EB332; AWSALB=myzYLq2dvc0UYjGMC+uVXwY89FGjExg07qWiQzcGBmZzWW7q1RIHXulvvUeKzQ2jEZjN/LkJrvrHF/ufSVMI5qxJ2oiS/4BN/pKB4CQtCDeTIuLqMBtu/rr7TaN4; AWSALBCORS=myzYLq2dvc0UYjGMC+uVXwY89FGjExg07qWiQzcGBmZzWW7q1RIHXulvvUeKzQ2jEZjN/LkJrvrHF/ufSVMI5qxJ2oiS/4BN/pKB4CQtCDeTIuLqMBtu/rr7TaN4; spr_device_id=170b2410-8b86-11f0-b45a-075afb61551f; spr-analytics=true; lang=en; connect.sid=s%3Awww-1tq2bTjXx4MsPQj6t7iL7X1fO3E0dfIo.ZHcpsMdrtns4Ji0K59ztcDIxhKxQcpsYSPqeAsT9aH4; sess-exp-time=Sun, 7 Sep 2025 01:30:50 GMT; DellCEMSession=82A44853A74F6896D9B7C07A26A92082; TS013d7cf0=01f7eb84748b90c4a30eb05df157f5b6e5d4b55c11bd888ad6fd6357625c2ddf7a375fc216eea4ddc1364af77e0272a98a58307db2; TS017b1cb5=01765abcd1299a2210722598d55d89070679cf24758924176eb30fb4dfbe06b6d0ce2e2558e221261b9904910fd24214f542acedf3; um_g_uc=false; akavpau_maintenance_vp=1757210195~id=34b37b184b0f99da099c3c5acce8bd45; s_c49=c%3Dau%26l%3Den%26s%3Dbsd%26cs%3Daubsd1%26servicetag%3D8g5q6z2%26systemid%3Doptiplex-7070-desktop; gpv_pn=au%7Cen%7Caubsd1%7Cbsd%7Cesupport-productsupport-dep%7Cservicetag; s_ips=378; s_tp=3477; s_ppv=au%257Cen%257Caubsd1%257Cbsd%257Cesupport-productsupport-dep%257Cservicetag%2C11%2C11%2C11%2C378%2C9%2C1; cidlid=%3A%3A; s_ivc=true; s_cc=true; dc-ctxt=c=AU&l=en&sdn=work&uh=44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a&ut=1757209888702; s_sq=dellglobalonlinemaster%3D%2526c.%2526a.%2526activitymap.%2526page%253Dau%25257Cen%25257Caubsd1%25257Cbsd%25257Cesupport-productsupport-dep%25257Cservicetag%2526link%253DProduct%252520Specifications%2526region%253Daccordion-item-content-249556425%2526pageIDType%253D1%2526.activitymap%2526.a%2526.c%2526pid%253Dau%25257Cen%25257Caubsd1%25257Cbsd%25257Cesupport-productsupport-dep%25257Cservicetag%2526pidt%253D1%2526oid%253Djavascript%25253Avoid%2525280%252529%2526ot%253DA",
          "Sec-Fetch-Dest: empty",
          "Sec-Fetch-Mode: cors",
          "Sec-Fetch-Site: same-origin",
          "Priority: u=0",
          "Content-Length: 0"
        ]
        c.setopt(c.HTTPHEADER, headers)
        c.setopt(c.WRITEFUNCTION, write_callback)
        c.setopt(c.ENCODING, "")
        c.setopt(c.FOLLOWLOCATION, 1)
        c.setopt(c.TIMEOUT, 30)
        c.perform()
        if response_data:
          full_response = b''.join(response_data)
          try:
            decoded_response = full_response.decode('utf-8')
          except UnicodeDecodeError:
            try:
              decoded_response = full_response.decode('latin-1')
            except:
              decoded_response = full_response.decode('utf-8', errors='replace')
          with open(csv_file, 'w', encoding='utf-8') as f:
            f.write(decoded_response)
        else:
          print("No response data received!")
          return None
      except pycurl.error as e:
        print(f"cURL error: {e}")
        return None
      finally:
        c.close()
      if not os.path.exists(html_file) and options['update'] is False:
        driver.get(options['servicetagurl'])
        time.sleep(2)
        html_doc = driver.page_source
        with open(html_file, "w", encoding="utf-8") as file:
          file.write(html_doc)
      if os.path.exists(csv_file):
        process_servicetag_csv(options)
    else:
      process_servicetag_csv(options)
  else:
    if os.path.exists(html_file) and options['update'] is False:
      with open(html_file, encoding="utf-8") as file:
        html_doc = file.read()
    else:
      driver.get(options['servicetagurl'])
      time.sleep(5)
      html_doc = driver.page_source
      with open(html_file, "w", encoding="utf-8") as file:
        file.write(html_doc)
      with open(html_file, encoding="utf-8") as file:
        html_doc = file.read()
    html_doc = BeautifulSoup(html_doc, features='lxml')
    for section in html_doc.select('p'):
      if re.search("warrantyExpiringLabel mb-0 ml-1 mr-1", str(section)):
        name = "Warranty"
        info = str(section).split("\n", maxsplit=1)[0].split(">")[1].split("<")[0]
        results[name] = info
  return results

def handle_old_firmware_info(options, results):
  return results

def get_firmware_info(options, results):
  """Get Firmware info from website"""
  name   = ""
  link   = ""
  links  = []
  html_file = f"{options['workdir']}/{options['model']}_all.html"
  if os.path.exists(html_file) and options['update'] is False:
    with open(html_file, encoding="utf-8") as file:
      html_doc = file.read()
  else:
    driver = start_web_driver()
    driver.get(options['modelurl'])
    WebDriverWait(driver, 5).until(
      EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))).click()
    html_doc = driver.page_source
    with open(html_file, "w", encoding="utf-8") as file:
      html_doc = driver.page_source
      file.write(html_doc)
  if re.search(r"nav__icon dds__pl-3", (html_doc)):
    html_doc = BeautifulSoup(html_doc, features='lxml')
    for span in html_doc.select("span"):
      string = str(span)
      if re.search(r"dds__table__cell", string):
        if not re.search(r">Action<", string):
          if not re.search(r"dds__badge dds__badge--md dds__badge--light dds__badge--", string):
            if re.search(r"0-PRODUCT-", string):
              if re.search(r"[a-z,A-Z]", name):
                name = re.sub(r"\s+", " ", name)
                name = re.sub(r"&amp;", "and", name)
                line = string
                idno = line.split('0-PRODUCT-')[1]
                idno = idno.split('"')[0]
                link = "https://www.dell.com/support/home/en-au/drivers/driversdetails?driverid=%s" % (idno)
                if re.search(r"list|all",options['type']) or name.lower().count(options['type'].lower()) > 0:
                  links.append(link)
                  results[name] = link
              name = ""
              line = ""
            else:
              line = string
              line = line.split('">')[1]
              line = line.split('</span')[0]
              line = re.sub(r"^\s+|\s+$", "", line)
              line = re.sub(r"\.$", "", line)
              if name == "":
                name = line
              else:
                name = "%s %s" % (name, line)
  else:
    html_doc = BeautifulSoup(html_doc, features='lxml')
    for section in html_doc.select("section"):
      for table in section.select("table"):
        for row in table.select("tr"):
          keyid = ""
          if re.search(r"tableRow_", str(row)):
            keyid = str(row)
            keyid = keyid.split('tableRow_')[1]
            keyid = keyid.split('"')[0]
            keyid = keyid.lower()
            link  = f"https://www.dell.com/support/home/en-us/drivers/driversdetails?driverid={keyid}"
            for column in row.select("td"):
              if re.search(r"dl-desk-view", str(column)):
                name = str(column)
                name = name.split('dl-desk-view">')[1]
                name = name.split('<span')[0]
                name = re.sub(r"^\s+|\s+$", "", name)
                name = re.sub(r"\.$", "", name)
              else:
                if re.search(r"aria-label", str(column)):
                  name = str(column)
                  name = name.split('aria-label="')[1]
                  name = name.split('" class=')[0]
                  name = re.sub(r"^\s+|\s+$|Expand to view details of ", "", name)
                  name = re.sub(r"\.$", "", name)
          if re.search(r"[a-z,A-Z]", name):
            name = re.sub(r"\s+", " ", name)
            name = re.sub(r"&amp;", "and", name)
            if re.search(r"list|all",options['type']) or name.lower().count(options['type'].lower()) > 0:
              if link not in links:
                links.append(link)
                results[name] = link
  return results

def check_idrac_redfish(options, base_url):
  """Check iDRAC redfish support"""
  response = requests.get(base_url, verify=False, auth=(options['username'], options['password']), timeout=30)
  if response.status_code != 200:
    print("\nWARNING: iDRAC version installed does not support this feature using Redfish API\n")
    sys.exit()

def get_idrac_ssh_info(options):
  """Get iDRAC information via SSH"""
  if re.search(r"inventory", options['get'].lower()):
    command = "racadm hwinventory"
  else:
    command = f"racadm {options['get']}"
  ssh_session = start_ssh_session(options)
  ssh_session.expect("/admin1-> ")
  ssh_session.sendline(command)
  ssh_session.expect("/admin1-> ")
  output = ssh_session.before
  output = output.decode()
  return output

def set_idrac_ssh_info(options):
  """Get iDRAC information via SSH"""
  if re.search(r"inventory", options['get'].lower()):
    command = "racadm hwinventory"
  else:
    command = f"racadm {options['set']}"
  ssh_session = start_ssh_session(options)
  ssh_session.expect("/admin1-> ")
  ssh_session.sendline(command)
  ssh_session.expect("/admin1-> ")
  output = ssh_session.before
  output = output.decode()
  return output

def get_idrac_ssh_hw_inventory(options):
  """Get iDRAC hardware inventory via SSH"""
  d_json = []
  d_text = []
  inv_file  = f"{options['workdir']}/{options['ip']}_hwinv.text"
  json_file = f"{options['workdir']}/{options['ip']}_hwinv.json"
  if not os.path.exists(inv_file) or not os.path.exists(json_file) or options['update'] is True:
    hw_inv = get_idrac_ssh_info(options)
    with open(inv_file, "w", encoding="utf-8") as file:
      file.write(hw_inv)
    hw_inv = file_to_array(inv_file)
    items  = filter(lambda a: "InstanceID:" in a, hw_inv)
    items  = len((list(items)))
    instance = ""
    d_json.append("{")
    for index, line in enumerate(hw_inv):
      line = line.rstrip()
      if options['text'] is True and options['print'] is True:
        d_text.append(line)
      else:
        if re.search(r"InstanceID:", line):
          instance = line.split(": ")[-1]
          instance = re.sub(r"\]", "", instance)
          string   = "  \"%s\": {" % (instance)
          d_json.append(string)
          items = items-1
        else:
          if re.search(r"---", line) and not re.search("[A-Z]", line):
            if items > 0:
              d_json.append("  },")
            else:
              d_json.append("  }")
          else:
            if re.search(r"^[A-Z]", line):
              (param, value) = line.split(" = ")
              if re.search(r"---", hw_inv[index+1]):
                string = "    \"%s\": \"%s\"" % (param, value)
              else:
                string = "    \"%s\": \"%s\"," % (param, value)
              d_json.append(string)
    d_json.append("}")
    d_json = "\n".join(d_json)
    d_text = "\n".join(d_text)
    if os.path.exists(inv_file) or options['update'] is True:
      with open(inv_file, "w", encoding="utf-8") as file:
        file.write(d_text)
    if os.path.exists(json_file) or options['update'] is True:
      with open(json_file, "w", encoding="utf-8") as file:
        file.write(d_json)
  if options['text'] is True:
    output = file_to_array(inv_file)
    for line in output:
      line = line.rstrip()
      if options['print'] is True:
        print(line)
  if options['json'] is True:
    with open(json_file, encoding="utf-8") as file:
      json_data = file.read()
      json_data = json.loads(json_data)
      json_data = json.dumps(json_data, indent=1)
      output = highlight(
        json_data,
        lexer=JsonLexer(),
        formatter=Terminal256Formatter(),
      )
      if options['print'] is True:
        print(output)
    file.close()
  return output

def get_idrac_redfish_info(options):
  """Get iDRAC information via Redfish"""
  if re.search(r"memory|tag|sku|power|model|bios|cpu|hostname",options['get'].lower()):
    rest_url = "/redfish/v1/Systems/System.Embedded.1"
  else:
    rest_url = "/redfish/v1"
  base_url = f"https://{options['ip']}{rest_url}"
  response = requests.get(base_url, verify=False, auth=(options['username'], options['password']), timeout=30)
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

def set_idrac_redfish_info(options):
  """Set iDRAC information via Redfish"""
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
  base_url = f"https://{options['ip']}{rest_url}"
  response = requests.post(base_url, data=json.dumps(payload), headers=headers, verify=False, auth=(options['username'], options['password']), timeout=30)
  status   = response.status_code
  if status == 204:
    print("\nPASS: status code %s returned, server power state successfully set to \"%s\"\n" % (status, options['value']))
  else:
    print("\nFAIL: Command failed, status code %s returned\n" % status)
    print(response.json())
    sys.exit()

def download_file(options, link, file):
  """Download file"""
  if options['force'] is True or options['update'] is True:
    if os.path.exists(file):
      os.remove(file)
  if not os.path.exists(file):
    if options['quiet'] is False:
      string  = f"Downloading {link} to {file}"
      print(string)
    response = requests.get(link)
    with open(file, 'wb') as file:
      file.write(response.content)

def download_driverid_files(options):
  """Download driverid files"""
  url    = options['driverid']
  link   = ""
  keyid  = url.split("=")[1]
  html_file = f"{options['workdir']}/{keyid}.html"
  model_dir = f"{options['fwdir']}/{options['model']}"
  if os.path.exists(html_file) and options['update'] is False:
    with open(html_file, encoding="utf-8") as file:
      html_doc = file.read()
  else:
    driver = start_web_driver()
    driver.get(url)
    time.sleep(5)
    html_doc = driver.page_source
    with open(html_file, "w", encoding="utf-8") as file:
      html_doc = driver.page_source
      file.write(html_doc)
  html_doc = BeautifulSoup(html_doc, features='lxml')
  for span in html_doc.select("span"):
    line = str(span)
    if re.search("driversDownload", line):
      if re.search("aria-label", line):
        found = False
        link  = line.split("href=")[1]
        link  = link.split('"')[1]
        if options['ext']:
          if re.search(options['ext'].lower(), link.lower()):
            found = True
        else:
          found = True
        if found is True: 
          if options['list'] is True or options['verbose'] is True:
            print(link)
          if options['download'] is True:
            if not os.path.exists(model_dir):
              os.mkdir(model_dir)
            file = os.path.basename(link)
            file = f"{model_dir}/{file}"
            download_file(options, link, file)

def start_ssh_session(options):
  """Initiate SSH Session"""
  ssh_command = "ssh -o StrictHostKeyChecking=no"
  ssh_command = f"{ssh_command} {options['username']}@{options['ip']}"
  ssh_session = pexpect.spawn(ssh_command)
  ssh_session.expect("assword: ")
  ssh_session.sendline(options['password'])
  return ssh_session

def print_results(options, results):
  """Print results"""
  model_dir = f"{options['fwdir']}/{options['model']}"
  total_res = len(results)
  found = False
  if options['json'] is True:
    print("{")
  counter = 0
  for name, url in results.items():
    counter = counter+1
    version = ""
    descs = []
    desc  = ""
    if options['json'] is True:
      fields = name.split(" ")
      for field in fields:
        if re.search(r"[0-9]\.[0-9]|^[v,V][0-9]|^[v|V]\.[0-9]", field):
          version = field
        else:
          if not re.search(r"ersion", field):
            descs.append(field)
      if not re.search(r"[0-9]", version):
        fields = url.split("_")
        for field in fields:
          if re.search(r"[0-9]\.[0-9]", field):
            version = field
      if re.search(r"\,", version):
        version = version.split(",")[-1]
      version = re.sub(r"^[v|V]", "", version)
      version = re.sub(r"[A-Z,a-z]", "", version)
      version = re.sub(r"^\.|\.$", "", version)
      desc = " ".join(descs)
      desc = re.sub(r"\,$|\.$", "", desc)
      string = "  '%s': {" % (desc)
      print(string)
      string = "    'version': '%s'," % (version)
      print(string)
      string = "    'url': '%s'" % (url)
      print(string)
      if counter < total_res:
        print("  },")
      else:
        print("  }")
    else:
      if re.search("all", options['search']):
        found = True
        if options['quiet'] is False:
          print()
          print(name)
          print(url)
        if found is True:
          if options['download'] is True or options['list'] is True:
            options['driverid'] = url
            download_driverid_files(options)
      else:
        found = False
        lc_name = name.lower()
        lc_url  = url.lower()
        lc_search = options['search'].lower()
        if lc_search in lc_name or lc_search in lc_url:
          found = True
          if options['quiet'] is False:
            print()
            print(name)
            print(url)
          if found is True:
            if options['download'] is True or options['list'] is True:
              options['driverid'] = url
              download_driverid_files(options)
  if options['json'] is True:
    print("}")
  else:
    if options['quiet'] is False:
      print()

if sys.argv[-1] == sys.argv[0]:
  print_help(script['file'])
  sys.exit()

# Get command line arguments

parser = argparse.ArgumentParser()
parser.add_argument("--ip", required=False)               # Specify IP of iDRAC
parser.add_argument("--ext", required=False)              # OS/Extension type
parser.add_argument("--get", required=False)              # Get Parameter
parser.add_argument("--set", required=False)              # Set Parameter
parser.add_argument("--type", required=False)             # Type e.g. BIOS (defaults to listing all)
parser.add_argument("--model", required=False)            # Model e.g. M610, R720, etc
parser.add_argument("--fwdir", required=False)            # Set a directory to download to
parser.add_argument("--check", required=False)            # Check installed against available (e.g. inventory)
parser.add_argument("--cookie", required=False)           # Cookie file
parser.add_argument("--search", required=False)           # Search for a term
parser.add_argument("--output", required=False)           # Output type, e.g. Text, HTML (defaults to Text)
parser.add_argument("--value", required=False)            # Used with set, to set a value, e.g. On for Power
parser.add_argument("--method", required=False)           # Method to get iDRAC information (e.g. SSH or Redfish)
parser.add_argument("--workdir", required=False)          # Work directory
parser.add_argument("--driverid", required=False)         # Driver ID
parser.add_argument("--platform", required=False)         # Platform e.g. PowerEdge, PowerVault, etc (defaults to PowerEdge)
parser.add_argument("--username", required=False)         # Set Username
parser.add_argument("--password", required=False)         # Set Password
parser.add_argument("--servicetag", required=False)       # Service Tag
parser.add_argument("--all", action='store_true')         # Return all versions (by default only latest are returned)
parser.add_argument("--ssh", action='store_true')         # Use SSH for iDRAC
parser.add_argument("--json", action='store_true')        # Process/output data in JSON
parser.add_argument("--list", action='store_true')        # Return full list of download URLs
parser.add_argument("--mask", action='store_true')        # Mask MAC addresses etc
parser.add_argument("--ping", action='store_true')        # Ping test host as part of getting iDRAC/Redfish data
parser.add_argument("--text", action='store_true')        # Output in text
parser.add_argument("--force", action='store_true')       # Ignore ping test etc
parser.add_argument("--print", action='store_true')       # Print out information (e.g. inventory)
parser.add_argument("--quiet", action='store_true')       # Quiet output
parser.add_argument("--tables", action='store_true')      # Format output in tables
parser.add_argument("--update", action='store_true')      # If file exists update it with latest data
parser.add_argument("--options", action='store_true')     # Display options information
parser.add_argument("--version", action='store_true')     # Display version information
parser.add_argument("--verbose", action='store_true')     # Verbose flag
parser.add_argument("--download", action='store_true')    # Download file
parser.add_argument("--nonheadless", action='store_true') # Non headless mode (useful for debugging)

options = vars(parser.parse_args())

if options['version']:
  print_version(script['file'])
  sys.exit()

if options['options']:
  print_options(script['file'])
  sys.exit()

if options['nonheadless']:
  options['headless'] = False
else:
  options['headless'] = True

if not options['workdir']:
  options['workdir'] = script['work']

if not options['cookie']:
  options['cookie'] = f"{options['workdir']}/cookie"

if not options['username']:
  options['username'] = "root"

if not options['password']:
  options['username'] = "calvin"

if not options['output']:
  options['output'] = "text"

if not options['fwdir']:
  options['fwdir'] = script['work']

if not os.path.exists(options['fwdir']):
  os.mkdir(options['fwdir'])

if not options['username']:
  options['username'] = "root"

if not options['password']:
  options['password'] = "calvin"

if not options['search']:
  options['search'] = "all"

if options['update']:
  options['update'] = True
else:
  options['update'] = False

if options['tables']:
  options['tables'] = True
else:
  options['tables'] = False

if options['download'] is True:
  options['list'] = True

if options['ip']:
  if options['ping'] is True:
    check_ping = check_ping(options['ip'])
    if check_ping is False:
      string = f"Host {options['ip']} not responding"
      if options['quiet'] is False:
        print(string)
      sys.exit()
  if options['check']:
    if re.search(r"inventory", options['check']):
      options['get'] = options['check']
      #parse_idrac_ssh_hw_inventory(options)
  else:
    if options['get']:
      if re.search(r"inventory", options['get']):
        get_idrac_ssh_hw_inventory(options)
      else:
        if options['ssh'] is True:
          get_idrac_redfish_info(options)
        else:
          get_idrac_ssh_info(options)
    if options['set']:
      if options['ssh'] is True:
        set_idrac_redfish_info(options)
      else:
        set_idrac_ssh_info(options)

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

if options['download'] is True:
  if not os.path.exists(options['fwdir']):
    os.mkdir(options['fwdir'])
  if options['model']:
    model_dir = options['fwdir']+"/"+options['model']
    if not os.path.exists(model_dir):
      os.mkdir(model_dir)

if options['driverid']:
  download_driverid_files(options)
  sys.exit()

if re.search(r"manual|pdf",options['type']):
  if options['quiet'] is False:
    print()
  if re.search(r"all",options['model']):
    models = get_model_list(options)
    for model_name in models:
      options['model'] = model_name
      print_document_urls(options)
  else:
    print_document_urls(options)
  sys.exit()

if options['servicetag']:
  if not options['get']:
    options['get'] = "warranty"
  service_tags = []
  if re.search(",", options['servicetag']):
    service_tags = options['servicetag'].split(",")
  else:
    service_tags.append(options['servicetag'])
  for service_tag in service_tags:
    options['servicetag'] = service_tag
    options['servicetopurl'] = f"https://www.dell.com/support/home/en-au/product-support/servicetag/{options['servicetag']}/overview#"
    options['servicetagurl'] = f"https://www.dell.com/support/product-details/en-au/ReviewSpecs/GetOriginalConfiguration?serviceTag={options['servicetag']}&showOriginalConfig=true&showCurrentConfig=true"
    options['servicecsvurl'] = f"https://www.dell.com/support/product-details/en-au/reviewspecs/export/${options['servicetag']}"
    if options['verbose'] is True:
      string = f"URL: {options['servicetagurl']}"
      if options['quiet'] is False:
        print(string)
    results = get_servicetag_info(options, results)
    print_results(options, results)

if options['model']:
  if re.search(r"all",options['model']):
    models = get_model_list(options)
    for model_name in models:
      options['model']    = model_name
      options['model']    = options['model'].lower()
      options['modelurl'] = f"https://www.dell.com/support/home/en-au/product-support/product/{options['hwtype']}-{options['model']}/drivers"
      if options['type'] == "list":
        if len(options['model']) < 5:
          string = f"{options['hwupcase']} {options['model'].upper()}:\t\t{options['modelurl']}"
          handle_output(options,string)
        else:
          string = f"{options['hwupcase']} {options['model'].upper()}:\t{options['modelurl']}"
          handle_output(options, string)
      else:
        if options['verbose'] is True:
          string = f"URL: {options['modelurl']}"
        results = get_firmware_info(options, results)
        print_results(options, results)
  else:
    options['model']    = options['model'].lower()
    options['modelurl'] = f"https://www.dell.com/support/home/en-au/product-support/product/{options['hwtype']}-{options['model']}/drivers"
    if options['verbose'] is True:
      string = f"URL: {options['modelurl']}"
      if options['quiet'] is False:
        print(string)
    results = get_firmware_info(options, results)
    print_results(options, results)
