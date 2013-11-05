pyShipping provides connections to interface with shipping companies and to transport shipping related information. 

 * package - shipping/cargo related calculations based on a unit of shipping (box, crate, package), includes
   a bin packing implementation in pure Python
 * sendung - defines an abstract shippment (Sendung), with packages and calculations based on that
 * addressvalidation - check if an address is valid
 * carriers.dpd - calculation of DPD/Georoutes routing data and labels. Included tables are for shippments from Wuppertal but it should work with all other german routing tables. See this Blogpost_ about updating routing information.
 * fortras - tools for reading and writing Fortras messages. Fortras is a EDI standard for logistics related information somewhat common in Germany. See Wikipedia_ for further enlightenment

.. _Wikipedia: http://de.wikipedia.org/wiki/Fortras
.. _Blogpost: https://cybernetics.hudora.biz/intern/wordpress/2010/09/dpd-routeninformationen-aktualisieren/

It also comes with the only python based `3D Bin Packing <http://www.cs.sunysb.edu/~algorith/files/bin-packing.shtml>`_ implementation I'm aware of. The Algorithm has sufficient performance to be used in everyday shipping and warehousing applications.

You can get the whole Package at http://pypi.python.org/pypi/pyShipping

This code is BSD Licensed.

.. image:: https://d2weczhvl823v0.cloudfront.net/hudora/pyshipping/trend.png
   :alt: Bitdeli badge
   :target: https://bitdeli.com/free

