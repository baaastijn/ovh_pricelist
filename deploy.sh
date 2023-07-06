#!/bin/bash

VERSION=2.1.0

# Docker build
docker build -t tdr2d/ovh_pricelist:${VERSION} .
docker push tdr2d/ovh_pricelist:${VERSION}

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
kubectl create deploy ovh-pricelist --image=tdr2d/ovh_pricelist:${VERSION} -n ovh-pricelist
kubectl expose deployment ovh-pricelist --port 80 --target-port 80 -n ovh-pricelist
kubectl create ingress ovh-pricelist-tls -n ovh-pricelist --class=default --rule="pricelist.ovh/*=ovh-pricelist:80,tls=ovh-pricelist-cert" --class nginx \
    --annotation cert-manager.io/cluster-issuer=letsencrypt


# K8S Cronjob for computing plans
docker build -t tdr2d/ovh_pricelist:${VERSION}-job -f Dockerfile-job .
docker push tdr2d/ovh_pricelist:${VERSION}job
# test it
docker run -it --rm \
    -e S3_BUCKET=${S3_BUCKET} \
    -e S3_ACCESS_KEY_ID=${S3_ACCESS_KEY_ID} \
    -e S3_SECRET_ACCESS_KEY=${S3_SECRET_ACCESS_KEY} \
    tdr2d/ovh_pricelist:${VERSION}-job env && python3 compute_plans.py
# deploy it
kubectl apply -f jobs/cronjob.yml