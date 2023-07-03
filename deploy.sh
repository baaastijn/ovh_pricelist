#!/bin/bash


# Docker build
docker build . -t tdr2d/ovh_pricelist:2.1.0
docker push tdr2d/ovh_pricelist:2.1.0

# S3 configuration

cat << EOF > cors.json
{
    "CORSRules": [
         {
             "AllowedHeaders": ["Authorization"],
             "AllowedMethods": ["GET", "HEAD"],
             "AllowedOrigins": ["*"],
             "ExposeHeaders": ["Access-Control-Allow-Origin"]
         }
    ]
}
EOF
aws s3api put-bucket-cors --bucket share --cors-configuration file://cors.json --region gra --endpoint-url=https://s3.gra.io.cloud.ovh.net/

# K8s Configuration 

kubectl create ns ovh-pricelist
kubectl create deploy ovh-pricelist --image=tdr2d/ovh_pricelist:1.0.0 -n ovh-pricelist
kubectl expose deployment ovh-pricelist --port 80 --target-port 80 -n ovh-pricelist
kubectl create ingress ovh-pricelist-tls -n ovh-pricelist --class=default --rule="pricelist.ovh/*=ovh-pricelist:80,tls=ovh-pricelist-cert" --class nginx \
    --annotation cert-manager.io/cluster-issuer=letsencrypt