# Create a pub/sub topic

https://cloud.google.com/pubsub/docs/quickstart-cli#create_a_subscription

```
$ gcloud pubsub topics create function-send-email
Created topic [projects/thirsty-sailor-290220/topics/function-send-email].
```

# Deploying the function

https://cloud.google.com/functions/docs/deploying/filesystem#deploy_using_the_gcloud_tool


    $ cd function
    $ gcloud functions deploy cloud_send_mail \
    --entry-point cloud_send_mail \
    --runtime python38 \
    --trigger-topic function-send-email \
    --retry

    Deploying function (may take a while - up to 2 minutes)...⠛
    For Cloud Build Stackdriver Logs, visit: https://console.cloud.google.com/logs/viewer?project...
    Deploying function (may take a while - up to 2 minutes)...done.
    availableMemoryMb: 256
    buildId: d82ec16f-3a10-4482-bf63-dc0d5c67ee7d
    entryPoint: cloud_send_mail
    eventTrigger:
    eventType: google.pubsub.topic.publish
    failurePolicy:
        retry: {}
    resource: projects/thirsty-sailor-290220/topics/function-send-email
    service: pubsub.googleapis.com
    ingressSettings: ALLOW_ALL
    labels:
    deployment-tool: cli-gcloud
    name: projects/thirsty-sailor-290220/locations/us-central1/functions/cloud_send_mail
    runtime: python38
    serviceAccountEmail: thirsty-sailor-290220@appspot.gserviceaccount.com
    sourceUploadUrl: https://storage.googleapis.com/gcf-upload-...
    status: ACTIVE
    timeout: 60s
    updateTime: '2021-02-03T16:15:12.655Z'
    versionId: '1'


# To view logs

    $ gcloud functions logs read cloud_send_mail
    $ gcloud logging read "log_name:projects/thirsty-sailor-290220/logs/python"


# Triggering the function

    gcloud pubsub topics publish function-send-email --message YOUR_NAME

# Installing the emulator

source: https://cloud.google.com/pubsub/docs/emulator

    $ sudo apt install openjdk-8-jre
    $ gcloud components install pubsub-emulator
    $ gcloud components update

    $ gcloud beta emulators pubsub start --project=thirsty-sailor-290220
    $ sudo ufw allow from any to any port 8941 proto tcp

# Setting environment variables

If your application and the emulator run on the same machine, you can set the environment variables automatically:

    $ $(gcloud beta emulators pubsub env-init)
    $ export GOOGLE_APPLICATION_CREDENTIALS="/home/scott/.google/keys/thirsty-sailor-290220-a9e3e7013c5c.json"

    $ cd ~/workspace/
    $ git clone https://github.com/googleapis/python-pubsub.git
    $ cd python-pubsub/
    $ pyenv virtualenv 3.8.6 python-pubsub
    $ pyenv local python-pubsub
    $ pip install google-cloud-pubsub
    $ cd samples/snippets/
    $ python publisher.py thirsty-sailor-290220 create function-send-email

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
