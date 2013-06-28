#Portcullis

Open source online data collection for sensor networks.

Why is Portcullis cool?

Portcullis is an application designed to centralize all kinds of data that can be collected from network connected sensor devices. Devices send data to a Portcullis server through an HTTP-based API. Once on the server, the data can be analyzed and visualized using a variety of fancy techiques.

##Software Prerequisites

- Python 2.7
- Django 1.4
- Dajaxice 0.5.5
- git
- gitPython

Database (one of the following):

- postgres with python-psycopg2
- sqlite3

Webserver:
 
- apache2 with libapache2-mod-wsgi
	

##Installation

Ubuntu or Debian users can usually install the prerequisites by executing the following.
```
$ sudo apt-get install python2.7 postgresql python-psycopg2 apache2 libapache-mod-wsgi python-setuptools git
$ sudo easy_install django
$ sudo easy_install django-dajaxice
$ sudo easy_install gitpython
```

Make sure to edit the database connection info in the settings.py

Run the setup script to create the database tables needed by Portcullis and pre-populate it with some demo data.
`portcullis/$ ./manage.py setup`

Run the dev server, which attaches to port 8000 by default
`portcullis/$ ./manage.py runserver`

or

`portcullis/$ ./manage.py runserver ip:port`


##Optional Setup in Apache

*For Debian/Ubuntu users.*

Make sure to edit portcullis_apache.conf to reflect your install location.
```
portcullis/$ sudo cp portcullis_apache.conf /etc/apache2/conf.d/
portcullis/$ ./manage.py collectstatic
portcullis/$ sudo service apache2 restart
```


##Users

There are a few Users that get loaded into the system once installation is complete for demonstration purposes.

- "auth@example.com"
- "normal@example.com"

The password for both are 'password'

"auth@example.com" is a super user and has privileges for everything in the web application while "normal@example.com" is not.
The normal user is restricted to its own data in the system.


##Sponsored by

Visgence, Inc.  
www.visgence.com  
portcullis@visgence.com  


##License
This work is licensed under the Creative Commons Attribution-ShareAlike 3.0 United States License. To view a copy of this license, visit http://creativecommons.org/licenses/by-sa/3.0/us/ or send a letter to Creative Commons, 444 Castro Street, Suite 900, Mountain View, California, 94041, USA.
