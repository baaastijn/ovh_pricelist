FROM php:7.2-apache
COPY . /var/www/html/
RUN sed -i 's/memory_limit = 128M/memory_limit = 1024M/' "$PHP_INI_DIR/php.ini-production" && \
    mv "$PHP_INI_DIR/php.ini-production" "$PHP_INI_DIR/php.ini"
RUN chown -R www-data:www-data /var/www/html