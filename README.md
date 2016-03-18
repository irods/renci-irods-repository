RENCI iRODS Repository
======================

Installing a package produced by this code adds the RENCI iRODS Repository to the host computer's list of trusted repositories.

Dependencies
------------

This code requires:

 - python 2.6+
 - fpm (sudo gem install fpm)

Build
-----

```
make
```

Running `make` will produce one datestamped package for each of the following supported packaging formats:

 - deb
 - rpm

RENCI hosts the resulting packages at https://packages.irods.org.

