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

## Install requirements
**Note** that Cloud Functions requires the `requirements.txt` file be in the same directory that contains `main.py`

```
❯ pip install -r function/requirements.txt
❯ pip install -r requirements-dev.txt
```

## Install `pre-commit`
```
❯ pre-commit install
pre-commit installed at .git/hooks/pre-commit
```

### VSCode setup
Some useful configurations. Edit these into your `.vscode/settings.json` file.

#### Add the `function` directory to path:
This will enable Pylance to resolve import paths.
```json
{
    "python.analysis.extraPaths": [
        "function"
    ]
}
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
### Environment variables
Certain environment variables must be set for configuration of the Mailgun API.
Cloud Functions allows [various methods](https://cloud.google.com/functions/docs/configuring/env-var#using_runtime_environment_variables) to set environment variable values.
Create a file named `.env.yaml` in the root directory, and store credentials, for example:

```yaml
MAILGUN_HOST: api.mailgun.net
MAILGUN_DOMAIN: mg.example.net
MAILGUN_API_SENDING_KEY: your-mailgun-api-key
```

### Confirm credentials work
```
❯ curl --silent --user 'api:MAILGUN_API_SENDING_KEY' \
    https://${MAILGUN_HOST}/v3/${MAILGUN_DOMAIN}/messages \
    --form from='Excited User <mailgun@example.net>' \
    --form to=me@mail.com \
    --form subject='Hello' \
    --form text='Testing some Mailgun awesomeness!'

```
### Create a Schema
A schema is a format that messages must follow, creating a contract between publisher and subscriber that Pub/Sub will enforce.
See Documentation: [Creating and managing schemas ](https://cloud.google.com/pubsub/docs/schemas)
Create a schema defined in Protocol Buffer format:
```
❯ gcloud pubsub schemas create MAIL_MESSAGE \
        --type=PROTOCOL_BUFFER \
        --definition='syntax = "proto3";

message MailMessage {
  string recipient = 1;
  string sender = 2;
  string subject = 3;
  string html_content = 4;
  string text_content = 5;
}'

Created schema [MAIL_MESSAGE].
❯ gcloud pubsub schemas list
NAME          TYPE             DEFINITION
MAIL_MESSAGE  PROTOCOL_BUFFER
```
## Create a pub/sub topic

See the [quickstart guide](https://cloud.google.com/pubsub/docs/quickstart-cli#create_a_topic)

> **Note:** You will have to set up a GCP project, enable the Pub/Sub API etc. See [here](https://cloud.google.com/pubsub/docs/quickstart-cli#before-you-begin)

Once GCP is configured, create a topic named `send-mail-message`, with the defined schema:
```
❯ gcloud pubsub topics create send-mail-message \
--message-encoding=json \
--schema=MAIL_MESSAGE

Created topic [projects/thirsty-sailor-290220/topics/send-mail-message].
```

## Deploying the function

See the [guide](https://cloud.google.com/functions/docs/deploying/filesystem#deploy_using_the_gcloud_tool)

```
❯ gcloud functions deploy cloud_send_mail \
--source function \
--entry-point cloud_send_mail \
--runtime python38 \
--trigger-topic send-mail-message \
--env-vars-file .env.yaml \
--retry

Deploying function (may take a while - up to 2 minutes)...
```

### Update deployment
```
gcloud functions deploy cloud_send_mail --update-env-vars MAILGUN_API_SENDING_KEY=bar
```

# Triggering the function
```
❯ gcloud pubsub topics publish send-mail-message --message \
'{
    "recipient": "scott.houseman@gmail.com",
    "sender": "noreply@stockfair.net",
    "subject": "Test message",
    "html_content": "<h1>Test</h1>",
    "text_content": "TEST"
}'

```

# To view logs
```
❯ gcloud functions logs read cloud_send_mail --sort-by=TIME_UTC --limit=10
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
    $ python publisher.py thirsty-sailor-290220 create send-mail-message

# Return to using cloud

    $ unset PUBSUB_EMULATOR_HOST
