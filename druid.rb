#!/usr/bin/env ruby -W:no-deprecated

# Name:         druid (Dell Retrieve Update Information and Download)
# Version:      0.0.8
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

# Install gems if they can't be loaded

def install_gem(load_name, install_name)
  puts "Information:\tInstalling #{install_name}"
  %x[gem install #{install_name}]
  Gem.clear_paths
  require "#{load_name}"
end

# Required gem list

gem_list = [ "rubygems", "nokogiri", "open-uri", "getopt/std", "fileutils", "selenium-webdriver", "mechanize" ]

# Try to load gems

for gem_name in gem_list
  begin
    require "#{gem_name}"
  rescue LoadError
    install_gem(gem_name, gem_name)
  end
end

fw_dir   = Dir.pwd+"/firmware"
download = "n"
options  = "Adhm:p:o:t:S:"
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

def get_firmware_info(model_url,search_term,results,get_all)
  opt = Selenium::WebDriver::Firefox::Options.new
  opt.add_argument('--headless')
  driver = Selenium::WebDriver.for :firefox, :options => opt
  driver.get(model_url)
  sleep(5)
  if get_all == true
    driver.find_element(id: "paginationRow").click
    sleep(5)
  end
  info = driver.page_source
  doc  = Nokogiri::HTML(info)
  name = ""
  link = ""
  doc.search("section").each do |section|
    section.search("table").each do |table|
      table.search("tr").each do |row|
        if !row.text.match(/NameCategoryRelease/)
          row.search("td").each do |column|
            if column.to_s.match(/href/)
              if column.to_s.match(/Download/)
                link = column.to_s.split(/href="/)[1].split(/" class="/)[0]
              end
            else
              if column.to_s.match(/dl-desk-view/)
                name = column.text
              else
                name = name+", "+column.text
              end
            end
          end
          if name.match(/[a-z]/)
            if search_term.match(/list/) or name.downcase.match(/#{search_term.downcase}/)
              results[name] = link
            end
          end
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

def print_document_urls(model_name,base_url,hw_upcase,fw_dir,download)
  owners_url = base_url+model_name+"_owner%27s%20manual_en-us.pdf"
  setup_url  = base_url+model_name+"_setup%20guide_en-us.pdf"
  fw_dir = fw_dir+"/"+model_name
  if !File.directory?(fw_dir) and download == "y"
    Dir.mkdir(fw_dir)
  end
  puts hw_upcase+" "+model_name.upcase+":"
  puts owners_url
  puts setup_url
  if download == "y"
    [ owners_url, setup_url ].each do |url|
      file = File.basename(url)
      file = fw_dir+"/"+file
      if !File.exist?(file)
        puts "Downloading "+url+" to "+file
        %x[wget "#{url}" -O #{file}]
      end
      if file.match(/owner/)
        if !File.size?(file)
          hw_type = hw_upcase.downcase
          url     = "http://topics-cdn.dell.com/pdf/"+hw_type+"-"+model_name+"_Owner's%20Manual_en-us.pdf"
          puts "Downloading "+url+" to "+file
          %x[wget "#{url}" -O #{file}]
        end
      end
    end
  end
  puts
  return
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
  puts "-A:          Display all versions (by default only latest will be shown)"
  puts "-m all:      Display firmware information for all machines"
  puts "             If no type is given a list of models will be returned"
  puts "-m MODEL:    Display firmware information for a specific model (eg. M620)"
  puts "-o OS:       Search by OS (not yet implemented)"
  puts "-t:          Search for type of firmware e.g. BIOS"
  puts "-d:          Download firmware or documentation"
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
if opt["m"]
  base_url = "http://www.dell.com/support/drivers/us/en/19/Product/"+hw_type+"-"
else
  base_url = "ftp://ftp.dell.com/Manuals/all-products/esuprt_ser_stor_net/esuprt_"+hw_type+"/"+hw_type+"-"
end

if opt['A']
  get_all = true
else
  get_all = false
end

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

if opt["p"]
  model_name = opt["p"]
  puts
  if model_name.match(/all/)
    models = get_model_list(top_url)
    models.each do |model_name|
      print_document_urls(model_name,base_url,hw_upcase,fw_dir,download)
    end
  else
    print_document_urls(model_name,base_url,hw_upcase,fw_dir,download)
  end
end

if opt["m"]
  model_name = opt["m"]
  if model_name.match(/all/)
    models = get_model_list(top_url)
    models.each do |model_name|
      # model_url = base_url+model_name+"#"
      model_url = "https://www.dell.com/support/home/en-au/product-support/product/"+hw_type+"-"+model_name+"/drivers"
      if search_term == "list"
        if model_name.length < 5
          puts hw_upcase+" "+model_name.upcase+":\t\t"+model_url
        else
          puts hw_upcase+" "+model_name.upcase+":\t"+model_url
        end
      else
        results = get_firmware_info(model_url,search_term,results,get_all)
        print_results(results,model_name,fw_dir,download)
      end
    end
  else
    model_name = model_name.downcase
    model_url  = "https://www.dell.com/support/home/en-au/product-support/product/"+hw_type+"-"+model_name+"/drivers"
    # model_url  = base_url+model_name+"#"
    puts model_url
    results = get_firmware_info(model_url,search_term,results,get_all)
    print_results(results,model_name,fw_dir,download)
  end
end


