FROM nginx:stable-alpine3.17-slim
COPY . /usr/share/nginx/html
RUN sed -i 's/memory_limit = 128M/memory_limit = 1024M/' "$PHP_INI_DIR/php.ini-production" && \
    mv "$PHP_INI_DIR/php.ini-production" "$PHP_INI_DIR/php.ini"
RUN chown -R www-data:www-data /var/www/html