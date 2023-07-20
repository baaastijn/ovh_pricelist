#!/bin/sh

jinja templates/index.html -o static/index.html
jinja templates/private-cloud.html -o static/private-cloud.html