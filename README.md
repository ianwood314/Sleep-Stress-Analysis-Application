# Sleep Analysis Application

Provide a basic description of the repository

## Table of Contents

[Overview](#overview) <br >
[Description of Data](#description-of-data) <br >
[Scripts](#scripts) <br >
[How to Build Your Own Image](#how-to-build-your-own-image) <br >
[Deployment of the Application to Kubernetes](#deployment-of-the-application-to-kubernetes) <br >
[How to Interact with the Application](#how-to-interact-with-the-application) <br >
[Interpret the Results](#interpret-the-results) <br >
[Test the Software System using Pytest](#test-the-software-system-using-pytest) <br >

## Overview



## Description of Data

The data being analyzed in this application is data collected by a 

Provide a basic description of the data, the variables, the units, and where the data was sourced.

## Scripts
- `flask_api.py`:
- `jobs.py`:
- `worker.py`:

## How to Build Your Own Image


## Deployment of the Application to Kubernetes

Now that we have created the Meteorite Landings Data Application found [here](https://github.com/ianwood314/homeworks/tree/main/homework05),
we can to deploy the application to Kubernetes to improve the usability and scalability of the application.

### Deploy Redis Server to Kubernetes
1. Deploy the Redis Deployment
    - `kubectl apply -f app-prod-db-deployment.yml`
2. Deploy the Redis Persistant Volume Claim
    - `kubectl apply -f app-prod-db-pvc.yml`
3. Deploy the Redis Service
    - `kubectl apply -f app-prod-db-service.yml`

### Deploy Flask App to Kubernetes
1. Deploy the Flask Deployment
    - `kubectl apply -f app-prod-api-deployment.yml`
2. Deploy the Flask Service
    - `kubectl apply -f app-prod-api-service.yml`

To see a list of all of the deployments and the pods created from those deployments, type 
`kubectl get all` in the terminal.

## How to Interact with the Application


## Interpret the Results


## Test the Software System using Pytest

