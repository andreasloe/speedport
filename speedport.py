#!/usr/bin/python3
#
#    Speedport W724V - Kommandozeilenprogramm
#    Copyright (C) 2016  Stefan Nuber, veraendert von A. Loeffler 2017
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#     51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
####################################################################
####################################################################
#
#              Kommandozeilenprogramm für SPEEDPORT W724V
#
# Der Speedport W724V deaktiviert die WLAN-Module nach eingestelltem
# Intervall nur wenn zum Schaltzeitpunkt kein Device eingebucht ist.
# Dieses Problem wird in den Telekom-Support Foren schon lange
# angeprangert, es erfolgt aber leider keine Reaktion:
#
# https://telekomhilft.telekom.de/t5/Telefonie-Internet/Speedport-W-724V-Zeitschaltung-funktioniert-nicht/td-p/339560/page/10
#
# Dieses Skript stellt hierfür eine mögliche Lösung dar!
# 
#
#####################################################################
#####################################################################
#
# Bitte unbedingt die IP-Adresse und das Router-Passwort unten 
# an die eigenen Werte anpassen!
#
# Dieses Skript benötigt python3 und die requests library.
# Bitte bei Bedarf nachinstallieren mit:
#
# pip install requests
#
#
#####################################################################
#
#
#
#


import requests
import hashlib
import re
import argparse
import configparser
import sys


# Funktion zum Einlesen der Kommandozeilenparameter:
def read_cmd_params():
    parser = argparse.ArgumentParser(description="Mögliche Optionen:")
    parser.add_argument("-w", "--wlan", dest="freq",
                        choices=["2,4", "5"],
                        required="True",
                        help="Das zu schaltende WLAN-Modul: mögliche Werte sind 2,4 und 5")
    parser.add_argument("-s", "--switch", dest="switch",
                        required="True",
                        choices=["on", "off"],
                        help="Ein oder Ausschalten: mögliche Werte sind 'on' und 'off'")
    parser.add_argument("-p", "--phonecalls", dest="switch",
                        required="True",
                        help="Auslesen der Telefonliste (10 Anrufe)")

    return parser.parse_args()


# formatting and printing single call
def print_call_data(str1, str2):
    # when do we need newlines when printing?
    nwl = (str1 == "takencalls_duration") or (str1 == "dialedcalls_duration") or (str1 == "missedcalls_who")
    # write duration using minutes and seconds
    if (str1 == "takencalls_duration") or (str1 == "dialedcalls_duration"):
         str2_min = int(str2) // 60 
         str2_sec = int(str2) % 60 
         str2 = str(str2_min) + "' " + str(str2_sec) + "''"
    # remove useless entries (do this after newlines and recalculation!)
    clutter = ["takencalls_", "missedcalls_", "dialedcalls_", "date", "time", "who"]
    for s in clutter:
        str1 = re.sub(s, '', str1)
    str1 = re.sub('duration', 'Dauer', str1)
    str1 = re.sub('id', 'Nr', str1)
    # finally print
    if nwl:
         print(str1, str2)
    else:
        print(str1, str2, end=" ")
    return 
    

# printing set of calls
def print_calls(i, str, denom, counter, no):
    if (i["varid"] == str):
        counter += 1
        if (counter == 1):
            print (denom)
        if (counter < no+1):
            for j in i["varvalue"]:
                print_call_data(j["varid"],j["varvalue"])
    return counter


# printing set of devices
def print_devices(i):
    str1 = ""
    if (i["varid"] == "dynrule_addmdevice"):
        for j in i["varvalue"]:
            if (j["varid"] == "mdevice_name"): 
                str1 = str1 + j["varvalue"] + ' = ' # Name des Geraetes
            elif (j["varid"] == "mdevice_mac"): 
                str1 = str1 + j["varvalue"] + ', sid = ' # Mac-Adresse des Geraetes
            elif (j["varid"] == "sid"): 
                str1 = str1 + j["varvalue"] # sid-Adresse (IP) des Geraetes
    
    if (i["varid"] == "addtcpredirect"):
        for j in i["varvalue"]:
            if (j["varid"] == "tcpredirect_id"): 
                str1 = str1 + j["varvalue"] + ' : ' # interne ID der Portumleitung
            elif (j["varid"] == "tcp_device"): 
                str1 = str1 + j["varvalue"]  # sid (IP) des Geraetes
    
    return str1


def main():
    url_router = 'http://speedport.ip'
    passwd_router = 'XXXXX'
    
    # Geraetepasswort gesetzt?
    if (passwd_router == 'XXXXX'):
        print("Bitte das Gerätepasswort passwd_router=XXXXX in speedport.py, Zeile 139, anpassen. Abbruch!")
        sys.exit()
    
    # Parameter einlesen
    param = read_cmd_params()
        
    # Einloggen
    with requests.Session() as s:
        page = s.post(url_router + '/data/Login.json', data={'password': hashlib.md5(bytes(passwd_router, 'utf-8')).hexdigest(), 'showpw': '0', 'httoken': ''})
        httoken = re.findall('_httoken = (\d*);', s.get(url_router + '/html/content/overview/index.html?lang=de').text)[0]
        
        if param.?? == "c":
            # Telefonate holen
            page = s.get(url_router + '/data/PhoneCalls.json', params={"_tn": httoken}, headers={'Referer': url_router + '/html/content/overview/index.html?lang=de'})
            page_decoded = json.loads(page.content.decode('utf-8'))
        
            no_printed_calls = 10 #how many calls shall be printed?
            counter_taken = 0 #three counters
            counter_missed = 0
            counter_dialed = 0
            for i in page_decoded:
                counter_taken = print_calls(i, "addtakencalls", "--angenommen", counter_taken, no_printed_calls)          
                counter_missed = print_calls(i, "adddialedcalls", "--angerufen", counter_missed, no_printed_calls)          
                counter_dialed = print_calls(i, "addmissedcalls", "--verpasst", counter_dialed, no_printed_calls)          

        else param.?? == "f":
            #Internetdaten (Portfreigaben insbesondere)
            page = s.get(url_router + '/data/Portforwarding.json', params={"_tn": httoken}, headers={'Referer': url_router + '/html/content/overview/index.html?lang=de'})
            page_decoded = json.loads(page.content.decode('utf-8'))
            for i in page_decoded:
                str1 = print_devices(i)
                if str1 != "":
                    print(str1)

if __name__ == '__main__':
    main()
    
