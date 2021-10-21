A simple Google Cloud Function, triggered ny a PubSub topic, that will send an email via teh MailGun service.

# Resources
- [Google Cloud Pub/Sub Triggers](https://cloud.google.com/functions/docs/calling/pubsub)

# Developer setup

## Clone this repository
```
❯ git clone git@github.com:houseman/sendmail-cloud-git
❯ cd sendmail-cloud-function
```

## Create a Python virtual environment
I recommend using [`pyenv-virtualenv`](https://github.com/pyenv/pyenv-virtualenv)
```
❯ pyenv virtualenv 3.8.9 sendmail-cloud-function
❯ pyenv local sendmail-cloud-function
❯ pip install --upgrade pip
```
or just
```
❯ python3 -m venv venv
❯ source ./venv/bin/activate.
```

## Install the package and dev requirements
```
❯ pip install -e .
❯ pip install -e ".[dev]"
```

## Install `pre-commit`
```
❯ pre-commit install
pre-commit installed at .git/hooks/pre-commit
```

## Run tests
```
❯ ./scripts/test.sh
```

# Google Cloud Platform (GCP) setup
- Login to GCP Console
- Create a new project (or select an existing one, it makes no difference)
- Your project will have to be linked to a billing account
- You will need the following GCP services enabled for your project
  - Cloud Functions  (Possibly [free](https://cloud.google.com/free/docs/gcp-free-tier/#cloud-functions))
  - Cloud Build (Possibly [free](https://cloud.google.com/free/docs/gcp-free-tier/#cloud-build))
  - Pub/Sub (Possibly [free](https://cloud.google.com/free/docs/gcp-free-tier/#pub-sub))

## Configuration
Create a file named `.env` in the `function` directory, and store credentials

```
MAILGUN_HOST=api.eu.mailgun.net
MAILGUN_DOMAIN=mg.example.net
MAILGUN_API_SENDING_KEY=4g0801ef-c9d487d3
```
## Create a pub/sub topic

See the [quickstart guide](https://cloud.google.com/pubsub/docs/quickstart-cli#create_a_topic)

> **Note:** You will have to set up a GCP project, enable the Pub/Sub API etc. See [here](https://cloud.google.com/pubsub/docs/quickstart-cli#before-you-begin)

Once GCP is configured, create a topic named `function-send-email`:
```
❯ gcloud pubsub topics create function-send-email
Created topic [projects/thirsty-sailor-290220/topics/function-send-email].
```

## Deploying the function

See the [guide](https://cloud.google.com/functions/docs/deploying/filesystem#deploy_using_the_gcloud_tool)

```
❯ gcloud functions deploy cloud_send_mail \
--source function \
--entry-point cloud_send_mail \
--runtime python38 \
--trigger-topic function-send-email \
--retry

Deploying function (may take a while - up to 2 minutes)...
```

# To view logs

    $ gcloud functions logs read cloud_send_mail
    $ gcloud logging read "log_name:projects/thirsty-sailor-290220/logs/python"


# Triggering the function
```
gcloud pubsub topics publish function-send-email --message \
'{"rcpt": "scott.houseman@gmail.com", "sender": "noreply@stockfair.net","subject": "Test message","html_content": "<h1>Test</h1>","text_content": "TEST"}'

```

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
