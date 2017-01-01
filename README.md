# wlan_switcher
Speedport W724V WLAN_Switcher

            WLAN_SWITCHER für SPEEDPORT W724V

Der Speedport W724V deaktiviert die WLAN-Module nach eingestelltem
Intervall nur wenn zum Schaltzeitpunkt kein Device eingebucht ist.
Dieses Problem wird in den Telekom-Support Foren schon lange
angeprangert, es erfolgt aber leider keine Reaktion:

https://telekomhilft.telekom.de/t5/Telefonie-Internet/Speedport-W-724V-Zeitschaltung-funktioniert-nicht/td-p/339560/page/10

Dieses Skript stellt hierfür eine mögliche Lösung dar!
Ausgeführt in einem cron-job auf zB einem Raspberry-PI kann es
zuverlässig die einzelnen WLAN-Module des W724V aktivieren und
deaktivieren!
Es könnte möglich sein, dass der wlan_switcher auch für andere
Speedport-Modelle funktioniert! Bitte unbedingt um Rückmeldungen!

Bitte unbedingt die IP-Adresse und das Router-Passwort in
der zugehörigen wlan_switcher.conf an die eigenen Werte an-
passen!
Falls die wlan_switcher.conf nicht im Verzeichns exisitiert, wird
sie beim erstmaligen Start des WLAN_Switcher angelegt!

Dieses Skript benötigt python3 und die requests library.
Bitte bei Bedarf nachinstallieren!
 
Einrichtung:

1. Wenn nicht bereits vorhanden: Installation von python3

	`Das Skript wurde mit python3.4.2 getestet und erstellt.`
2. Wenn nicht bereits vorhanden: Installaton von 'requests': http://docs.python-requests.org/en/latest/

	`pip install requests`
3. wlan_switcher.py in ein leeres Verzeichnis kopieren und ausführbar machen:

	`chmod u+x wlan_switcher.py`
	
	Beim erstmaligen Start durch `./wlan_switcher.py` wird im selben Verzeichnis eine `wlan_switcher.conf` erstellt.
4. `wlan_switcher.conf` anpassen!
 
Benutzung:
* Um zB das 2,4GHz Modul zu deaktivieren:

  `./wlan_switcher.py -w 2,4 -s off`
* Zum Überprüfen ob wlan_switcher korrekt funktioniert kann -v mit angegeben werden:

  `./wlan_switcher.py -w 2,4 -s off -v`
* Wenn in der letzten Zeile der Ausgabe folgender Text steht war der Vorgang erfolgreich:

  `Vorgangsstatus: WLAN-Modul: 2,4 GHz, Schaltzustand: off --> ok`
 
Mögliche Kommandozeilenparameter:

`-h / --help`: Gibt eine Hilfe zu den verfügbaren Kommandozeilenparametern an.  
`-w / --wlan`: 2,4 oder 5GHz -- Gibt an welches WLAN-Modul geschaltet werden soll.  
`-s / --switch`: on oder off -- Gibt an ob das mit -w gewählte Modul ein oder ausgeschaltet werden soll.  
`-p / --phonecalls`: Soll die Anrufliste ausgeben.  
`-v / -- verbose`: Aktiviert die detailierte Ausgabe von Statusinformationen und Infos zu Fehlersuche.  
 
