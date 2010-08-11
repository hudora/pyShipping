pyShipping provides connections to interface with shipping companies and to transport shipping related information. 

 * package - shipping/cargo related calculations based on a unit of shipping (box, crate, package)
 * sendung - defines an abstract shippment (Sendung), with packages and calculations based on that
 * carriers.dpd - calculation of DPD/Georoutes routing data and labels. Included tables are for shippments from Wuppertal but it should work with all other german routing tables.
 * fortras - tools for reading and writing Fortras messages. Fortras is a EDI standard for logistics related information somewhat common in Germany. See Wikipedia_ for further enlightenment

.. _Wikipedia: http://de.wikipedia.org/wiki/Fortras

You can get it at http://pypi.python.org/pypi/pyShipping


This contains linked in the binpack module code (c) Copyright 1998, 2003, 2005, 2006 by

   David Pisinger                        Silvano Martello, Daniele Vigo
   DIKU, University of Copenhagen        DEIS, University of Bologna
   Universitetsparken 1                  Viale Risorgimento 2
   Copenhagen, Denmark                   Bologna, Italy

 This code can be used free of charge for research and academic purposes.
