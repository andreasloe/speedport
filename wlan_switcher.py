#!/usr/bin/python3
#
#    Speedport W724V - WLAN SWITCHER
#    Copyright (C) 2016  Stefan Nuber
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
#              WLAN-SWITCHER fuer SPEEDPORT W724V
#
# Der Speedport W724V deaktiviert die WLAN-Module nach eingestelltem
# Intervall nur wenn zum Schaltzeitpunkt kein Device eingebucht ist.
# Dieses Problem wird in den Telekom-Support Foren schon lange
# angeprangert, es erfolgt aber leider keine Reaktion:
#
# https://telekomhilft.telekom.de/t5/Telefonie-Internet/Speedport-W-724V-Zeitschaltung-funktioniert-nicht/td-p/339560/page/10
#
# Dieses Skript stellt hierfuer eine moegliche Loesung dar!
# Ausgefuehrt in einem cron-job auf zB einem Raspberry-PI kann es
# zuverlaessig die einzelnen WLAN-Module des W724V aktivieren und
# deaktivieren!
# Es koennte moeglich sein, dass der wlan_switcher auch fuer andere
# Speedport-Modelle funktioniert! Bitte unbedingt um Rueckmeldungen!
#
#####################################################################
#####################################################################
#
# Bitte unbedingt die IP-Adresse und das Router-Passwort in
# der zugehoerigen wlan.conf an die eigenen Werte an-
# passen!
# Falls die wlan.conf nicht im Verzeichns exisitiert, wird
# sie beim erstmaligen Start des WLAN_Switcher angelegt!
#
# Dieses Skript benoetigt python3 und die requests library.
# Bitte bei Bedarf nachinstallieren mit:
#
# pip install requests
#
#
#####################################################################
#
# Version 1.1 (andreasloeffler): Auslesen der Anrufliste mit python; funktioniert aber noch nicht
#
#


import requests
import hashlib
import re
import argparse
import configparser
import sys
import time


# Funkton zum Einlesen der Kommandozeilenparameter:
def read_cmd_params():
    parser = argparse.ArgumentParser(description="Moegliche Optionen:")
    parser.add_argument("-w", "--wlan", dest="freq",
                        choices=["2,4", "5"],
                        help="Das zu schaltende WLAN-Modul: moegliche Werte sind 2,4 und 5")
    parser.add_argument("-s", "--switch", dest="switch",
                        choices=["on", "off"],
                        help="Ein oder Ausschalten: moegliche Werte sind 'on' und 'off'")
    parser.add_argument("-p", "--phonecalls", dest="phone",
                        action="store_true",
                        help="Anrufe ausgeben")
    parser.add_argument("-v", "--verbose",
                        action="store_true",
                        help="Schreibe Statusmeldungen to stdout")

    return parser.parse_args()



# Funktion um wlan.conf mit default Werten zu erstellen:
def write_config_file():
    config_header = "####################################################################\n" \
                    "####################################################################\n" \
                    "#\n" \
                    "#              WLAN_SWITCHER fuer SPEEDPORT W724V\n" \
                    "#\n" \
                    "# Konfigurationsdatei fuer wlan_switcher.py\n" \
                    "#\n" \
                    "#####################################################################\n" \
                    "#####################################################################\n" \
                    "#\n" \
                    "# Bitte unbedingt die IP-Adresse des Speedports (router_ip) und das\n" \
                    "# Router-Passwort (router_pw) an die eigenen Werte anpassen!\n" \
                    "# Anschliessend 'Routerdaten wurden angepasst:' auf 'true' setzen!\n" \
                    "#\n" \
                    "#####################################################################\n" \
                    "#\n" \
                    "# Stefan Nuber, 03.01.2016, GNU GPL\n" \
                    "#\n" \
                    "#\n"

    config = configparser.ConfigParser()
    config['Routerdaten'] = {'router_ip': '192.168.2.1',
                             'router_pw': '',
                             'Routerdaten wurden angepasst': 'false'}

    with open('wlan.conf', 'w') as configfile:
        print(config_header, file=configfile)
        config.write(configfile)


# Funktion um die ben\"{o}tigten Werte aus wlan.conf auszulesen:
def read_config_file():
    config = configparser.ConfigParser()
    config.read('wlan.conf')
    routerdaten = config['Routerdaten']
    if routerdaten['Routerdaten wurden angepasst'] != 'true':
        print('Die wlan.conf wurde nicht angepasst! Abbruch!')
        sys.exit()
    return routerdaten


# Erzeuge die benoetigten URLs:
def generiere_urls(router_ip):
    url_router = 'http://' + router_ip
    url_login = url_router + '/data/Login.json'
    url_main = url_router + '/html/content/overview/index.html?lang=de'
    url_modules_json = url_router + '/data/Modules.json'
    url_portforwarding_json = url_router + '/data/Portforwarding.json'
    url_Phonecalls_json = url_router + '/data/PhoneCalls.json'
    url_modules_json_headers = {'Referer': url_router + '/html/content/overview/index.html?lang=de'}
    return url_router, url_login, url_main, url_modules_json, url_portforwarding_json, url_Phonecalls_json, url_modules_json_headers


# Generiere md5 Hash fuer password
def pass_hash(pw):
    return hashlib.md5(bytes(pw, 'utf-8')).hexdigest()


# Extrahiere den Wert von _httoken aus der Website
def get_httoken(page_object):
    regex = re.compile('_httoken = (\d*);')
    return re.findall(regex, page_object.text)[0]


#  Schalter fuer WLAN ein/aus fuer jeweils 2,4 und 5 GHz:
def wlan(ghz, status, httoken):
    if ghz == '5':
        freq_modul = 'use_wlan_5ghz'
    else:
        freq_modul = 'use_wlan'

    if status == 'off':
        schalter = 0
    else:
        schalter = 1

    return {freq_modul: schalter, 'httoken': httoken}


#  Anrufliste abfragen
def phonecalls(httoken):
    zeit = int(time.time()) # ist doch so, dass nur der ganzzahlige Teil verwendet wird?
    return {'_time': zeit, '_tn': httoken}


# Troubleshootingfunktion zur Ausgabe der Requests, Header, usw..
def printrequestandcontent(page):
    print("page.request.url und header: ", page.request.url, page.request.headers)
    print("page.content: ", page.content)


# Funktion zum requesten von 'url' innerhalb von 'session'
def pagerequest(url, session):
    page = session.get(url)
    httoken = get_httoken(page)
    # print('Der httoken ist: ', httoken)
    return httoken, session


# Hauptfunktion
def main():
    # Pruefe ob wlan.conf existiert:
    try:
        with open('wlan.conf') as file:
            pass
    except IOError as e:
        print("wlan.conf existiert nicht. Erstelle neu!\n"
              "Bitte wlan.conf editieren und entsprechend anpassen!")
        write_config_file()
        sys.exit()

    # Lese cmd_params ein:
    param = read_cmd_params()
    if param.verbose is True:
        print('freq=', param.freq, ', switch=', param.switch, ', phone=', param.phone, ', verbose=', param.verbose)

    # Starte neue http-Session:
    with requests.Session() as s:
        routerdaten = read_config_file()
        router_urls = generiere_urls(routerdaten['router_ip'])
        if param.verbose is True:
            print('URLS:', router_urls)
        httoken, s = pagerequest(router_urls[0], s)

        page = s.post(router_urls[1],
                      data={'password': pass_hash(routerdaten['router_pw']), 'showpw': '0', 'httoken': httoken})
        if param.verbose is True:
            printrequestandcontent(page)
            print('Loginvorgang:', page.json()[1]["varvalue"])

        httoken, s = pagerequest(router_urls[2], s)

        if param.switch != None:
            page = s.post(router_urls[3], data=wlan(param.freq, param.switch, httoken), headers=router_urls[4])
            if param.verbose is True:
                print('Vorgangsstatus: WLAN-Modul:', param.freq, 'GHz, Schaltzustand:', param.switch, '-->',
                      page.json()[0]["varvalue"])

        if param.phone is True:
            page = s.get(router_urls[5], data=phonecalls(httoken), headers=router_urls[6])
            print("page.request.response ist aergerlichweise anscheinend leer: ", page.request.response)
            if param.verbose is True:
                print('Vorgangsstatus: Anrufe-Modul')

if __name__ == '__main__':
    main()
