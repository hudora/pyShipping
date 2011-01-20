#!/usr/bin/env python
# encoding: utf-8
"""
entl.py - parse Fortras ENTL messages.

Created by Maximillian Dornseif on 2006-11-19.
You may consider this BSD licensed.
"""

import re
import logging
import datetime


class Entladebericht(object):
    """Parses and represent an ENTL message."""
    m_record_re = (r'M(?P<borderonr>[0-9 ]{18})(?P<borderodatum>[0-9 ]{8})(?P<kundennummer>.{10})'
                   + r'(?P<eingangsdatum>[0-9 ]{8})(?P<eingangszeit>[0-9 ]{4})(?P<zeitschranfenstatus>..)'
                   + r'(?P<entladebeginn_datum>[0-9 ]{8})(?P<entladebeginn_zeit>[0-9 ]{4})'
                   + r'(?P<entladeende_datum>[0-9 ]{8})(?P<entladeende_zeit>[0-9 ]{4})'
                   + r'(?P<entladehinweis>.{30})             (?P<foo>.{9})5')
    m_record_re = re.compile(m_record_re)
    # Satzart ‚ÄòM‚Äô muss 1 001 - 001
    # Bordero-Nr.Versandpartner muss          18 002 - 019
    # Borderodatum Versandpartner (TTMMJJJJ) muss 8/0 020 - 027
    # Kunden-Nr. Empfangspartner beim Versandpartner muss          10 028 - 037
    # Eingangsdatum (TTMMJJJJ) muss 8/0 038 - 045
    # Eingangszeit (SSMM) muss 4/0 046 - 049
    # Zeitschranken-Status* muss 2 050 - 051
    # Entladebeginn-Datum (TTMMJJJJ) muss 8/0 052 - 059
    # Entladebeginn Zeit (SSMM) muss 4/0 060 - 063
    # Entladeende-Datum (TTMMJJJJ) muss 8/0 064 - 071
    # Entladeende-Zeit (SSMM) muss 4/0 072 - 075
    # Nicht sendungsbezogener Entladehinweis-Text kann          30 076 - 105
    # Euro-Paletten-Belastung  Versandpartner aus Bordero kann 3/0 106 - 108
    # Gitterbox-Paletten-  Belastung Versandpartner  aus Bordero kann 3/0 109 - 111
    # Euro-Paletten-Entladung Empfangspartner kann 3/0 112 - 114
    # Gitterbox-Paletten-Entladung Empfangspartner kann 3/0 115 - 117
    # Verkehrsart** kann 1 118 - 118
    # Frei 9 119 - 127
    # Releasestand ‚Äò5‚Äô muss 1 128 - 128

    n_record_re = (r'N(?P<borderonr>[0-9 ]{18})(?P<position>[0-9 ]{3})(?P<sendungsnrversender>[0-9 ]{16})'
                   + r'(?P<sendungsnrempfaenger>[0-9 ]{16})(?P<differenzschluessel1>..)'
                   + r'(?P<differenzzahl1>[0-9 ]{4})(?P<verpackungsart1>..)(?P<differenztext1>.{29})'
                   + r'(?P<differenzschluessel2>..)(?P<differenzzahl2>[0-9 ]{4})(?P<verpackungsart2>..)'
                   + r'(?P<differenztext2>.{29})')
    n_record_re = re.compile(n_record_re)
    # Satzart ‚ÄòN‚Äô muss 1 001 - 001
    # Bordero-Nr. Versandpartner muss          18 002 - 019
    # Laufende Bordero-Position Versandpartner muss 3/0 020 - 022
    # Sendungs-Nr.  Versandpartner muss          16 023 - 038
    # Sendungs-Nr. Empfangspartner muss          16 039 - 054
    # Differenzartschluüssel 1* muss 2 055 - 056
    # Differenzanzahl 1 kann 4/0 057 - 060
    # Verpackungsart 1** kann 2 061 - 062
    # Text/Hinweis 1 kann          29 063 - 091
    # Differenzartschluüssel 2* kann 2 092 - 093
    # Differenzanzahl 2 kann 4/0 094 - 097
    # Verpackungsart 2** kann 2 098 - 099
    # Text/Hinweis 2 kann          29 100 - 128

    # no match 'V461               720-00             00340498430009431112               0                          19092008183100              '
    v_record_re = (r'V(?P<borderonr>[0-9 ]{18})(?P<sendungsnrversender>.{16})(?P<barcodetype>...)'
                   + r'(?P<nve>.{35})(?P<hinweiscode>...)(?P<hinweistext>.{24})'
                   + r'(?P<date>[0-9 ]{8})(?P<time>[0-9 ]{4})'
                   + r'(?P<benutzer>.{10})(?P<terminal>.{4})')
    v_record_re = re.compile(v_record_re)
    # Loüst 'N'-Satz ab bei Einsatz von Barcode
    # Satzart ‚ÄòV‚Äô muss 1 001 - 001
    # Bordero-Nr. Versandpartner muss          18 002 - 019
    # Sendungs-Nr. Versandpartner muss          16 020 - 035
    # Barcode-Qualifier * kann 3 036 - 038
    # Barcode-Nr. muss          35 039 - 073
    # Fehler-/Hinweiscode 1 ** muss 3 074 - 076
    # Frei waühlbarer Text/Hinweis kann          24 077 - 100
    # Ereignisdatum (TTMMJJJJ) muss 8 101 - 108
    # Ereignisuhrzeit (HHMMSS) muss 6 109 - 114
    # Benutzer-ID kann          10 115 - 124
    # Scanner/Terminal-ID kann 4 125 - 128
    # Fehler-/Hinweiscode:
    statustexte = {
        0: 'Packstück',
        2: 'Packstück eingedrückt',
        3: 'Packstück aufgerissen, Ware greifbar',
        4: 'Packstück nass',
        5: 'Packstückinhalt läuft aus',
        9: 'Packstück beschädigt',
       10: 'Euro-Palette',
       11: 'Euro-Palette, Ware beschädigt',
       12: 'Euro-Palette beschädigt',
       13: 'Euro-Palette und Ware beschädigt',
       14: 'Euro-Palette verschweißt/gewickelt',
       15: 'Euro-Palette, Folie ein-/aufgerissen, Ware greifbar',
       19: 'Euro-Palette und/oder Ware mit Beschädigung',
       20: 'Gitterbox',
       21: 'Gitterbox, Ware beschädigt',
       22: 'Gitterbox beschädigt',
       23: 'Gitterbox und Ware beschädigt',
       29: 'Gitterbox und/oder Ware mit Beschädigung',
       30: 'Halbpalette',
       31: 'Halbpalette, Ware beschädigt',
       32: 'Halbpalette beschädigt',
       33: 'Halbpalette und Ware beschädigt',
       34: 'Halbpalette verschweißt/gewickelt',
       35: 'Halbpalette, Folie ein-/aufgerissen, Ware greifbar',
       39: 'Halbpalette und/oder Ware mit Beschädigung',
       40: 'Einwegpalette',
       41: 'Einwegpalette, Ware beschädigt',
       42: 'Einwegpalette beschädigt',
       43: 'Einwegpalette und Ware beschädigt',
       44: 'Einwegpalette verschweißt/gewickelt',
       45: 'Einwegpalette, Folie ein-/aufgerissen, Ware greifbar',
       49: 'Einwegpalette und/oder Ware mit Beschädigung.',
       50: 'Packstück fehlt bei Entladung',  # (Wird durch Entladebericht beim EP erzeugt)
       51: 'Backbox SK1*',
       52: 'Backbox SK2*',
       53: 'Backbox SK3*',
       54: 'Backbox SK4*',
       62: 'HUB/Konsolidierungspunkt - Packstück handverteilt',
       63: 'HUB/Konsolidierungspunkt - Palette mit Übermaß',
       64: 'HUB/Konsolidierungspunkt - Packstuückroutung nicht lesbar (Nachbearbeitung)',
       65: 'HUB/Konsolidierungspunkt - Versender Direktanlieferung - Aufkleber erstellt',
       66: 'HUB/Konsolidierungspunkt - Dienstleistung - Routung durch HUB / Konsolidierungspunkt',
       67: 'HUB/Konsolidierungspunkt - Dienstleistung - Vereinbarte Nachbearbeitung',
       68: 'HUB/Konsolidierungspunkt - Retoure HUB / Konsolidierungspunkt an Versandspediteur',
       69: 'HUB/Konsolidierungspunkt - Ware im HUB / Konsolidierungspunkt stehen geblieben',
       70: 'HUB/Konsolidierungspunkt - Ware im HUB palettiert',
       93: 'Routerfehler',
       94: 'Verladefehler',
       95: 'PLZ-Fehler*',
       96: 'Platzmangel',
       97: 'Zeitmangel',
       98: 'Rückscannung - Packstuück wieder entladen',
       99: 'Korrekturscannung',
       }

    def update_packstueck(self, nve, datadict):
        """Updates a huLOG Packstueck record with the parsed ENTL data."""

        # TODO: decouple this from huLOG
        import huLOG.models
        try:
            packstueck = huLOG.models.Packstueck.objects.get(_trackingnummer=nve)
        except huLOG.models.Packstueck.DoesNotExist:
            logging.warning('Problem locating Packstueck with barcode %r for ENTL record - ignoring' % nve)
            return
        info = []
        if datadict['terminal']:
            info.append('an Terminal %r' % datadict['terminal'])
        if datadict['benutzer']:
            info.append('gescannt durch Nutzer %r' % datadict['benutzer'])
        if datadict['hinweiscode'] in ['0', '']:
            info.insert(0, 'Bei der Spedition entladen')
            if datadict['hinweistext']:
                info.insert(1, datadict['hinweistext'])
            if datadict['timestamp']:
                info.append(str(datadict['timestamp']))
            log = huLOG.models.PackstueckLogentry(packstueck=packstueck)
            log.displaytext = ', '.join(info)
            log.sourcedata = repr(datadict)
            log.source = 'Maeuler ENTL'
            log.code = '200'
            log.timestamp = datadict['timestamp']
            log.save()
        elif datadict['hinweiscode'] in ['50']:
            info.insert(0, 'Fehlte bei der Entladung')
            log = huLOG.models.PackstueckLogentry(packstueck=packstueck)
            log.displaytext = ', '.join(info)
            log.sourcedata = repr(datadict)
            log.source = 'Maeuler ENTL'
            log.code = '500'
            log.timestamp = datadict['timestamp']
            log.save()
        else:
            logging.error('unknown ENTL data: %r (%r)' % (datadict['hinweiscode'],
                                                          datadict['hinweistext']))

    def parse(self, data):
        """Parses Fortras ENTL data."""
        lines = data.split('\n')
        if not lines[0].startswith('@@PHENTL128 0128003500107 MAEULER HUDORA1                       '):
            raise RuntimeError("illegal status data %r" % data[:300])
        for line in lines[1:]:
            line = line.strip('\r')
            if not line:
                continue
            if line[0] == 'M':
                match = re.search(Entladebericht.m_record_re, line)
                if not match:
                    print 'no match', repr(line)
                # the content of M records are ignored
            elif line[0] == 'N':
                match = re.search(Entladebericht.n_record_re, line)
                if not match:
                    print 'no match', repr(line)
                # the content of N records are ignored
            elif line[0] == 'V':
                match = re.search(Entladebericht.v_record_re, line)
                newdict = {}
                if not match:
                    print 'no match', repr(line)
                for key, value in match.groupdict().items():
                    newdict[key] = value.strip()
                newdict['timestamp'] = datetime.datetime(int(newdict['date'][4:]), int(newdict['date'][2:4]),
                                                         int(newdict['date'][:2]), int(newdict['time'][:2]),
                                                         int(newdict['time'][2:]))
                newdict['sendungsnrversender'] = newdict['sendungsnrversender']
                self.update_packstueck(newdict['nve'], newdict)

            elif line[0] == 'W':
                pass  # we happyly ignore W records
            else:
                print "unknown %r" % line
