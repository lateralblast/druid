#!/usr/bin/env ruby -W:no-deprecated

# Name:         druid (Dell Retrieve Update Information and options['download'])
# Version:      0.1.1
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

gem_list = [ "rubygems", "nokogiri", "open-uri", "getopt/std", "fileutils", "selenium-webdriver", "mechanize", "getopt/long" ]

# Try to load gems

gem_list.each do |load_name|
  case load_name
  when "getopt/long"
    install_name = "getopt"
  else
    install_name = load_name
  end
  begin
    require "#{load_name}"
  rescue LoadError
    install_gem(load_name, install_name)
  end
end

def_dir = Dir.pwd+"/firmware"
options = {}
results = {}

def print_results(options,results)
  options['fwdir'] = options['fwdir']+"/"+options['model']
  if !File.directory?(options['fwdir']) and options['download'] == "y"
    Dir.mkdir(options['fwdir'])
  end
  results.each do |name, url|
    puts
    puts name
    puts url
    if options['download'] == true
      puts
      file = File.basename(url)
      file = options['fwdir']+"/"+file
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

def get_firmware_info(options,results)
  opt = Selenium::WebDriver::Firefox::Options.new
  opt.add_argument('--headless')
  driver = Selenium::WebDriver.for :firefox, :options => opt
  driver.get(options['modelurl'])
  sleep(5)
  if options['all'] == true
    driver.find_element(id: "_evidon-accept-button").click
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
              if column.to_s.match(/download/)
                link = column.to_s.split(/href="/)[1].split(/" class="/)[0]
              end
            else
              if column.to_s.match(/dl-desk-view/)
                name = column.to_s.split(/dl-desk-view">/)[1].split(/<span/)[0]
                name = name.gsub(/\s+$/,"")
                name = name.gsub(/\.$/,"")
              else
                if !name.match(/#{column.text}/)
                  name = name+", "+column.text
                end
              end
            end
          end
          if name.match(/[a-z]/)
            name = name.gsub(/\s+/," ")
            if options['type'].match(/list/) or name.downcase.match(/#{options['type'].downcase}/)
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
    options['model'] = node[:id]
    if options['model'].match(/poweredge/)
      options['model'] = options['model'].split("-")[1]
      models.push(options['model'])
    end
  end
  return models
end

def print_document_urls(options)
  owners_url = options['baseurl']+options['model']+"_owner%27s%20manual_en-us.pdf"
  setup_url  = options['baseurl']+options['model']+"_setup%20guide_en-us.pdf"
  options['fwdir'] = options['fwdir']+"/"+options['model']
  if !File.directory?(options['fwdir']) and options['download'] == true
    Dir.mkdir(options['fwdir'])
  end
  puts options['hwupcase']+" "+options['model'].upcase+":"
  puts owners_url
  puts setup_url
  if options['download'] == true
    [ owners_url, setup_url ].each do |url|
      file = File.basename(url)
      file = options['fwdir']+"/"+file
      if !File.exist?(file)
        puts "Downloading "+url+" to "+file
        %x[wget "#{url}" -O #{file}]
      end
      if file.match(/owner/)
        if !File.size?(file)
          options['hwtype'] = options['hwupcase'].downcase
          url = "http://topics-cdn.dell.com/pdf/"+options['hwtype']+"-"+options['model']+"_Owner's%20Manual_en-us.pdf"
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

# Handle output

def handle_output(options,text)
  if options['output'].to_s.match(/html/)
    if text == ""
      text = "<br>"
    end
  end
  if options['output'].to_s.match(/text/)
    puts text
  end
  return options
end

# Get valid switches and put in an array

def get_valid_options()
  file_array  = IO.readlines $0
  option_list = file_array.grep(/\['--/)
  return option_list
end

# Print script usage information

def print_help(options)
  switches     = []
  long_switch  = ""
  short_switch = ""
  help_info    = ""
  handle_output(options,"")
  handle_output(options,"Usage: #{options['script']}")
  handle_output(options,"")
  option_list = get_valid_options()
  option_list.each do |line|
    if not line.match(/file_array/)
      help_info    = line.split(/# /)[1]
      switches     = line.split(/,/)
      long_switch  = switches[0].gsub(/\[/,"").gsub(/\s+/,"")
      short_switch = switches[1].gsub(/\s+/,"")
      if short_switch.match(/REQ|BOOL/)
        short_switch = ""
      end
      if long_switch.gsub(/\s+/,"").length < 7
        handle_output(options,"#{long_switch},\t\t\t#{short_switch}\t#{help_info}")
      else
        if long_switch.gsub(/\s+/,"").length < 15
          handle_output(options,"#{long_switch},\t\t#{short_switch}\t#{help_info}")
        else
          handle_output(options,"#{long_switch},\t#{short_switch}\t#{help_info}")
        end
      end
    end
  end
  handle_output(options,"")
  return
end

include Getopt

begin
  options = Long.getopts(
    ['--model', REQUIRED],      # Model e.g. M610, R720, etc
    ['--platform', REQUIRED],   # Platform e.g. PowerEdge, PowerVault, etc (defaults to PowerEdge)
    ['--type', REQUIRED],       # Type e.g. BIOS (defaults to listing all)
    ['--search', REQUIRED],     # Search for a term
    ['--fwdir', REQUIRED],      # Set a directory to download to
    ['--output', REQUIRED],     # Output type, e.g. Text, HTML (defaults to Text)
    ['--version', BOOLEAN],     # Print version information
    ['--help', BOOLEAN],        # Print help information
    ['--download', BOOLEAN],    # Download file 
    ['--all', BOOLEAN]          # Return all versions (by default only latest are returned)
  )
rescue
  options['output'] = "text"
  print_help(options)
  exit
end

if !options['output']
  options['output'] = "text"
end

if options['help'] == true
  print_help(options)
end

if !options['fwdir']
  options['fwdir'] = def_dir
end

if !options['platform']
  options['hwtype']   = "poweredge"
  options['hwupcase'] = "PowerEdge"
else
  options['hwtype'] = options['platform'].downcase
  case options['hwtype']
  when /vault/
    options['hwupcase'] = "PowerVault"
  when /compellent/
    options['hwupcase'] = options['hwtype'].capitalize
  else
    options['hwupcase'] = "PowerEdge"
  end
end
top_url  = "http://www.dell.com/support/troubleshooting/us/en/19/ProductSelector/Select/FamilySelection?CategoryPath=all-products%2Fesuprt_ser_stor_net%2Fesuprt_"+options['hwtype']+"&Family="+options['hwupcase']+"&DisplayCrumbs=Product%2BType%40%2CServers%252c%2BStorage%2Band%2BNetworking%40%2C"+options['hwupcase']+"&rquery=na&sokey=solink"
if options['model']
  options['baseurl'] = "http://www.dell.com/support/drivers/us/en/19/Product/"+options['hwtype']+"-"
else
  options['baseurl'] = "ftp://ftp.dell.com/Manuals/all-products/esuprt_ser_stor_net/esuprt_"+options['hwtype']+"/"+options['hwtype']+"-"
end

if options['version'] == true
  print_version(options)
end

if !options['type']
  options['type'] = "list"
end

if options['download'] == true
  if !File.directory?(options['fwdir'])
    Dir.mkdir(options['fwdir'])
  end
  if options['model']
    model_dir = options['fwdir']+"/"+options['model']
    if !File.directory?(model_dir)
      Dir.mkdir(model_dir)
    end
  end
end

if options['type'].to_s.match(/manual|pdf/)
  puts
  if options['model'].match(/all/)
    models = get_model_list(top_url)
    models.each do |model_name|
      options['model'] = model_name
      print_document_urls(options)
    end
  else
    print_document_urls(options)
  end
  exit
end

if options['model']
  if options['model'].match(/all/)
    models = get_model_list(top_url)
    models.each do |mode_name|
      options['model']    = model_name
      options['modelurl'] = "https://www.dell.com/support/home/en-au/product-support/product/"+options['hwtype']+"-"+options['model']+"/drivers"
      if options['type'] == "list"
        if options['model'].length < 5
          puts options['hwupcase']+" "+options['model'].upcase+":\t\t"+options['modelurl']
        else
          puts options['hwupcase']+" "+options['model'].upcase+":\t"+options['modelurl']
        end
      else
        results = get_firmware_info(options,results)
        print_results(options,results)
      end
    end
  else
    options['model']    = options['model'].downcase
    options['modelurl'] = "https://www.dell.com/support/home/en-au/product-support/product/"+options['hwtype']+"-"+options['model']+"/drivers"
    results = get_firmware_info(options,results)
    print_results(options,results)
  end
end


