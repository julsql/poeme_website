# Poème

This is the repo of Poeme project!

It's a Django project the build a website for the project Poeme.

Poeme, it's a scholar project to generate random French poems.

In short, you select the format wanted for the poem, and it will generate a poem with the rhymes and syllable wanted.

> Website available at address: [poeme.h.minet.net](http://poeme.h.minet.net)

## Table of Contents

- [Information](#information)
- [App Structure](#app-structure)
- [Installation](#installation)
- [Deploy](#deploy)
- [Authors](#authors)

## Information

Poeme uses a database with all the words in French, from [The Lexique project](http://www.lexique.org). \
With a database of sentence of a certain number of syllabes, it will change the words with others with the same number of syllabes, with the rhymes wanted.\
You can select an existing form (Sonnet: ABBA CDDC EEF GGF) fo create a new one.

## App Structure

- [static/](poeme/main/static): The files used by the website (images, documents, css & javascript…)
- [templates/](poeme/main/templates): The html templates of the pages
- [views.py](poeme/main/views.py): the code launch when loading a page
- [poeme/](poeme/poeme): the settings files (urls, wsgi, settings) used by Django
- [manage.py](poeme/manage.py): the main file that runs the website

## Installation

> You need to have python3 and pip installed on your machine

1. Clone git repository

    ```bash
    git clone git@github.com:julsql/poeme_website.git
    ```

2. Don't forget to add the settings file in `./poeme/poeme`

3. Configure the python virtual environment

    ```bash
    pip install virtualenv
    cd poeme_website
    python3 -m venv env
    source env/bin/activate
    ```
   
4. Install the libraries

    ```bash
    pip install -r requirements.txt
   ```

5. Launch the website

    ```bash
    cd poeme
    ./manage.py runserver 
    ```
6. To leave the virtual environment
    ```bash
    deactivate
    ```

## Deploy

You need to configure your VM.

Don't forget to download git, python, apache2, pip on your VM:
    
```bash
sudo apt-get update
sudo apt-get install apache2
sudo apt-get install postgresql
sudo apt-get install python3
sudo apt-get install python3-pip
sudo apt-get install libapache2-mod-wsgi-py3
sudo apt-get install git
sudo apt-get install python3-venv
```

After installing the project as explained in [Installation](#installation)
you can configure the VM as follows:

```bash
sudo nano /etc/apache2/sites-available/myconfig.conf
```

```
<VirtualHost *:80>
    ServerName poeme.h.minet.net
    ServerAdmin admin@email.fr

    AddDefaultCharset UTF-8

    Alias /static /home/username/poeme_website/poeme/generator/static/
    <Directory /home/username/poeme_website/poeme/generator/static/>
        Require all granted
    </Directory>

    <Directory /home/username/poeme_website/poeme/poeme/>
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>

    WSGIDaemonProcess poeme_process python-home=/home/username/poeme_website/env python-path=/home/username/poeme_website/poeme
    WSGIProcessGroup poeme_process
    WSGIScriptAlias / /home/username/poeme_website/poeme/poeme/wsgi.py process-group=poeme_process

    ErrorLog ${APACHE_LOG_DIR}/error.log
    CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
```

You load the configuration and restart the apache server
```bash
sudo a2ensite myconfig.conf
sudo service apache2 restart
```

> To unload a configuration: `sudo a2dissite myconfig.conf`

## Authors

- Jul SQL