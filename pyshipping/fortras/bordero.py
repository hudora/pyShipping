#!/usr/bin/env python
# encoding: utf-8
"""
bordero.py - implements BORD messages. BORD is similar to IFTMIN in EDIFACT. Think of it as an work order
to a freight forwarder.

This implementation is specific for usage between HUDORA GmbH and Mäuler but could be used as the basis for a
more generic implementation.

Created by Lars Ronge and Maximillian Dornseif on 2006-11-06.
You may consider this BSD licensed.
"""

import os
import time


#def _transcode(data):
#    """Decode utf-8 to latin1 (which is used by fortras)."""
#    return data.decode('utf-8', 'replace').encode('latin-1', 'replace')


def _clip(length, data):
    """Clip a string to a maximum length."""
    # I wonder if this can't be done with clever formatstring usage.
    if not isinstance(data, str):
        data = data.decode('latin-1')
    if len(data) > length:
        return data[:length]
    return data

# zwei führende Nullen weg !!!
# übertragung: "übergepackt"
# übertragung: Palettenformat 1.5, 1, 0.5
# überticragung: lieferfenster
# DFü: Teil- Und Komplettladungen - verkehrsartschluessel : statt L (LKW) ein X (komplettladung)
# Mäuler Telefonummer
# Liste Auslandssendungen

#doctext = """Bordero-Kopf-Satz"""
#Afelder = [
#    dict(length=18, startpos=0,   endpos=19, name='borderonr',       fieldclass=IntegerFieldZeropadded),
#    dict(length=8,  startpos=19,  endpos=27, name='datum',           fieldclass=DateFieldReverse,
#         default=datetime.date.today()),
#    dict(length=1,  startpos=27,  endpos=28,  name='versandweg',     fieldclass=RightAdjustedField,
#         default='L', choices=('L', 'X')),
#    dict(length=2,  startpos=28,  endpos=30,  name='fahrzeugnummer', fieldclass=IntegerFieldZeropadded),
#    dict(length=10, startpos=34,  endpos=44,  name='versenderid',    fieldclass=RightAdjustedField,
#          default='L515'),
#    dict(length=13, startpos=44,  endpos=57,  name='frachtfuehrer',  fieldclass=RightAdjustedField,
#          default='Maeuler'),
#    dict(length=9,  startpos=53,  endpos=63,  name='plz',            fieldclass=RightAdjustedField,
#          default='42897'),
#    dict(length=12, startpos=63,  endpos=76,  name='ort',            fieldclass=RightAdjustedField,
#          default='Remscheid'),
#    dict(length=15, startpos=76,  endpos=91,  name='ladeeinheit1',   fieldclass=RightAdjustedField),
#    dict(length=15, startpos=91,  endpos=106, name='ladeeinheit1',   fieldclass=RightAdjustedField),
#    dict(length=10, startpos=106, endpos=117, name='plombe1',        fieldclass=RightAdjustedField),
#    dict(length=10, startpos=117, endpos=127, name='plombe1',        fieldclass=RightAdjustedField),
#    dict(length=10, startpos=117, endpos=127, name='release',        fieldclass=FixedField, default='6'),
#]
# Verkehrsartschlüssel (Satzart ‘A’, Position 031)
# B = Bahn
# E = Bordero für den eigenen Nahverkehr
# H = VP an ZKP
# K = Kombi
# L = LKW
# P = Packmittel-Clearing
# W = Weiterleitungsbordero
# X = Teilladungs-/Ladungspartie
# Y = Bordero ZKP an EB ohne Weiterverladung
# Z = ZKP an EP
# C = Codis
# N = Night Star Express
# S = SystemPlus international
# T = Teppichkurier


#doctext="""Versender-Adress-Satz - Teil 1"""
#Bfelder = [
#    dict(length=35, startpos= 0 , endpos= 35, name='versender_name1', default='HUDORA GmbH'),
#    dict(length=35, startpos= 35, endpos= 70, name='versender_name2'),
#    dict(length=35, startpos= 70, endpos=105, name='versender_strasse', default='Jägerwald 13'),
#    dict(length= 3, startpos=105, endpos=107, name='versender_land', default='DE'),
#    dict(length= 9, startpos=107, endpos=116, name='versender_plz', default='42897'),
#    dict(length= 3, startpos=116, endpos=119, name='frei', fieldclass=FixedField, default='   '),
#    dict(length= 3, startpos=119, endpos=122, name='codis_abholstelle', fieldclass=FixedField, default='   '),
#    dict(length= 1, startpos=122, endpos=123, name='codis_laufkennzeichen',
#         fieldclass=FixedField, default=' '),
#]
#
#doctext="""Versender-Adress-Satz - Teil 2"""
#Cfelder = [
#    dict(length=35, startpos=  0, endpos= 35, name='versenderort'),
#    dict(length= 3, startpos= 35, endpos= 38, name='versender_berechnungsland', fieldclass=FixedField,
#         default='   '),
#    dict(length= 9, startpos= 38, endpos= 48, name='versender_berechnugnsplz', fieldclass=FixedField,
#         default='         '),
#    dict(length=35, startpos= 48, endpos= 83, name='versender_berechnungsort', fieldclass=FixedField,
#         default='                                   '),
#    dict(length=17, startpos= 83, endpos=100, name='versender_kundennummer', fieldclass=RightAdjustedField,
#         default='11515'),
#    dict(length= 9, startpos=100, endpos=109, name='warenwert', fieldclass=DecimalFieldWithoutDot, precision=2),
#    dict(length= 3, startpos=109, endpos=112, name='waehrung', default='EUR'),
#    dict(length=13, startpos=112, endpos=123, name='frei', fieldclass=FixedField, default='             '),
#]
#
#doctext = """Empfänger-Adress-Satz  - Teil 1"""
#Dfelder = [
#    dict(length=35, startpos=  0, endpos= 35, name='name1'),
#    dict(length=35, startpos= 35, endpos= 70, name='name2'),
#    dict(length=35, startpos= 70, endpos=105, name='stadtteil'),
#    dict(length=19, startpos=105, endpos=123, name='frei'),
#]
#
#doctext = """Empfänger-Adress-Satz - Teil 2"""
#Efelder = [
#    dict(length=25, startpos=  0, endpos= 35, name='strasse'),
#    dict(length= 3, startpos= 35, endpos= 38, name='land'),
#    dict(length= 9, startpos= 38, endpos= 47, name='plz'),
#    dict(length=35, startpos= 47, endpos= 81, name='Empfängerort muss'),
#    dict(length= 3, startpos= 81, endpos= 84, name='Zustellbezirk Empfänger'),
#    dict(length=10, startpos= 84, endpos= 94, name='Matchcode Empfänger- Nachname'),
#    dict(length=17, startpos= 94, endpos=111, name='Kunden-Nr. Empfänger'),
#    dict(length=10, startpos=111, endpos=121, name='Original-ID des VP beim  Empfangspartner*'),
#    dict(length= 2, startpos=123, endpos=123, name='Frei'),
#]
#
#dictext="""Sendungs-Positions-Satz (je Sendungsteil; mehrfach möglich)."""
#Ffelder = [
#    dict(kength= 4, startpos=  0, endpos=  4, name='packstueck_anzahl'),
#    dict(kength= 2, startpos=  4, endpos=  6, name='verpackungsart'), # ???
#    dict(kength= 4, startpos=  6, endpos= 10, name='packstueck_anzahl_auf_paletten', fieldclass=FixedField,
#         default='    '),
#    dict(kength= 2, startpos= 10, endpos= 12, name='verpackungsart_auf_paletten', fieldclass=FixedField,
#         default='  '),
#    dict(kength=20, startpos= 10, endpos= 30, name='wareninhalt'),
#    dict(kength=20, startpos= 30, endpos= 50, name='zeichen',
#         doc="Zeichen der Sendung beim Versender"),
#    dict(kength= 5, startpos= 50, endpos= 55, name='gewicht', fieldclass=IntegerField,
#         doc="Bruttogewicht in KG."),
#    dict(kength= 5, startpos= 55, endpos= 60, name='gewicht_frachtpflichtig', fieldclass=IntegerField,
#         doc="In der Regel max(gewicht, N), wobei N=150 oder 200"),
#    # Die Satzart ‘F’ darf nicht mit einem 2. Sendungsteil versehen werden,
#    # wenn die Satzarten ‘G’ bzw. ‚Y‘ und ‚Z‘ (Gefahrgut) oder Satzart ‘H’ (Packstück-Nr.) folgen!
#    dict(kength=68, startpos=  60, endpos=123, name='frei'),
#]
# Verpackungsartschlüssel (Satzart ‘F’, Positionen 009/010, 015/016, 071/072 und 077/078)
# Schlüssel Art
# AB Auf Bohlen
# AD AD-Bahnbehälter
# BD BD-Bahnbehälter
# BE Beutel
# BL Ballen
# BU Bund
# CC Collico
# CO SystemPlus Collo
# CD CD-Bahnbehälter
# CP Chep-Palette
# DO Dose
# DR Drum
# EI Eimer
# EB Einweg-Behälter
# EP Einweg-Palette
# FA Fass
# FK Faltkiste
# FL Flasche
# FP DB Euro-Flachpalette
# GE Gebinde
# GP Gitterboxpalette
# GS Gestell
# HC Haus-Haus-Corlette
# HO Hobbock
# HP Halbpalette
# KA Kanne
# KB Kundeneigener Sonderbehälter
# KF Korbflasche
# KI Kiste
# KN Kanister
# KO Korb
# KP Kundeneigene Sonderpalette
# KS Kasten
# KT Karton
# PA Paket
# PK Pack
# RC Rollcontainer
# RG Ring
# RO Rolle
# SA Sack
# SB Spediteureigener Behälter
# ST Stück
# TC Tankcontainer
# TR Trommel
# UV Unverpackt
# VG Verschlag

# 'H':  '002%(barcode)-35s%(foo)35s%(foo)35s%(foo)16s',
# doctext = """Packstück-Nummern-Satz (je Packstück-Nr./Gruppe; mehrfach möglich)"""
#
# BARCODETYP_CHOICES = { 1: 'Freie, unformatierte Markierung',
#                        2: 'Nummer der Versandeinheit (EAN 128)',
#                        3: 'Nummer der Versandeinheit (EAN 128) FORTRAS',
#                        4: 'Paket-Nummer DPD (2/5 Interleaved)',
#                        5: 'Router Label-Nummer DPD (2/5 Interleaved)',
#                        6: 'Packstück-Nummer SystemPlus (2/5 Interleaved)',
#                        7: 'Router Label-Nummer SystemPlus (2/5 Interleaved)',
#                        8: 'IDS-Barcode (2/5 Interleaved)',
#                        9: 'IDS-Barcode (39)',
#                       10: 'IDS-Barcode (128)',
#                       11: 'Nummer der Versandeinheit (Philips)',
#                       12: 'Wechselbehälter-Barcode (2/5 Interleaved)',
#                       13: 'DPD Container-Nummer (2/5 Interleaved)',
#                       }
# Hfelder = [
#     dict(length= 3, startpos=  0, endpos=  3, name='barcodeart', fieldclass=IntegerFieldZerotagged,
#          choices=BARCODETYP_CHOICES),
#     dict(length=35, startpos=  3, endpos= 38, name='barcode1'),
#     dict(length=35, startpos= 38, endpos= 73, name='barcode2'),
#     dict(length=35, startpos= 73, endpos=108, name='barcode3'),
#     dict(length=16, startpos=108, endpos=123, name='frei'),
# ]
#
# # 'I': ('%(sendungsnummer)-16s%(sendungskilo)05d0000000000%(ladedm)03d    %(frankatur)-2s%(frankatur)-2s  %(foo)30s  %(foo)30s%(foo)16s  '),
# doctext = """Sendungs-Gewichte (je Sendung 1x)"""
#
# # Frankaturschlüssel des Spediteur-Übergabescheins (Satzart ‘I’, Positionen 043/044)
# # kann Bordero-Frankatur wie folgt ergeben:
# FRANKATUR_CHOICES = { 0: 'ohne Berechnung',
#                       4: 'Frei Empfangsspediteur',
#                       2: 'frei Haus',
#                       5: 'frei Haus verzollt',
#                       6: 'frei Haus unverzollt ',
#                       7: 'unfrei',
#                       9: 'Nachlieferung',
#                       }
#
# # Hinweistextschlüssel (Satzart ‘I’, Positionen 047/048 und 079/080 sowie Satzart ‚T‘
# # Positionen 002/003, 034/035 und 066/067)
# # * Exakte Definition der Formate bei Schlüsseln mit Zusatztext:
# #    1) Datum (TTMMJJJJ); Feldgröße: 8 Stellen
# #    2) Uhrzeit (SSMM); Feldgröße: 4 Stellen
# #    Die Positionen 049 - 056 enthalten das Datum (TTMMJJJJ), Position
# #    057 ist leer, die Positionen 058 - 051 enthalten die Uhrzeit (SSMM).
# HINWEISTEXTTYP_CHOICES = { 1: 'Sendung bitte avisieren unter Tel.-Nr.',
#                            2: 'Recall-Service - Nach Zustellung Rückruf unter Tel.-Nr.',
#                            3: 'Achtung Zollgut, Anlage Zollversandschein',
#                           14: 'Termindienst! Auslieferung spätestens am (nicht Eingangstag)',
#                           15: 'Fixtermin! Nicht früher oder später - am',
#                           16: 'Termingut! Unbedingt zustellen in KW:',
#                           17: 'SystemPlus 10-Uhr-Service - Zustellung bis 10.00 Uhr',
#                           18: 'SystemPlus 12-Uhr-Service - Zustellung bis 12.00 Uhr',
#                           19: 'SystemPlus Next-Day-Service (24 Std.-Service)',
#                           20: 'SystemPlus international Express Service',
#                           21: 'Sendung bitte nur liegend transportieren',
#                           22: 'Thermogut - vorgegebenen Temperaturbereich beachten',
#                           23: 'Empfänger kann Regalservice verlangen',
#                           25: 'Samstag-Service via Night Star Express',
#                           50: 'Warenwertnachnahme - Quick-Nachnahme',
#                           51: 'Zustellung unbedingt mit Hebebühnen-LKW',
#                           52: 'Sendung vor Zustellung telefonisch avisieren',
#                           53: 'Achtung Warenwertnachnahme - nur gegen bar ausliefern',
#                           58: 'Warenwertnachnahme - Verrechnungsscheck',
#                           60: 'Sendung ohne Entladung direkt ausliefern',
#                           61: 'Empfindliche Ware - vorsichtig behandeln',
#                           70: 'Lieferscheinnummer',
#                           71: 'Kundenauftragsnummer',
#                           72: 'Abholauftragsreferenz',
#                           73: 'Freie weitere Kundenreferenz',
#                           74: 'Retourenreferenz',
#                           }
#
#
# # Hinweistextschlüssel der Auftragsart (Satzart ‘I’, Position 127)
# # 'I': ('%(sendungsnummer)-16s%(sendungskilo)05d0000000000%(ladedm)03d    %(frankatur)-2s%(frankatur)-2s  %(foo)30s  %(foo)30s%(foo)16s  '),
# Ifelder = [
#     dict(lentgth=16, startpos=  0, endpos= 16, name='Sendungs-Nr. Versandpartner****** muss'),
#     dict(lentgth= 5, startpos= 16, endpos= 21, name='gewicht', fieldclass=IntegerField,
#          doc="Sendungsgewicht in KG"),
#     dict(lentgth= 5, startpos= 21, endpos= 26, name='gewicht_frachtpflichtig', fieldclass=IntegerField,
#          doc="Frachtpflichtiges Sendungsgewicht in KG"),
#     dict(lentgth= 5, startpos= 26, endpos= 31, name='kubikdezimeter', fieldclass=IntegerField),
#     dict(lentgth= 3, startpos=  0, endpos=123, name='lademeter', fieldclass=DecimalFieldWithoutDot,
#          precision=1),
#     dict(lentgth= 2, startpos=  0, endpos=123, name='zusaetzliche_ladehilfsmittel', fieldclass=IntegerField),
#     dict(lentgth= 2, startpos=  0, endpos=123, name='verpackungsart_zusaetzliche_ladehilfsmittel'), # 2 041 - 042
#     dict(lentgth= 2, startpos=  0, endpos=123, name='frankatur_fpediteur-Über- gabeschein* muss', choices=FRANKATUR_CHOICES), # 2 043 - 044
#     dict(lentgth= 2, startpos=  0, endpos=123, name='Frankatur Bordero* muss', choices=FRANKATUR_CHOICES), # 2 045 - 046
#     dict(lentgth= 2, startpos=  0, endpos=123, name='Hinweistextschlüssel 1** kann'), # 2 047 - 048
#     dict(lentgth=30, startpos=  0, endpos=123, name='Hinweiszusatztext 1 kann'), # 30 049 - 078
#     dict(lentgth= 2, startpos=  0, endpos=123, name='Hinweistextschlüssel 2** kann'), # 2 079 - 080
#     dict(lentgth=30, startpos=  0, endpos=123, name='Hinweiszusatztext 2 kann'), # 30 081 - 110
#     dict(lentgth=16, startpos=  0, endpos=123, name='Sendungs-Nr.  Empfangspartner*** kann'),  # 16 111 - 126
#     dict(lentgth= 1, startpos=121, endpos=122, name='auftragsart**** kann'), # 1 127 - 127
#     dict(lentgth= 1, startpos=122, endpos=123, name='lieferscheindaten_folgen', fieldclass=FixedField,
#          default=' '),
# ]
#** siehe beigefügter Hinweistextschlüssel
#*** bei Nachlieferungen (Original-Sendungs-Nr. des EP) bzw. bei Ersterfassung von über-
#zähligen Sendungen (vorläufige Sendungs-Nr. des EP)
#**** siehe beigefügter Schlüsseltabelle für Auftragsarten


# 'L': ('%(sendungen)05d%(packstuecke)05d%(bruttogewicht)05d'
#       + '%(kostensteuerplichtig)09d%(kostensteuerfrei)09d000000000%(kostenzoll)09d'
#       + '%(eust)09d000%(gitterboxen)03d%(europaletten)03d000000000000'
#       + '%(sonstigeladehilfsmittel)03d000N%(foo)36s'),
#                                                (Muss/Kann)              davon dezimal                      Position
# Bordero-Summen-Satz       muss
# (je Bordero 1x)
# Satzart ‘L’ muss 1 001 - 001
# Konstante ‘999’ muss 3/0 002 - 004
# Gesamt-Sendungs-Anzahl muss 5/0 005 - 009
# Gesamt-Packstück-Anzahl muss 5/0 010 - 014
# Tatsächliches Bruttoge-
# wicht gesamt in kg muss 5/0 015 - 019
# Gesamt-Empf.-Kosten
# steuerpflichtig muss 9/2 020 - 028
# Gesamt-Empf.-Kosten
# steuerfrei muss 9/2 029 - 037
# Gesamt-Versendernach-
# nahme muss 9/2 038 - 046
# Gesamt-Zoll muss 9/2 047 - 055
# Gesamt-EUSt muss 9/2 056 - 064
# Anzahl SB = spediteur-
# eigene Behälter muss 3/0 065 - 067
# Anzahl GP = Gitterbox-
# Paletten** muss 3/0 068 - 070
# Anzahl FP = Euro-Flach-
# Paletten** muss 3/0 071 - 073
# Anzahl CC = Collico muss 3/0 074 - 076
# Anzahl AD = Bahnbehälter muss 3/0 077 - 079
# Anzahl BD = Bahnbehälter muss 3/0 080 - 082
# Anzahl CD = Bahnbehälter muss 3/0 083 - 085
# Anzahl FP = zusätzliche
# Ladehilfsmittel ** muss 3/0 086 - 088
# Anzahl GP = zusätzliche
# Ladehilfsmittel** muss 3/0 089 - 091
# Clearing-Kennzeichen (J/N)*muss 1 092 - 092
# Frei  36 093 - 128
# Die Summenfelder für Frachtbeträge, Kosten und Nachnahmen innerhalb dieser Satzart sind
# währungsneutral, d.h. es ist lediglich eine Summierung der Werte aus der Satzart K vorzunehmen.
# Eine Währungsumrechnung darf nicht erfolgen.
# * J  = Kosten sind für das Clearing zu berücksichtigen (wird nicht verwendet)
# N = Kosten sind nicht für das Clearing zu berücksichtigen (wird nicht verwendet)
#
#
# 'T': ('%(textschluessel1)02s%(hinweistext1)-30s'
#       + '%(textschluessel2)02s%(hinweistext2)-30s'
#       + '%(textschluessel3)02s%(hinweistext3)-30s%(foo)28s'),
# Textschlüssel-Satz*                        kann
# (je Sendung maximal 3x)
# Satzart ‘T’ muss 1 001 - 001
# Laufende Bordero-Position muss 3/0 002 - 004
# Hinweistextschlüssel 1** kann 2 005 - 006
# Hinweiszusatztext 1 kann 30 007 - 036
# Hinweistextschlüssel 2** kann 2 037 - 038
# Hinweiszusatztext 2 kann 30 039 - 068
# Hinweistextschlüssel 3** kann 2 069 - 070
# Hinweiszusatztext 3 kann 30 071 - 100
# Frei
#
# 'J':  '%(zusatztext1)-62s%(zusatztext2)-62s',
# Satzart ‘J’ muss 1 001 - 001
# Laufende Bordero-Position muss 3/0 002 - 004
# Zusatztext 1 muss 62 005 - 066
# Zusatztext 2 kann 62 067 - 128

class Bordero(object):
    """Kapselt die Daten für ein Gefäß (LKW) - Verwendung ähnlich IFTSTAR."""

    def __init__(self, empfangspartner='11515'):
        super(Bordero, self).__init__()
        self.filename = ""
        self.empfangspartner = empfangspartner
        self.lieferungen = []
        self.satznummer = 0
        self.borderonr = None
        self.verladung = None
        self.generated_output = ''
        # definitions of records
        self.satzarten = {'A': (u'%(borderonr)018d%(datum)-8s%(versandweg)s  %(empfangspartner)-10s %(frachtfuehrer)'
                                + '-13s%(plz)-9s%(ort)-12s%(foo)-49s6'),
                          'B': u'%(name1)-35s%(name2)-35s%(strasse)-35s%(lkz)-3s%(plz)-9s       ',
                          'C': u'%(ort)-35s%(foo)-3s%(foo)9s%(foo)35s%(kdnnr)17s%(wert)09fEUR%(foo)-13s',
                          'D': u'%(name1)-35s%(name2)-35s%(foo)-35s%(foo)-19s',
                          'E': (u'%(strasse)-35s%(lkz)-3s%(plz)-9s%(ort)-35s%(foo)3s%(matchcode)-10s'
                                + '%(kdnnr)17s%(foo)10s%(foo)2s'),
                          'F': (u'%(anzahlpackstuecke)04d%(verpackungsart)2s0000  %(wareninhalt)-20s'
                                + '%(zeichennr)-20s%(sendungskilo)05d00000%(foo)-62s'),
                          'H': '002%(barcode)-35s%(foo)35s%(foo)35s%(foo)16s',
                          'I': (u'%(sendungsnummer)-16s%(sendungskilo)05d0000000000%(ladedm)03d    '
                                + '%(frankatur)-2s%(frankatur)-2s  %(foo)30s  %(foo)30s%(foo)16s  '),
                          'L': (u'%(sendungen)05d%(packstuecke)05d%(bruttogewicht)05d'
                                + '%(kostensteuerplichtig)09d%(kostensteuerfrei)09d000000000%(kostenzoll)09d'
                                + '%(eust)09d000%(gitterboxen)03d%(europaletten)03d000000000000'
                                + '%(sonstigeladehilfsmittel)03d000N%(foo)36s'),
                          'T': (u'%(textschluessel1)02s%(hinweistext1)-30s'
                                + '%(textschluessel2)02s%(hinweistext2)-30s'
                                + '%(textschluessel3)02s%(hinweistext3)-30s%(foo)28s'),
                          'J': u'%(zusatztext1)-62s%(zusatztext2)-62s',
                          }

    def add_lieferung(self, lieferung):
        """Adds a lieferung to our Bordero."""
        if self.generated_output:
            raise RuntimeError('tried to  add data to an already exported Bordero.')
        self.lieferungen.append(lieferung)

    def generate_satz(self, satzart, data):
        """Helper function to generate output for a Record."""
        ret = (u'%s%03d' % (satzart, self.satznummer)) + (self.satzarten[satzart] % data)
        if len(ret) != 128:
            raise RuntimeError('bordero Satz %r kaputt! (len=%r) %r %r' % (satzart, len(ret), ret, data))
        return ret

    def generate_kopfsatz_a(self, verladung=None):
        """Generates bodero record A - header."""
        # Bordro nummer - Fortlaufend?
        # Verkehrsart - immer LKW?
        # IDNr des Verrsandpartyners beim Empfangspartern? L515
        # Frachtführername - Mäuler?
        # Ladeeinheitnr - 1 & 2? frei
        # Plombennummer ?        frei
        if not self.borderonr:
            raise RuntimeError('No bordero nr set.')
        data = {'empfangspartner': self.empfangspartner, 'frachtfuehrer': 'Maeuler', 'plz': '42897',
                'ort': 'Remscheid', 'versandweg': 'L', 'foo': '',
                'datum': time.strftime('%d%m%Y'),
                'borderonr': self.borderonr}
        if verladung:
            if verladung.spedition == 'Direktfahrt':
                data['versandweg'] = 'X'
        return self.generate_satz('A', data)

    def generate_versendersatz_b(self, lieferung):
        """Generates bodero record B - first half of sender."""
        data = {'name1': 'HUDORA GmbH', 'name2': '', 'strasse': u'Jägerwald 13', 'lkz': 'DE',
                'plz': '42897'}
        return self.generate_satz('B', data)

    def generate_versendersatz_c(self, lieferung):
        """Generates bodero record C - second half of sender."""
        data = {'ort': 'Remscheid', 'foo': ' ', 'kdnnr': self.empfangspartner, 'wert': 0}
        return self.generate_satz('C', data)

    def generate_empfaengersatz_d(self, lieferung):
        """Generates bodero record D - first half of recipient."""
        data = {'name1': _clip(35, lieferung.name1), 'name2': _clip(35, lieferung.name2), 'foo': ' '}
        return self.generate_satz('D', data)

    def generate_empfaengersatz_e(self, lieferung):
        """Generates bodero record E - second half of recipient."""
        data = {'strasse': _clip(35, lieferung.adresse), 'lkz': _clip(3, lieferung.land),
        'plz': _clip(9, lieferung.plz), 'ort': _clip(35, lieferung.ort), 'kdnnr': lieferung.kundennummer,
        'matchcode': _clip(10, (lieferung.name1 + lieferung.ort).replace(' ', '')), 'foo': ' '}
        return self.generate_satz('E', data)

    def generate_sendungspossatz_f(self, lieferung):
        """Generates bodero record F."""
        # Packstück Anzahl? Pakete? Paletten? NVEs!
        # Fuer weitere Paletten typen neuen Satz
        # Tatsächliches Gewicht einpflegen
        data = {'anzahlpackstuecke': len(lieferung.packstuecke),
        'verpackungsart': _clip(2, 'FP'),
        'sendungskilo': int(lieferung.gewicht / 1000),
        'wareninhalt': _clip(20, 'HUDORA Sportartikel'),
        'zeichennr': _clip(20, '%s/%s' % (lieferung.lieferscheinnummer, lieferung.id)),
        'foo': ''}
        return self.generate_satz('F', data)

    def generate_packstuecksatz(self, lieferung, packstueck):
        """Generates bodero record H."""
        barcode = packstueck.nve
        if not barcode.startswith('00'):
            barcode = '00' + barcode
        data = {'barcode': barcode,
        'foo': ' '}
        return self.generate_satz('H', data)

    def generate_sendungsinfosatz_i(self, lieferung):
        """Generates bodero record I."""
        # Sendungsnummer - eindeutig!
        data = {'sendungsnummer': _clip(16, "%016s" % lieferung.id),
        'ladedm': 0,
        'frankatur': '02',  # frei Haus
        'foo': ' '}
        data['sendungskilo'] = int(lieferung.gewicht / 1000)
        return self.generate_satz('I', data)

    def generate_textsatz_t(self, lieferung, schluesselliste):
        """Generates bodero record(s) T - text info."""
        satz = []
        ret = []
        for schluessel, text in schluesselliste:
            satz.append((schluessel, text))
            if len(satz) == 3:
                data = {'textschluessel1': '%02d' % int(satz[0][0]), 'hinweistext1': _clip(30, satz[0][1]),
                        'textschluessel2': '%02d' % int(satz[1][0]), 'hinweistext2': _clip(30, satz[1][1]),
                        'textschluessel3': '%02d' % int(satz[2][0]), 'hinweistext3': _clip(30, satz[2][1]),
                        'foo': ' '}
                satz = []
                ret.append(self.generate_satz('T', data))
        if len(satz) > 0:
            data = {'textschluessel1': '%02s' % int(satz[0][0]), 'hinweistext1': _clip(30, satz[0][1]),
                    'textschluessel2': '  ', 'hinweistext2': '',
                    'textschluessel3': '  ', 'hinweistext3': '',
                    'foo': ' '}
            if len(satz) > 1:
                data['textschluessel2'] = '%02d' % int(satz[1][0])
                data['hinweistext2'] = _clip(30, satz[1][1])
            ret.append(self.generate_satz('T', data))
        return '\n'.join(ret)

    def generate_textsaetze(self, lieferung):
        """Generate as many T records as needed."""
        schluesselliste = []
        if lieferung.avisieren_unter:
            # 52 = Sendung vor Zustellung telefonisch avisieren
            # 01 = Sendung bitte avisieren unter Tel.-Nr.: ...(Zusatztext)
            schluesselliste.append(('01', _clip(30, lieferung.avisieren_unter)))
        if lieferung.fixtermin:
            # 15 = Fixtermin! Nicht früher oder später - am: ... (Zusatztext)*
            datum = lieferung.fixtermin.strftime('%d%m%Y')
            zeit = lieferung.fixtermin.strftime('%H:%M')
            if zeit == '00:00':
                zeit = '     '
            timestamp = '%8s %5s' % (datum, zeit)
            schluesselliste.append(('15', _clip(30, timestamp)))
        if lieferung.hebebuehne:
            # 51 = Zustellung unbedingt mit Hebebühnen-LKW
            schluesselliste.append(('51', _clip(30, 'Zustellung mit Hebebühne')))
        if lieferung.auftragsnummer_kunde.strip():
            # 71 = Kundenauftragsnummer (Nummer im Zusatztext)
            schluesselliste.append(('71', _clip(30, lieferung.auftragsnummer_kunde)))
        # 70 = Lieferscheinnummer (Nummer im Zusatztext)
        schluesselliste.append(('70', _clip(30, lieferung.lieferscheinnummer)))
        # 73 = Freie weitere Kundenreferenz (Referenz im Zusatztext)
        # schluesselliste.append(('73', _clip(30, 'http://hudora.de/track/XXX')))

        # 14 = Termindienst! Auslieferung spätestens am (nicht Eingangstag): (Zusatztext)*
        # 16 = Termingut! Unbedingt zustellen in KW: ... (Zusatztext)
        # 61 = Empfindliche Ware - vorsichtig behandeln
        return self.generate_textsatz_t(lieferung, schluesselliste)

    def generate_zusatztextsatz_j(self, lieferung):
        """Generates bodero record J - additional text info."""
        data = {'zusatztext1': _clip(62, u'AuftragsNr: %s / KundenNr: %s' %
                                         (lieferung.auftragsnummer, lieferung.kundennummer)),
                'zusatztext2': _clip(62, u'huLOG Code: %s' % lieferung.code),
                'foo': ' '}
        return self.generate_satz('J', data)

    def generate_summensatz_l(self):
        """Generates bodero record L."""
        # Was ist ein Packstück? => NVEs
        # Empfangskosten?
        # Was bei Einwegpaletten?
        # Was bei CHEP / Düsseldorfer Paletten = speditereigenebehaelter
        # clearing kennzeichen?
        data = {'sendungen': len(self.lieferungen),
            'bruttogewicht': int(sum([lieferung.gewicht for lieferung in self.lieferungen]) / 1000),
            'kostensteuerplichtig': 0,
            'kostensteuerfrei': 0,
            'kostenzoll': 0,
            'eust': 0,
            'gitterboxen': 0,
            'europaletten': sum([len(lieferung.packstuecke) for lieferung in self.lieferungen]),
            'packstuecke': sum([len(lieferung.packstuecke) for lieferung in self.lieferungen]),
            'sonstigeladehilfsmittel': 0,
            'foo': '',
        }
        self.satznummer = 999
        return self.generate_satz('L', data)

    def generate_lieferungssaetze(self, lieferung):
        """Generates all bodero records for a shipment."""
        self.satznummer += 1
        out = []
        out.append(self.generate_versendersatz_b(lieferung))
        out.append(self.generate_versendersatz_c(lieferung))
        out.append(self.generate_empfaengersatz_d(lieferung))
        out.append(self.generate_empfaengersatz_e(lieferung))
        out.append(self.generate_sendungspossatz_f(lieferung))
        for packstueck in lieferung.packstuecke:
            out.append(self.generate_packstuecksatz(lieferung, packstueck))
        out.append(self.generate_sendungsinfosatz_i(lieferung))
        out.append(self.generate_textsaetze(lieferung))
        out.append(self.generate_zusatztextsatz_j(lieferung))
        return u'\n'.join(out)

    def generate_dataexport(self):
        """Return complete BODERO data."""
        if not self.generated_output:
            out = []
            out.append(self.generate_kopfsatz_a(self.verladung))
            for lieferung in self.lieferungen:
                out.append(self.generate_lieferungssaetze(lieferung))
            out.append(self.generate_summensatz_l())
            self.generated_output = (u"@@PHBORD128 0128003500107 HUDORA1 MAEULER\n"
                                     + u'\n'.join(out) + u'\n@@PT\n')
        return self.generated_output


def ship(verladung, empfangspartner='11515', basedir='/usr/local/maeuler/current/In/BORD/'):
    """Creates a BORDERO object and writes it to a file.

    The file lies in directory basedir containing the borderonr and a timestamp in its name.
    Returns the BORDERO object w/ its filename attached.
    """
    bordero = Bordero(empfangspartner)
    bordero.verladung = verladung
    bordero.borderonr = verladung.borderonr
    for lieferung in verladung.lieferungen:
        bordero.add_lieferung(lieferung)
    data = bordero.generate_dataexport()  # generate first to assure bordero.borderonr is set
    # we first create a temporary file and later rename it to it's final name
    basefilename = time.strftime('%Y%m%dT%H%M%S') + ('_%05d.txt' % (bordero.borderonr))
    tmpfilename = os.path.join(basedir, '._' + basefilename + '_tmp')
    filename = os.path.join(basedir, basefilename)
    outfile = open(tmpfilename, 'w')
    outfile.write(data.encode('latin-1', 'ignore'))
    outfile.close()
    os.rename(tmpfilename, filename)
    for lieferung in verladung.lieferungen:
        lieferung.ship()
        lieferung.log(code=201, message="Verladung abgeschlossen / DFü an Spedition (Mäuler)")
        lieferung.save()
    verladung.ship()
    bordero.filename = filename
    return bordero


def ship_lieferungen(lieferungen, empfangspartner='11515'):
    """Should be called when 'lieferungen' just left the building."""
    bordero = Bordero(empfangspartner)
    for lieferung in lieferungen:
        bordero.add_lieferung(lieferung)
    data = bordero.generate_dataexport()  # generate first to assure bordero.borderonr is set
    # we first create a temporary file and later rename it to it's finaal name
    filename = time.strftime('%Y%m%dT%H%M%S') + ('_%05d.txt' % (bordero.borderonr))
    outfile = open(os.path.join('/usr/local/maeuler/current/In/BORD/', '._' + filename + '_tmp'), 'w')
    outfile.write(data)
    outfile.close()
    os.rename(os.path.join('/usr/local/maeuler/current/In/BORD/', '._' + filename + '_tmp'),
              os.path.join('/usr/local/maeuler/current/In/BORD/', filename))
    for lieferung in lieferungen:
        lieferung.ship()
        lieferung.log(code=201, message="DFü an Mäuler")
        lieferung.save()
    return bordero
