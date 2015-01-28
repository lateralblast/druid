#!/usr/bin/env ruby

# Name:         druid (Dell Retrieve Update Information and Download)
# Version:      0.0.4
# Release:      1
# License:      CC-BA (Creative Commons By Attrbution)
#               http://creativecommons.org/licenses/by/4.0/legalcode
# Group:        System
# Source:       N/A
# URL:          http://lateralblast.com.au/
# Distribution: UNIX
# Vendor:       Lateral Blast
# Packager:     Richard Spindler <richard@lateralblast.com.au>
# Description:  Ruby script to get available firmware from Dell site
#               http://www.dell.com/support/troubleshooting/us/en/19/ProductSelector/Select/FamilySelection?CategoryPath=all-products%2Fesuprt_ser_stor_net%2Fesuprt_poweredge&Family=PowerEdge&DisplayCrumbs=Product%2BType%40%2CServers%252c%2BStorage%2Band%2BNetworking%40%2CPowerEdge&rquery=na&sokey=solink

require 'nokogiri'
require 'open-uri'
require 'selenium-webdriver'
require 'phantomjs'
require 'getopt/std'

fw_dir   = Dir.pwd+"/firmware"
download = "n"
options  = "dhm:t:S:"
results  = {}

def print_results(results,model_name,fw_dir,download)
  fw_dir = fw_dir+"/"+model_name
  if !File.directory?(fw_dir) and download == "y"
    Dir.mkdir(fw_dir)
  end
  results.each do |name, url|
    puts
    puts name
    puts url
    if download == "y"
      puts
      file = File.basename(url)
      file = fw_dir+"/"+file
      if !File.exist?(file)
        puts "Downloading "+url+" to "+file
        %x[wget "#{url}" -O #{file}]
      end
    end
  end
  puts
  return
end

def get_version_string(string)
  #string  = string.gsub(/\.$/,"")
  strings = string.split(/ /)
  strings.each do |test|
    if test.match(/[0-9]/) and test.match(/\./)
      vers = test
      if test.match(/\,/)
        info = test.split(/\,/)
        info.each_with_index do |cell,index|
          if cell.match(/[0-9]/)
            if cell.match(/\./) or info[index-1].match(/version|revision/)
              vers = cell
            end
          end
        end
      end
      if vers.match(/^[0-9]|v/)
        vers = vers.gsub(/^v/,"")
        vers = vers.gsub(/^\.|\.$/,"")
        return vers
      end
    end
  end
  return string
end

def get_firmware_info(model_url,search_term,results)
  driver = Selenium::WebDriver.for :phantomjs
  driver.get(model_url)
  info = driver.page_source.split(/DriverName/)
  info.each do |data|
    if data.match(/DellHttpFileLocation/)
      name = data.split(/&quot;:&quot;/)[1].split(/&quot;,&quot;/)[0].gsub(/&amp;/,"&").gsub(/\[|\]/,"").gsub(/\\\//,"")
      vers = get_version_string(name)
      if !vers.match(/[0-9]/)
        vers = data.split(/DellVer/)[1].split(/&quot;:&quot;/)[1].split(/&quot;,&quot;/)[0]
      end
      url  = data.split(/DellHttpFileLocation/)[1].split(/&quot;:&quot;/)[1].split(/&quot;,&quot;/)[0].gsub(/\\/,"")
      if search_term == "list"
        name = name+" ("+vers+")"
        results[name] = url
      else
        if name.downcase.match(/#{search_term.downcase}/) or vers.downcase.match(/#{search_term.downcase}/)
          name = name+" ("+vers+")"
          results[name] = url
        end
      end
    end
  end
  return results
end

def get_model_list(top_url)
  models = []
  doc    = Nokogiri::HTML(open(top_url))
  doc.css('a.uif_link').each do |node|
    model_name = node[:id]
    if model_name.match(/poweredge/)
      model_name = model_name.split("-")[1]
      models.push(model_name)
    end
  end
  return models
end

def print_version()
  file_array = IO.readlines $0
  version    = file_array.grep(/^# Version/)[0].split(":")[1].gsub(/^\s+/,'').chomp
  packager   = file_array.grep(/^# Packager/)[0].split(":")[1].gsub(/^\s+/,'').chomp
  name       = file_array.grep(/^# Name/)[0].split(":")[1].gsub(/^\s+/,'').chomp
  puts name+" v. "+version+" "+packager
  return
end

def print_usage(options)
  puts
  puts "Usage: "+$0+" -["+options+"]"
  puts
  puts "-V:          Display version information"
  puts "-h:          Display usage information"
  puts "-m all:      Display firmware information for all machines"
  puts "             If no type is given a list of models will be returned"
  puts "-m MODEL:    Display firmware information for a specific model (eg. M620)"
  puts "-t:          Search for type of firmware e.g. BIOS"
  puts "-d:          Download firmware"
  puts "-S Hardware: Set hardware type to (Default is PowerEdge)"
  puts
  return
end

begin
  opt = Getopt::Std.getopts(options)
rescue
  print_usage(options)
  exit
end

if !opt["S"]
  hw_type   = "poweredge"
  hw_upcase = "PowerEdge"
else
  hw_type = opt["S"].downcase
  case hw_type
  when /vault/
    hw_upcase = "PowerVault"
  when /compellent/
    hw_upcase = hw_type.capitalize
  else
    hw_upcase = "PowerEdge"
  end
end
top_url  = "http://www.dell.com/support/troubleshooting/us/en/19/ProductSelector/Select/FamilySelection?CategoryPath=all-products%2Fesuprt_ser_stor_net%2Fesuprt_"+hw_type+"&Family="+hw_upcase+"&DisplayCrumbs=Product%2BType%40%2CServers%252c%2BStorage%2Band%2BNetworking%40%2C"+hw_upcase+"&rquery=na&sokey=solink"
base_url = "http://www.dell.com/support/drivers/us/en/19/Product/"+hw_type+"-"

if opt["V"]
  print_version()
end

if opt["h"]
  print_usage(options)
end

if opt["t"]
  search_term = opt["t"]
else
  search_term = "list"
end

if opt["d"]
  if !File.directory?(fw_dir)
    Dir.mkdir(fw_dir)
  end
  download = "y"
end

if opt["m"]
  model_name = opt["m"]
  if model_name.match(/all/)
    models = get_model_list(top_url)
    models.each do |model_name|
      model_url = base_url+model_name+"#"
      if search_term == "list"
        if model_name.length < 5
          puts hw_upcase+" "+model_name.upcase+":\t\t"+model_url
        else
          puts hw_upcase+" "+model_name.upcase+":\t"+model_url
        end
      else
        results   = get_firmware_info(model_url,search_term,results)
        print_results(results,model_name,fw_dir,download)
      end
    end
  else
    model_name = model_name.downcase
    model_url  = base_url+model_name+"#"
    results    = get_firmware_info(model_url,search_term,results)
    print_results(results,model_name,fw_dir,download)
  end
end


