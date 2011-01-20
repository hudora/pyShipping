#!/usr/bin/env python
# encoding: utf-8
"""
stat.py - parse Fortras STAT messages.

Created by Maximillian Dornseif on 2006-11-19.
You may consider this BSD licensed.
"""

import re
import datetime
import logging


class Statusmeldung(object):
    """Parses and represents an STAT message."""
    q_record_re = (r'Q(?P<idbeimempfangspartner>.{10})(?P<verkehrsart>.)(?P<sendungsnrversender>.{16})'
                   + r'(?P<sendungsnrempfaenger>.{16})(?P<sendungsschluessel>[0-9 ]{3})(?P<date>[0-9 ]{8})'
                   + r'(?P<time>[0-9 ]{4})(?P<wartezeit>[0-9 ]{3})(?P<quittungsgeber>.{15})(?P<zusatztext>.{49})'
                   + r'(?P<foo>.)5')
    # Satzart ‘Q’ muss 1 001 - 001
    # Identifkations-Nr. des Versandpartners beim Empfangspartner** muss          10 002 - 011
    # Verkehrsart muss 1 012 - 012
    # Sendungs-Nr. Versandpartner muss          16 013 - 028
    # Sendungs-Nr.Empfangspartner muss          16 029 - 044
    # Statusschlüssel* muss 3 045 - 047
    # Datum des Ereignisses
    # (TTMMJJJJ) muss 8/0 048 - 055
    # Uhrzeit des Ereignisses
    # (SSMM) muss 4/0 056 - 059
    # Warte-/Standzeit in Minuten kann 3 060 - 062
    # Name des Quittungsgebers kann          15 063 - 077
    # Zusatztext kann          49 078 - 126
    # Frei 1 127 - 127
    # Releasestand ‘5’ muss 1 128 - 128

    # stati, die dazu fuehren, dass eine  sendung erledigt ist
    erledigtstati = [11,  # Nicht in Zustellung - Sendung endgültig in Verlust
                     12,  # Zugestellt - reine Quittung
                     66,  # Keine Zustellung - Komplett-Fehlmenge per Entladebericht gemeldet
                     67,  # Nicht zugestellt - annahmeverweigerte Sendung, Retour lt. Verfügung
                     68,  # Nicht zugestellt - annahmeverweigerte Sendung, Retour-Verfügung fehlt
                     69,  # Zugestellt - mit Teilfehlmenge
                     70,  # Zugestellt - mit Beschädigung
                     71,  # Zugestellt - Zustellung nicht belegbar/SPÜS verloren
                     74,  # Zugestellt - Teil-AV
                     80,  # AV - Ware beschädigt
                     81,  # AV - Fehlmenge
                     82,  # AV - Liefertermin überschritten
                     83,  # AV - Lieferschein fehlt/Begleitpapiere unvollständig
                     84,  # AV - Empfänger zahlt WWNN/EUSt. nicht
                     85,  # AV - nicht bestellt
                     88,  # Erledigung durch ...
                   ]
    okstati = [12, 50]
    bouncestati = [80, 81, 82, 83, 84, 85]
    errorstati = [66, 67, 68, 69, 70, 71, 74] + bouncestati
    warnstati = [5, 8, 9, 18, 63, 64, 65, 66, 99, 100] + bouncestati
    statustexte = {
         1: 'Nicht in Zustellung - Sendung fehlt komplett lt. EB',
         2: 'Nicht in Zustellung - unvollständige/falsche Sendungsangaben',
         3: 'Nicht in Zustellung – Ware beschädigt',
         4: 'Nicht in Zustellung - Sendung verstapelt/nicht auffindbar',
         5: 'Nicht in Zustellung - Platzmangel auf Zustelltour',
         6: 'Nicht in Zustellung - Fix- oder Zustelltermin lt. Vorgabe',
         7: 'Nicht in Zustellung - Empfänger außerhalb des Produktionsgebietes (24 h)',
         8: 'Nicht zugestellt - Zeitmangel auf Zustelltour',
         9: 'Nicht zugestellt - Empfänger nicht angetroffen.  Zustellbescheid hinterlassen',
        10: 'Nicht zugestellt - annahmeverweigert/unzustellbar  oder Adressfehler',
        11: 'Nicht in Zustellung - Sendung endgültig in Verlust (Protokoll folgt)',
        12: 'Zugestellt - reine Quittung',
        13: 'Nicht in Zustellung - Sendung unvollständig',
        14: 'Nicht in Zustellung - Empfänger ist Selbstabholer',
        15: 'Nicht in Zustellung – Regionaler Feiertag',
        16: 'Nicht in Zustellung - Zollgut',
        17: 'Nicht in Zustellung - Avisvorschrift lt. Beleg/Anweisung/Inkasso',
        18: 'Nicht zugestellt - zu lange Wartezeit beim Empfünger',
        22: 'Nicht in Zustellung - Lieferschein fehlt/Begleitpapiere  unvollstündig',
        31: 'Nicht in Zustellung - Fernverkehr vom VP/HUB  verspätet (E2-Status)',
        40: 'Sendung auf dem Weg zum Empfänger / in Zustellung',
        50: 'Zugestellt - reine Quittung',
        52: 'Sendung zu spät beim Empfangsspediteur angekommen, Auslieferung verspätet sich',
        53: 'Sendung für Zustellung vorgesehen / Nachladesdg',
        54: 'Sendung auf dem Weg zum Empfänger / in Zustellung',
        55: 'Nicht in Zustellung - keine Warenannahme oder Vereinbarung',
        63: 'Nicht zugestellt - keine Warennahme oder Warenannahme geschlossen',
        64: 'Nicht zugestellt - Hebebühne erforderlich',
        65: 'Nicht zugestellt - Empfänger wünscht Avis oder Fixtermin',
        66: 'Keine Zustellung - Komplett-Fehlmenge per Entladebericht gemeldet',
        67: 'Nicht zugestellt - annahmeverweigerte Sendung, Retour lt. Verfügung',
        68: 'Nicht zugestellt - annahmeverweigerte Sendung, Retour-Verfügung fehlt',
        69: 'Zugestellt - mit Teilfehlmenge',
        70: 'Zugestellt - mit Beschädigung',
        71: 'Zugestellt - Zustellung nicht belegbar/SPÜS verloren',
        74: 'Zugestellt - Teil-AV',
        80: 'AV - Ware beschädigt',
        81: 'AV - Fehlmenge',
        82: 'AV - Liefertermin überschritten',
        83: 'AV - Lieferschein fehlt/Begleitpapiere unvollständig',
        84: 'AV - Empfänger zahlt WWNN/EUSt. nicht',
        85: 'AV - nicht bestellt',
        88: 'Erledigung durch ...',
        90: 'Übermittlung des Quittungsgebers, des Zustelldatums und der Ablieferzeit',
        91: 'Zustellbeleg archiviert',
        99: 'Nicht in Zustellung - Ereignis zu Lasten Empfangspartner',
        100: 'Nicht in Zustellung - Ereignis nicht zu Lasten Empfangspartner',
    }

    def update_sendung(self, sendung_id, datadict):
        """Updates a huLOG Sendung record with the parsed STAT data."""
        import huLOG.models
        try:
            sendung = huLOG.models.Sendung.objects.get(id=sendung_id)
        except huLOG.models.Sendung.DoesNotExist:
            logging.warning('Problem locating Sendung with id %r for STAT record - ignoring' % sendung_id)
            return
        if datadict['timestamp'] > datetime.datetime.now():
            logging.warning('Future timestamp for Sendung with id %r: %s' % (sendung_id, datadict['timestamp']))
            return
        if datadict['timestamp'] < sendung.created_at:
            logging.warning('Inconsistent timestamps for Sendung with id %r: %s' % (sendung_id, datadict['timestamp']))
            return
        if int(datadict['sendungsschluessel']) in Statusmeldung.warnstati:
            sendung.needs_attention = True
        if int(datadict['sendungsschluessel']) in Statusmeldung.erledigtstati:
            sendung.delivered_at = datadict['timestamp']
            sendung.status = 'delivered'
        if int(datadict['sendungsschluessel']) in Statusmeldung.errorstati:
            sendung.needs_attention = True
            sendung.status = 'error'
        if int(datadict['sendungsschluessel']) in Statusmeldung.bouncestati:
            sendung.status = 'bounced'
            logging.warning('bounced shipment %r: %r (%r|%r)' % (datadict['sendungsnrversender'],
                                                                       datadict['sendungsschluessel'],
                                                                       datadict['statustext'],
                                                                       datadict['zusatztext']))

        if datadict['statustext']:
            info = [datadict['statustext']]
        else:
            info = ['']
        if datadict['quittungsgeber']:
            info.append('quittiert durch %r' % datadict['quittungsgeber'])
        if datadict['wartezeit']:
            info.append('Wartezeit % min' % int(datadict['wartezeit']))
        if datadict['zusatztext']:
            info.append(datadict['zusatztext'])
        info.append(str(datadict['timestamp']))
        log = huLOG.models.SendungLogentry(lieferung=sendung)
        log.displaytext = repr(', '.join(info))
        log.sourcedata = repr(datadict)
        log.source = 'Maeuler STAT'
        log.code = '200'
        if datadict['sendungsschluessel'] in Statusmeldung.warnstati:
            log.code = '220'
        if datadict['sendungsschluessel'] in Statusmeldung.errorstati:
            log.code = '230'
        log.timestamp = datadict['timestamp']
        log.save()
        sendung.updated_at = datetime.datetime.now()

        # we only save well known stati
        if datadict['sendungsschluessel'] in ['005', '006', '007', '008', '009', '012', '015', '016', '017',
                                              '018', '031', '040', '050', '054', '055', '063', '068', '069',
                                              '071', '084', '085', '091', '099', '053', '100', '999']:
            if datadict['sendungsnrempfaenger']:
                if (sendung.speditionsauftragsnummer
                  and sendung.speditionsauftragsnummer != datadict['sendungsnrempfaenger']):
                    logging.error('Problem with Sendung %r: original speditionsauftragsnummer %r replaced by %r' % (sendung, sendung.speditionsauftragsnummer, datadict['sendungsnrempfaenger']))
                sendung.speditionsauftragsnummer = datadict['sendungsnrempfaenger']
        else:
            logging.error('unknown STAT data for record %r: %r (%r|%r)' % (datadict['sendungsnrversender'],
                                                                           datadict['sendungsschluessel'],
                                                                           datadict['statustext'],
                                                                           datadict['zusatztext']))
        sendung.save()

    def parse(self, data):
        """Parses Fortras STAT data."""
        lines = data.split('\n')
        lines = [x.strip('\r') for x in lines]
        if lines[0] == '' and len(lines) == 1:
            logging.error('empty file')
            return
        if not lines[0].startswith('@@PHSTAT128 0128003500107 MAEULER HUDORA1                       '):
            raise RuntimeError("illegal status data %r" % data[:300])
        for line in lines[1:]:
            if not line or line[0] == 'X':  # 'X' records and empty lines are ignored
                continue
            match = re.search(Statusmeldung.q_record_re, line)
            newdict = {}
            if not match:
                print 'no match', repr(line)
            for key, value in match.groupdict().items():
                newdict[key] = value.strip()
            try:
                if newdict['time']:
                    newdict['timestamp'] = datetime.datetime(int(newdict['date'][4:]), int(newdict['date'][2:4]),
                                                             int(newdict['date'][:2]), int(newdict['time'][:2]),
                                                             int(newdict['time'][2:]))
                else:
                    newdict['timestamp'] = datetime.datetime(int(newdict['date'][4:]), int(newdict['date'][2:4]),
                                                             int(newdict['date'][:2]))
            except ValueError:
                logging.error("malformed timestamp %r|%r" % (newdict['date'], newdict['time']))
                newdict['timestamp'] = datetime.datetime.now()
            newdict['statustext'] = Statusmeldung.statustexte.get(int(newdict['sendungsschluessel']))
            try:
                newdict['sendungsnrversender'] = int(newdict['sendungsnrversender'])
                self.update_sendung(newdict['sendungsnrversender'], newdict)
            except ValueError:
                logging.warning('Problem with invalid id %r for STAT record - ignoring' % newdict['sendungsnrversender'])
