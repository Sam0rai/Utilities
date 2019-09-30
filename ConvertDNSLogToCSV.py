#!/usr/bin/env python
# -*- coding: utf-8 -*-

__description__ = '''
[!] ConvertDNSLogToCSV.py: A tool to parse DNS Records from a Windows DNS
server\'s debug log (aka: "DNSDebugLog.txt"), and save the results to a 
CSV file.'''
__author__ = 'Sam0rai'
__version__ = '1.0'
__date__ = '2019/09/30'


import optparse
import textwrap
import os, sys, csv
import re
from re import IGNORECASE

def PrintManual():
    manual = '''
Manual:

ConvertDNSLogToCSV is a tool to parse parse DNS Records from a Windows DNS 
server\'s debug log (aka: "DNSDebugLog.txt"), and save the results to a CSV 
file.
The input to the tool is the full path of the DNG debug log file.
If not destination full path is give, the parsed file is saved by default in 
the folder where the tool is located, as "DNSDebugLog_Output.csv". 

[*] Use-case: Parse a DNS debug log file. 
    Usage: ConvertDNSLogToCSV.py -s <full path to file>
    Example:
        ConvertDNSLogToCSV.py -s c:\test\DNSDebugLog.txt
        
[*] Use-case: Parse a DNS debug log file and save it as designated outputfile. 
    Usage: ConvertDNSLogToCSV.py -s <full path to file> -c <output file>
    Example:
        ConvertDNSLogToCSV.py -s c:\test\DNSDebugLog.txt 
        -c c:\results\DNS_results.csv
'''
    for line in manual.split('\n'):
        print(textwrap.fill(line, 78))


def ConvertSingleDNSLogToCSV(sourceFile, outputFile, DNS_regexFilter, verbose=False):
    counter = 0
    try:
        outputFileWriter = open(outputFile, 'w', newline='')
        writer = csv.writer(outputFileWriter)
        DNS_Pattern = re.compile(r"^(([0-9]{1,2}.[0-9]{1,2}.[0-9]{2,4}|[0-9]{2,4}-[0-9]{2}-[0-9]{2})\s*[0-9: ]{7,8}\s*(PM|AM)?) ([0-9A-Z]{3,4} PACKET\s*[0-9A-Za-z]{8,16}) (UDP|TCP) (Snd|Rcv) ([0-9.]{7,15}|[0-9a-f:]{3,50})\s*([0-9a-z]{4}) (.) (.) (\[.*\]) (.*) (\(.*)", re.IGNORECASE)
        with open(sourceFile, 'r') as dnsLogFile:
            while True:
                row = dnsLogFile.readline()
                if(row == ''):
                    break
                
                matchObj = DNS_Pattern.findall(row)
                if matchObj == []:
                    continue
                
                counter += 1
                record = [field.strip() for field in matchObj[0]]
                record[12] = re.sub("\(\d+\)", ".", record[12])
                record[12] = re.sub("^\.", "", record[12])
                record[12] = re.sub("\.$", "", record[12])
                if(DNS_regexFilter):
                    matchObj = DNS_regexFilter.findall(str(record))
                    if matchObj == []:
                        writer.writerow(record)
                else:
                    writer.writerow(record)
                if(verbose):
                    print("{0}) {1}".format(counter, record))
                    
        outputFileWriter.close()
    except Exception as e:
        print("[ERROR] " + str(e))
        sys.exit(1)
    finally:
        return counter
            
       
def ConvertDNSLogToCSV(options):
    sourceFile          = os.path.join(os.getcwd(), "DNSDebugLog.txt")
    outputFile          = os.path.join(os.getcwd(), "DNSDebugLog_Output.csv")
    verbose             = False
    counter             = 0
    DNS_regexFilter     = ''

    if options.filter:
        DNS_regexFilter = re.compile(r"(([0-9.]{7,15}).in-addr.arpa)|(.*_nfsv4idmapdomain)|(.*.ip6\.arpa)|(.*dns.msftncsi.com)|(.*\.digicert.com)|(.*\.verisign.com)|(.*\.googleapis.com)|(.*\.google-analytics.com)", re.IGNORECASE     )
    if options.verbose:
        verbose = True
           
    if options.csv:
        outputFile = options.csv
        
    if options.sourceFile:
        sourceFile = options.sourceFile
        
    try:            
        counter = ConvertSingleDNSLogToCSV(sourceFile, outputFile, DNS_regexFilter, verbose)
        if(counter is None):
            counter = 0
        if(verbose):
            print("[{0}]: Processed a total of {1} records".format(sourceFile, counter))        
    except Exception as e:
        print("[ERROR] " + str(e))
        sys.exit(1)

    
def Main():
    oParser = optparse.OptionParser(usage='\r\n%prog [options] [DNS debug log source file]\n' + __description__, version='%prog ' + __version__)
    oParser.add_option('-m', '--man', action='store_true', default=False, help='Print manual')
    oParser.add_option('-v', '--verbose', action='store_true', default=False, help='Verbose mode: print the parsed records to stdout')
    oParser.add_option('-s', '--sourceFile', type=str, default='', help='Full path of input DNS debug log file')
    oParser.add_option('-f', '--filter', action='store_true', default=False, help='Filter out common DNS records (which can be considered unnecessary \'white noise\')')
    oParser.add_option('-c', '--csv', type=str, default='', help='Full path of output CSV file (comprised of parsed DNS records)')
    (options, args) = oParser.parse_args()

    if options.man:
            oParser.print_help()
            PrintManual()
            return
    
    if len(args) > 0:
        oParser.print_help()
        return
    else:
        try:
            ConvertDNSLogToCSV(options)
        except Exception as e:
            print("[ERROR] " + str(e))
            

if __name__ == '__main__':
    Main()
