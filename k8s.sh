#!/bin/bash

kubectl create ns ovh-pricelist
kubectl create deploy ovh-pricelist --image=tdr2d/ovh_pricelist:1.0.0 -n ovh-pricelist
kubectl expose deployment ovh-pricelist --port 80 --target-port 80 -n ovh-pricelist
kubectl create ingress ovh-pricelist-tls -n ovh-pricelist --class=default --rule="pricelist.ovh/*=ovh-pricelist:80,tls=ovh-pricelist-cert" --class nginx \
    --annotation cert-manager.io/cluster-issuer=letsencrypt