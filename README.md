# Deploying the function

    $ cd function
    $ gcloud functions deploy salepen_send_mail \
    --runtime python37 \
    --trigger-topic salepen-send-welcome-email \
    --retry

    Deploying function (may take a while - up to 2 minutes)...⠛                                                                                                                                                       
    For Cloud Build Stackdriver Logs, visit: https://console.cloud.google.com/logs/viewer?project=sonic-signifier-298020&advancedFilter=resource.type%3Dbuild%0Aresource.labels.build_id%3Da33c7ff8-ac5d-4530-9573-01fc27559e2a%0AlogName%3Dprojects%2Fsonic-signifier-298020%2Flogs%2Fcloudbuild
    Deploying function (may take a while - up to 2 minutes)...done.                                                                                                                                                   
    availableMemoryMb: 256
    buildId: a33c7ff8-ac5d-4530-9573-01fc27559e2a
    entryPoint: salepen_send_mail
    eventTrigger:
    eventType: google.pubsub.topic.publish
    failurePolicy: {}
    resource: projects/sonic-signifier-298020/topics/salepen-send-welcome-email
    service: pubsub.googleapis.com
    ingressSettings: ALLOW_ALL
    labels:
    deployment-tool: cli-gcloud
    name: projects/sonic-signifier-298020/locations/us-central1/functions/salepen_send_mail
    runtime: python37
    serviceAccountEmail: sonic-signifier-298020@appspot.gserviceaccount.com
    sourceUploadUrl: https://storage.googleapis.com/gcf-upload-us-central1-545a3224-aa4c-4233-bd2c-a6b9af707d49/9208f712-a47f-4bb1-991e-f3c10d439b71.zip?GoogleAccessId=service-876923987677@gcf-admin-robot.iam.gserviceaccount.com&Expires=1610037848&Signature=xk6hzcTcZ1BU8l%2BQRQFXr60uKoHL5GKtVtPOoIXySgMXJiqPbctP4N48Oc0d9xLfg27xQtaFQsKd0BIki9o%2BmCnF%2FJTwzYJz2xjQcLxVmO051bIqCXz8696j%2B%2B2KXogD8hmnfHZqiQ%2FbX%2FHqCwheziUImAtZHGwv3P4R6bwrRuFQgrLrHM9E%2BL%2BKWVMX3kMQFI8RJn%2F14KPmvyT6rSCYr3hfgpJ8cexu1OoOdNCJdmdgwVj2F82f%2FDa4pvhzSuwz4iqM88NjbZK6pKBOLkX3qRlcIzpFt7U%2FLSdtwKyze7oxKfQWNK7dOdK2MPU4NjihZxERdCatXz0jLUuHU%2Fm9RQ%3D%3D
    status: ACTIVE
    timeout: 60s
    updateTime: '2021-01-07T16:15:15.096Z'
    versionId: '2'

# To view logs

    $ gcloud functions logs read salepen_send_mail
    $ gcloud logging read "log_name:projects/sonic-signifier-298020/logs/python"


# Triggering the function

    gcloud pubsub topics publish salepen-send-welcome-email --message YOUR_NAME

# Installing the emulator

source: https://cloud.google.com/pubsub/docs/emulator

    $ sudo apt install openjdk-8-jre
    $ gcloud components install pubsub-emulator
    $ gcloud components update

    $ gcloud beta emulators pubsub start --project=sonic-signifier-298020
    $ sudo ufw allow from any to any port 8941 proto tcp

# Setting environment variables

If your application and the emulator run on the same machine, you can set the environment variables automatically:

    $ $(gcloud beta emulators pubsub env-init)
    $ export GOOGLE_APPLICATION_CREDENTIALS="/home/scott/.google/keys/sonic-signifier-298020-a9e3e7013c5c.json"
    
    $ cd ~/workspace/
    $ git clone https://github.com/googleapis/python-pubsub.git
    $ cd python-pubsub/
    $ pyenv virtualenv 3.8.6 python-pubsub
    $ pyenv local python-pubsub
    $ pip install google-cloud-pubsub
    $ cd samples/snippets/
    $ python publisher.py sonic-signifier-298020 create salepen-send-welcome-email

# Return to using cloud

    $ unset PUBSUB_EMULATOR_HOST

# use secrets

    $ gcloud services enable secretmanager.googleapis.com cloudfunctions.googleapis.com
    $ echo -n "****************-******-******" | \
    gcloud secrets create mailgun-api-sending-key \
      --data-file=- \
      --replication-policy automatic
    $ gcloud secrets add-iam-policy-binding mailgun-api-sending-key \
    --role roles/secretmanager.secretAccessor \
    --member serviceAccount:876923987677-compute@developer.gserviceaccount.com

    $ gcloud secrets versions access 1 --secret="mailgun-api-sending-key"


# pytest

    $ export PYTHONPATH=.
    $ pytest --import-mode importlib -vv

