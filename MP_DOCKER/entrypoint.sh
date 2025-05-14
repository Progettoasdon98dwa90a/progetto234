#!/bin/bash

# Start MySQL temporarily to initialize the database
service mysql start

# Check if database is already initialized
if [ ! -d /var/lib/mysql/masterplan ]; then
    # Secure MySQL installation
    mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'rootpassword';"
    mysql -uroot -prootpassword -e "CREATE DATABASE IF NOT EXISTS masterplan;"
    mysql -uroot -prootpassword -e "CREATE USER 'masterplan'@'%' IDENTIFIED BY 'PASSWORD';"
    mysql -uroot -prootpassword -e "GRANT ALL PRIVILEGES ON masterplan.* TO 'masterplan'@'%';"
    mysql -uroot -prootpassword -e "FLUSH PRIVILEGES;"
fi

# Stop MySQL to allow Supervisor to start it
service mysql stop

# Configure MASTERPLAN (correct path)
cp /var/www/html/masterplan/conf.php.example /var/www/html/masterplan/conf.php

# Configure phpMyAdmin
if [ ! -f /var/www/html/phpmyadmin/config.inc.php ]; then
    cp /var/www/html/phpmyadmin/config.sample.inc.php /var/www/html/phpmyadmin/config.inc.php
    BLOWFISH_SECRET=$(openssl rand -base64 32)
    sed -i "s|\$cfg\['blowfish_secret'\] = ''|\$cfg\['blowfish_secret'\] = '${BLOWFISH_SECRET}'|" /var/www/html/phpmyadmin/config.inc.php
    echo "\$cfg['Servers'][1]['host'] = '127.0.0.1';" >> /var/www/html/phpmyadmin/config.inc.php
    echo "\$cfg['Servers'][1]['user'] = 'root';" >> /var/www/html/phpmyadmin/config.inc.php
    echo "\$cfg['Servers'][1]['password'] = 'rootpassword';" >> /var/www/html/phpmyadmin/config.inc.php
    echo "\$cfg['Servers'][1]['AllowNoPassword'] = false;" >> /var/www/html/phpmyadmin/config.inc.php
fi

# Start services through Supervisor
exec /usr/bin/supervisord