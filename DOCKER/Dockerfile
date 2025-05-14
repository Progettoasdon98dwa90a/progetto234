# Use a lightweight Ubuntu base image
FROM ubuntu:20.04

# Install necessary packages
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    apache2 \
    php \
    php-mysql \
    php-curl \
    php-json \
    php-mbstring \
    php-xml \
    php-zip \
    mysql-server \
    supervisor \
    git \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Delete existing masterplan directory (if any)
RUN rm -rf /var/www/html

# Add this section before the "Clone MASTERPLAN repository" step
# Configure MySQL
RUN mkdir -p /etc/mysql/conf.d
COPY mysql.cnf /etc/mysql/conf.d/mysql.cnf

# Copy local the MASTERPLAN repository
COPY MASTERPLAN/ /var/www/html/masterplan/

# Install PHP dependencies
RUN cd /var/www/html

# Install phpMyAdmin
RUN mkdir -p /var/www/html/phpmyadmin \
    && curl -sSL https://www.phpmyadmin.net/downloads/phpMyAdmin-latest-all-languages.tar.gz -o phpmyadmin.tar.gz \
    && tar -xzf phpmyadmin.tar.gz -C /var/www/html/phpmyadmin --strip-components 1 \
    && rm phpmyadmin.tar.gz

# Set file permissions
RUN chown -R www-data:www-data /var/www/html/masterplan \
    && chmod -R 755 /var/www/html/masterplan \
    && chown -R www-data:www-data /var/www/html/phpmyadmin \
    && chmod -R 755 /var/www/html/phpmyadmin

# Enable Apache rewrite module
RUN a2enmod rewrite

# Copy configuration files
COPY apache-config.conf /etc/apache2/sites-available/000-default.conf
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose ports
EXPOSE 80 3306

# MySQL data volume
VOLUME /var/lib/mysql

# Start services
ENTRYPOINT ["/entrypoint.sh"]