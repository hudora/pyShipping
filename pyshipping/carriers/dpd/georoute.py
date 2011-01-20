#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
georoute.py - get DPD related routng information

Originally coded by md, cleand up and extended by jmv and then again reworked by md.
Copyright 2006, 2007 HUDORA GmbH. Published under a BSD License.
"""

import os
import os.path
import gzip
import logging
import sqlite3


ROUTETABLES_BASE = os.path.join(os.path.split(os.path.abspath(__file__))[0], 'georoutetables')
ROUTES_DB_BASE = '/tmp/dpdroutes'


# Quelle: http://de.wikipedia.org/wiki/Liste_der_Kfz-Nationalitätszeichen
ISO2CAR = {
    'AT': 'A',
    'BE': 'B',
    'FR': 'F',
}


class InvalidFormatError(Exception):
    """Invalid input file format."""
    pass


class GeorouteException(Exception):
    """Base class for all routing exceptions"""
    pass


class CountryError(GeorouteException):
    """Unknown country."""
    pass


class DepotError(GeorouteException):
    """Unknown depot."""
    pass


class ServiceError(GeorouteException):
    """Unknown service."""
    pass


class TranslationError(GeorouteException):
    """Cannot translate city and country to postcode."""
    pass


class RoutingDepotError(GeorouteException):
    """Unknown routing depot."""
    pass


class NoRouteError(GeorouteException):
    """Route not found."""
    pass


class Parcel(object):
    """Parcel destination data."""

    # depreciated
    def __init__(self, depot='142', service='101', country='DE', city=None, postcode=None):
        import warnings
        warnings.warn("Parcel() is deprecated", DeprecationWarning, stacklevel=2)

        self.service = service
        self.country = country
        self.city = city
        self.postcode = postcode


class Destination(object):
    """Parcel destination data."""

    def __init__(self, country='DE', postcode=None, city=None, service='101'):
        self.service = service
        self.country = country
        self.city = city
        self.postcode = postcode


class Route:
    """Output of the routing algorithm."""

    def __init__(self, d_depot, o_sort, d_sort, grouping_priority, barcode_id,
                 iata_code, service_text, service_mark, country, serviceinfo, countrynum,
                 routingtable_version, postcode):
        self.d_depot = d_depot
        self.o_sort = o_sort
        self.d_sort = d_sort
        self.grouping_priority = grouping_priority
        self.barcode_id = barcode_id
        self.iata_code = iata_code
        self.service_text = service_text
        self.service_mark = service_mark
        self.country = country
        self.serviceinfo = serviceinfo
        self.countrynum = countrynum
        self.routingtable_version = routingtable_version
        self.postcode = postcode

    def __unicode__(self):
        output = u"""Output parameters:
Country: %s
D-Depot: %s
O-Sort: %s
D-Sort: %s
Grouping priority: %s
Barcode ID: %s
ITA Code: %s
Service Text: %s""" % (self.country, self.d_depot, self.o_sort, self.d_sort,
                       self.grouping_priority, self.barcode_id, self.iata_code,
                       self.service_text)
        if self.service_mark:
            output += "\nService Mark: %s" % self.service_mark
        if self.iata_code:
            output += "\nIATA Code: %s" % self.iata_code
        if self.serviceinfo:
            output += "\nService Info: %s" % self.serviceinfo

        return output

    def __repr__(self):
        return repr(vars(self))

    def routingdata(self):
        return {'o_sort': self.o_sort, 'd_sort': self.d_sort,
                'd_depot': self.d_depot, 'country': self.country,
                'service_text': self.service_text, 'serviceinfo': self.serviceinfo}


def _readfile(filename):
    """Read file line-by-line skipping comments."""
    if os.path.exists(filename + '.gz'):
        fhandle = gzip.GzipFile(filename + '.gz')
    else:
        fhandle = file(filename)
    for line in fhandle:
        line = line.strip().decode('latin1')
        if line.startswith('#'):
            continue
        yield line.split('|')


class RouteData(object):
    """More convenient representation of the georoute data."""

    def __init__(self, routingdepot='0142'):
        """Routingdepot the depot from where you are sending."""
        self.routingdepot = routingdepot
        self.routingdepotgroups = ''
        self.routingdepotcountry = ''

        services = os.path.join(ROUTETABLES_BASE, 'SERVICE')
        self.version = None
        for line in file(services):
            if line.startswith('#Version: '):
                self.version = line.split(':')[1].strip()
                break
        if self.version is None:
            raise InvalidFormatError("There's no version in the SERVICE file")

        self.countries = {}
        for line in _readfile(os.path.join(ROUTETABLES_BASE, 'COUNTRY')):
            isonum, isoname = line[:2]
            self.countries[isoname.upper()] = isonum

        self.depots = {}
        for line in _readfile(os.path.join(ROUTETABLES_BASE, 'DEPOTS')):
            geopostdepotnumber = line[0]
            self.depots[geopostdepotnumber] = tuple(line)

        self.services = {}
        for line in _readfile(os.path.join(ROUTETABLES_BASE, 'SERVICE')):
            servicecode = line[0]
            self.services[servicecode] = tuple(line)

        self.serviceinfo = {}
        for line in _readfile(os.path.join(ROUTETABLES_BASE, 'SERVICEINFO.DE')):
            servicecode = line[0]
            self.serviceinfo[servicecode] = line[1]

        filename = ROUTES_DB_BASE + ('-%s-%s.db' % (routingdepot, self.version))
        self.db = sqlite3.connect(filename)

        self.read_depots(ROUTETABLES_BASE)
        self.read_locations(ROUTETABLES_BASE)
        self.read_routes(ROUTETABLES_BASE)

    def read_depots(self, path):
        """Read DEPOTS file and save all the information in a
        SQLite database."""
        c = self.db.cursor()

        c.execute("""SELECT COUNT(*)
                     FROM sqlite_master
                     WHERE type = 'table' AND name = 'depots'""")
        if not c.fetchone()[0]:
            logging.info("regenerating depots table")
            c.execute("""CREATE TABLE depots
            (DepotNumber TEXT PRIMARY KEY,
             IATACode TEXT,
             GroupId TEXT,
             Name1 TEXT,
             Name2 TEXT,
             Address1 TEXT,
             Address2 TEXT,
             Postcode TEXT,
             CityName TEXT,
             Country TEXT,
             Phone TEXT,
             Fax TEXT,
             Mail TEXT,
             Web TEXT)""")

            for line in _readfile(os.path.join(path, 'DEPOTS')):
                c.execute("""INSERT INTO depots
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                          line[:14])
                if line[0] == self.routingdepot:
                    self.routingdepotgroups = line[2]
                    self.routingdepotgrouplist = line[2].split(',')
                    self.routingdepotcountry = line[9]
            c.execute('VACUUM;')

    def read_locations(self, path):
        """Read LOCATION file and save all the information in a SQLite database."""
        c = self.db.cursor()

        c.execute("""SELECT COUNT(*)
                     FROM sqlite_master
                     WHERE type='table' AND name='location'""")
        if not c.fetchone()[0]:
            logging.info("regenerating location table")
            c.execute("""CREATE TABLE location
            (Area TEXT,
             City TEXT,
             Country TEXT,
             Postcode TEXT)""")

            for line in _readfile(os.path.join(path, 'LOCATION.DE')):
                c.execute('INSERT INTO location VALUES (?,?,?,?)',
                          line[:4])
            c.execute('VACUUM;')

    def read_routes(self, path):
        """Read ROUTES file and save all the information in a SQLite database."""
        # self.db = sqlite3.connect(ROUTES_DB)
        c = self.db.cursor()

        c.execute("""SELECT COUNT(*)
                     FROM sqlite_master
                     WHERE type='table' AND name='routes'""")
        if not c.fetchone()[0]:
            logging.info("regenerating routes table")
            c.execute("""CREATE TABLE routes
            (id INTEGER PRIMARY KEY,
            DestinationCountry TEXT,
            BeginPostCode TEXT,
            EndPostCode TEXT,
            ServiceCodes TEXT,
            RoutingPlaces TEXT,
            SendingDate TEXT,
            OSort TEXT,
            DDepot TEXT,
            GroupingPriority TEXT,
            DSort TEXT,
            BarcodeID TEXT)""")

            c.execute("""SELECT COUNT(*)
                         FROM sqlite_master
                         WHERE type='table' AND name='routedepots'""")
            if not c.fetchone()[0]:
                logging.info("regenerating routedepots table")
                c.execute("""CREATE TABLE routedepots
                (route INTEGER,
                 depot TEXT)""")

            c.execute("PRAGMA synchronous=OFF;")
            c.execute("PRAGMA temp_store=MEMORY;")
            i = 1
            for line in _readfile(os.path.join(path, 'ROUTES')):
                services = self.expand_services(line[3])
                c.execute('INSERT INTO routes VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
                          [i] + line[:3] + [services] + line[4:-1])
                self.expand_depots(i, line[4], c)
                i += 1

            c.execute("CREATE INDEX routes_DestinationCountry ON routes(DestinationCountry)")
            c.execute("CREATE INDEX routes_BeginPostCode ON routes(BeginPostCode)")
            c.execute("CREATE INDEX routes_EndPostCode ON routes(EndPostCode)")
            c.execute("CREATE INDEX routedepots_route ON routedepots(route)")
            c.execute("CREATE INDEX routedepots_depot ON routedepots(depot)")
            c.execute('VACUUM;')  # also commits the database

    def expand_services(self, services):
        """Expand services list."""
        services_list = []
        for service in services.split(','):
            if len(service) > 4:
                start = int(service[1:4])
                end = int(service[4:])
                for i in range(start, end + 1):
                    services_list.append(unicode(i))
            else:
                services_list.append(service[1:])

        return ','.join(services_list)

    def expand_depots(self, route, depots, c):
        """Parse depots list and generate route->depots relationship."""
        # but only four "our" depot.
        # if you change the self.routingdepot, you have to rebuild the database
        if depots == '':
            c.execute("""INSERT INTO routedepots(route, depot) VALUES (?, ?)""", (route, depots))
            return

        for depot in depots.split(','):
            if depot.startswith('C'):
                if depot[1:] == self.routingdepotcountry:
                    c.execute("""INSERT INTO routedepots(route, depot) VALUES(?, ?)""", (route,
                                                                                         self.routingdepot))
            elif depot.startswith('D'):
                if len(depot) > 5:
                    start = int(depot[1:5])
                    end = int(depot[5:])
                    for i in range(start, end + 1):
                        if ("%04d" % i) == self.routingdepot:
                            c.execute("""INSERT INTO routedepots(route, depot) VALUES(?, ?)""",
                                      (route, self.routingdepot))
                else:
                    if depot[1:5] == self.routingdepot:
                        c.execute("""INSERT INTO routedepots(route, depot) VALUES(?, ?)""",
                                  (route, depot[1:5]))
            elif depot.startswith('G'):
                if depot[1:] in self.routingdepotgroups:
                    c.execute("INSERT INTO routedepots(route, depot) VALUES(?, ?)",
                              (route, self.routingdepot))
            else:
                raise InvalidFormatError("Unable to parse depot '%s'" % depot)

    def get_countrynum(self, isoname):
        """Return country ISO code."""
        if not isoname.upper() in self.countries:
            raise CountryError("Country %s unknown" % isoname)
        return self.countries[isoname.upper()]

    def get_depot(self, depotnumber):
        """Return depot."""
        if not depotnumber in self.depots:
            raise DepotError("Depot %s unknown" % depotnumber)
        return self.depots[depotnumber]

    def get_service(self, servicecode):
        """Return service."""
        if not servicecode in self.services:
            raise ServiceError("Service %s unknown" % servicecode)
        return self.services[servicecode]

    def get_servicetext(self, servicecode):
        """Return service info to be printed on label."""
        if not servicecode in self.serviceinfo:
            return ''
        return self.serviceinfo[servicecode]

    def translate_location(self, city, country):
        """Return postcode for given city and country."""
        cur = self.db.cursor()
        cur.execute("SELECT Postcode FROM location WHERE City=? AND Country=?", (city, country))
        rows = cur.fetchall()
        if not rows:
            raise TranslationError("Cannot find postcode for location %s, %s" % (city, country))
        return rows[0][0]


class Router(object):
    """Routes parcels."""

    def __init__(self, data):
        self.route_data = data
        self.db = self.route_data.db

    def route(self, parcel):
        """Find route."""

        self.current_subset = []
        self.conditions = ['1=1']
        self.cleanup_postcode(parcel)

        self.select_country(parcel)
        if parcel.postcode is None:
            parcel.postcode = self.route_data.translate_location(parcel.city, parcel.country)
            self.subsetstack.append(self.subset)

        self.select_postcode(parcel)
        self.select_service(parcel)
        self.select_depot(parcel)
        # Sending date is not used yet, according to documentation

        if len(self.current_subset) == 1:
            rows = self.select_routes("1=1")
            (service_text, service_mark) = self.route_data.get_service(parcel.service)[1:3]
            depot = self.route_data.get_depot(rows[0][8])
            iata_code = depot[1]
            country = depot[9]
            if not country:
                country = parcel.country
            serviceinfo = self.route_data.get_servicetext(parcel.service)

            return Route(rows[0][8], rows[0][7], rows[0][10], rows[0][9], rows[0][11],
                         iata_code, service_text, service_mark, country,
                         serviceinfo, self.route_data.get_countrynum(country),
                         self.route_data.version, parcel.postcode)
        raise NoRouteError("No route found for %r|%r|%r" % \
              (parcel.country, parcel.postcode, parcel.service))

    def add_condition(self, condition):
        self.conditions.append(condition)

    def select_routes(self, condition, params=()):
        """Find routes matching condition and currently selected subset of the routes table.
        If routes are found, save their ids for narrowing future searches.
        If no routes are found, do not change current subset.
        """

        subsetcondition = ' AND '.join(self.conditions)
        cur = self.db.cursor()
        cur.execute("SELECT * FROM routes WHERE %s AND %s" % (subsetcondition, condition), params)
        rows = cur.fetchall()

        # Save matched rows if there were any results
        if rows:
            self.add_condition(condition)
        self.current_subset = [unicode(row[0]) for row in rows]
        return rows

    def select_country(self, parcel):
        """Select all routes with the given country."""
        rows = self.select_routes("DestinationCountry='%s'" % (parcel.country.upper().replace("'", ''), ))
        if not rows:
            raise CountryError("Country %s unknown" % parcel.country)

    def cleanup_postcode(self, parcel):
        """Removes spaces and country prefixes from postcodes."""

        if not parcel.postcode:
            return
        parcel.postcode = parcel.postcode.replace(' ', '').strip()
        if parcel.postcode.startswith('-'):
            parcel.postcode = parcel.postcode[1:]
            self.cleanup_postcode(parcel)
        if parcel.postcode.upper().startswith(parcel.country.upper()):
            parcel.postcode = parcel.postcode[len(parcel.country):]
            self.cleanup_postcode(parcel)
        if parcel.country.upper() in ISO2CAR:
            if parcel.postcode.upper().startswith(ISO2CAR[parcel.country.upper()]):
                parcel.postcode = parcel.postcode[len(ISO2CAR[parcel.country.upper()]):]
                self.cleanup_postcode(parcel)
        if parcel.country.upper() == 'DE' and parcel.postcode.upper().startswith('CH-'):
            parcel.country = 'CH'
            parcel.postcode = parcel.postcode[2:]
            self.cleanup_postcode(parcel)
        if parcel.country.upper() == 'DE' and parcel.postcode.upper().startswith('BE-'):
            parcel.country = 'BE'
            parcel.postcode = parcel.postcode[2:]
            self.cleanup_postcode(parcel)
        if parcel.country.upper() == 'DE' and parcel.postcode.upper().startswith('B-'):
            parcel.country = 'BE'
            parcel.postcode = parcel.postcode[1:]
            self.cleanup_postcode(parcel)
        if parcel.country.upper() == 'DE' and parcel.postcode.upper().startswith('AT-'):
            parcel.country = 'AT'
            parcel.postcode = parcel.postcode[2:]
            self.cleanup_postcode(parcel)
        if parcel.country.upper() == 'DE' and parcel.postcode.upper().startswith('A-'):
            parcel.country = 'AT'
            parcel.postcode = parcel.postcode[1:]
            self.cleanup_postcode(parcel)

    def select_postcode(self, parcel):
        """Select all routes matching the given postcode."""

        # direct match
        rows = self.select_routes("BeginPostCode='%s'" % parcel.postcode.replace("'", ''))
        if not rows:
            # range
            rows = self.select_routes("BeginPostCode<='%s' AND EndPostCode>='%s'"
                                       % (parcel.postcode.replace("'", ''), parcel.postcode.replace("'", '')))
        if not rows:
            # catch all
            rows = self.select_routes("BeginPostCode=''")
        if not rows:
            raise NoRouteError("Postcode %r|%r unknown" % (parcel.country, parcel.postcode))

    def select_service(self, parcel):
        """Select all routes with the given service code."""

        # we have to redo postcode query as a backoff strategy
        self.conditions.pop()
        postcodequeries = ["BeginPostCode='%s'" % parcel.postcode.replace("'", ''),
            "BeginPostCode<='%s' AND EndPostCode>='%s'" % (parcel.postcode.replace("'", ''),
                                                           parcel.postcode.replace("'", '')),
            "BeginPostCode=''"]
        for postcodequery in postcodequeries:
            rows = self.select_routes("%s AND ServiceCodes LIKE '%%%s%%'" % (postcodequery, parcel.service))
            if not rows:
                # catch all
                rows = self.select_routes("%s AND ServiceCodes = ''" % (postcodequery))
            if rows:
                break
        if not rows:
            raise ServiceError("No route for service found %r|%r|%r unknown" % \
                (parcel.country, parcel.postcode, parcel.service))

    def select_depot(self, parcel):
        """Select all routes with the given depot."""
        subset = "route IN (%s)" % ','.join([unicode(route) for route in self.current_subset])
        cur = self.db.cursor()
        cur.execute("SELECT route FROM routedepots WHERE depot=%s AND %s" % (self.route_data.routingdepot,
                                                                             subset))
        rows = cur.fetchall()
        if not rows:
            cur.execute("SELECT route FROM routedepots WHERE %s" % (subset))
            rows = cur.fetchall()
        if not rows:
            raise RoutingDepotError("No route found for %r|%r|%r|%r|%r" % \
                  (parcel.country, parcel.postcode, parcel.service, self.route_data.routingdepot, subset))
        self.current_subset = [unicode(row[0]) for row in rows]


def get_route_without_cache(country=None, postcode=None, city=None, servicecode='101'):
    router = Router(RouteData())
    return router.route(Destination(country, postcode, city))


def get_route(country=None, postcode=None, city=None, servicecode='101'):
    # this includes somewhat overly complex caching
    filename = ROUTES_DB_BASE + ('_cache.db')
    cache_db = sqlite3.connect(filename, isolation_level=None)
    cur = cache_db.cursor()
    # ensure table exists
    cur.execute("""SELECT COUNT(*)
                 FROM sqlite_master
                 WHERE type = 'table' AND name = 'routing_cache'""")
    if not cur.fetchone()[0]:
        logging.info("regenerating cache table")
        cur.execute("""CREATE TABLE routing_cache
        (country_postcode_servicecode TEXT PRIMARY KEY,
        d_depot TEXT,
        o_sort TEXT,
        d_sort TEXT,
        grouping_priority TEXT,
        barcode_id TEXT,
        iata_code TEXT,
        service_text TEXT,
        service_mark TEXT,
        country TEXT,
        serviceinfo TEXT,
        countrynum TEXT,
        routingtable_version TEXT,
        postcode TEXT
        )""")

    # check if entry is cached
    cur.execute("SELECT * FROM routing_cache WHERE country_postcode_servicecode='%s'"
                 % ("%s_%s_%s" % (country, postcode, servicecode)))
    rows = cur.fetchall()
    if not rows:
        # nothing found
        route = get_route_without_cache(country, postcode, city, servicecode)
        cur.execute("""INSERT INTO routing_cache
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                             ("%s_%s_%s" % (country, postcode, servicecode),
                             route.d_depot,
                             route.o_sort,
                             route.d_sort,
                             route.grouping_priority,
                             route.barcode_id,
                             route.iata_code,
                             route.service_text,
                             route.service_mark,
                             route.country,
                             route.serviceinfo,
                             route.countrynum,
                             route.routingtable_version,
                             route.postcode))
        # For some reason closing the cache generated occasionally runtime errors.
        # cache_db.close()
    else:
        if len(rows) > 1:
            raise RuntimeError("to many cache hits!")
        route = Route(*rows[0][1:])
    return route


# compability layer to old georoute code prior to huLOG revision 1710

def find_route(depot, servicecode, land, plz):
    """Legacy method - to be removed."""

    import warnings
    warnings.warn("georoute.find_route() is deprecated use get_route() instead",
                  DeprecationWarning, stacklevel=2)

    if unicode(depot) != '0142':
        raise RuntimeError("wrong depot")
    return get_route(unicode(land), unicode(plz), servicecode=unicode(servicecode))
