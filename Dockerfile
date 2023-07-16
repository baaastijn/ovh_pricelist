FROM nginx:stable-alpine3.17-slim
COPY ./static/* /usr/share/nginx/html