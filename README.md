# Speedport Kommandozeilenprogramm
Speedport W724V Kommandozeilenprogramm

            Kommandozeilenprogramm für SPEEDPORT W724V

Der Speedport W724V ist ein vielgenutzter Router der Telekom, der (im
Gegensatz zur Fritz!Box) fast überhaupt nicht mit der Kommandozeile 
bedienbar ist. Beispielsweise deaktiviert er die WLAN-Module nach eingestelltem
Intervall nur, wenn zum Schaltzeitpunkt kein Device eingebucht ist.
Dieses Problem wird in den Telekom-Support Foren schon lange
angeprangert, es erfolgt aber leider keine Reaktion:

https://telekomhilft.telekom.de/t5/Telefonie-Internet/Speedport-W-724V-Zeitschaltung-funktioniert-nicht/td-p/339560/page/10

Ebenso wenig ist es möglich, kommandozeilenbasiert die Anrufliste auszulesen 
oder die Einstellungen bezüglich Portforwarding auszulesen oder einzustellen.
Dieses Skript stellt hierfür eine mögliche Lösung dar.

Dieses Skript benötigt python3 und die requests library.
Bitte bei Bedarf nachinstallieren!
 
Einrichtung:

1. Wenn nicht bereits vorhanden: Installation von python3

	`Das Skript wurde mit python3.4.2 getestet und erstellt.`
2. Wenn nicht bereits vorhanden: Installation von 'requests': http://docs.python-requests.org/en/latest/

	`pip install requests`
3. speedport.py in ein leeres Verzeichnis kopieren und ausführbar machen:

	`chmod u+x speedport.py`
	
	Vor dem Start von `./speedport.py` das Gerätepasswort anpassen.
 
Benutzung:
* Um zB das 2,4GHz Modul zu deaktivieren:

  `./speedport.py -w 2,4 -s off`

  `./speedport.py -w 2,4 -s off -v`
* Wenn in der letzten Zeile der Ausgabe folgender Text steht war der Vorgang erfolgreich:

  `Vorgangsstatus: WLAN-Modul: 2,4 GHz, Schaltzustand: off --> ok`
 
Mögliche Kommandozeilenparameter:

`-h / --help`: Gibt eine Hilfe zu den verfügbaren Kommandozeilenparametern an.  
`-w / --wlan`: 2,4 oder 5GHz -- Gibt an welches WLAN-Modul geschaltet werden soll.  
`-s / --switch`: on oder off -- Gibt an ob das mit -w gewählte Modul ein oder ausgeschaltet werden soll.  
`-p / --phonecalls`: Gibt die Anrufliste aus.  
`-f / --portforwarding`: Gibt Informationen zum Portforwarding aus.  
 
