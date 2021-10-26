A simple Google Cloud Function, triggered ny a PubSub topic, that will send an email via the [Mailgun](https://www.mailgun.com/) service.

Sending email asynchronously through a third-party provider is a pretty good use case for distributed event streaming through Google Cloud Pub/Sub.
This is just a scratchpad repo to demonstrate to myself and others how it can be done using a Python 3.8 Cloud Function.

The content below is mostly derived from the Google Cloud Platform (GCP) documentation.

# Resources
- [Google Cloud Functions Pub/Sub Triggers](https://cloud.google.com/functions/docs/calling/pubsub)

# Developer setup

## Clone this repository
```
❯ git clone git@github.com:houseman/sendmail-cloud-git
❯ cd sendmail-cloud-function
```
### Structure
```
❯ tree .
.
├── README.md
├── function
│   ├── __init__.py
│   ├── config.py
│   ├── controllers.py
│   ├── exceptions.py
│   ├── integrations.py
│   ├── main.py                 <-- Function entry point
│   ├── requirements.txt        <-- Function dependency list meta file
│   ├── responses.py
│   └── schemas.py
├── requirements-dev.txt        <-- Dev environment dependency list meta file
├── schema.proto                <-- Pub/Sub message schema definition
├── scripts
│   └── test.sh
├── tests
│   ├── __init__.py
│   ├── conftest.py
│   ├── requirements-test.txt   <-- Test pack dependency list meta file
│   ├── test_config.py
│   ├── test_controller.py
│   ├── test_exceptions.py
│   ├── test_integrations.py
│   └── test_main.py
└── version
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
**Note** that Cloud Functions specifies the `requirements.txt` file be in the same directory that contains `main.py`
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
These should pass with 100% coverage.
```
❯ ./scripts/test.sh
```
# Mailgun
You will need to
- [Create a Mailgun account](https://signup.mailgun.com/new/signup)
- [Add your domain to Mailgun](https://help.mailgun.com/hc/en-us/articles/203637190-How-Do-I-Add-or-Delete-a-Domain-)
- [Verify your domain](https://help.mailgun.com/hc/en-us/articles/360026833053-Domain-Verification-Walkthrough)
- [Retrieve your Mailgun API sending key](https://help.mailgun.com/hc/en-us/articles/203380100-Where-Can-I-Find-My-API-Key-and-SMTP-Credentials-)

## Confirm credentials work
Once done, you can test that sending works:
```
❯ curl --silent --user 'api:MAILGUN_API_SENDING_KEY' \
    https://${MAILGUN_HOST}/v3/${MAILGUN_DOMAIN}/messages \
    --form from='Excited User <mailgun@example.net>' \
    --form to=me@mail.com \
    --form subject='Hello' \
    --form text='Testing some Mailgun awesomeness!'
```

# Google Cloud Platform (GCP) setup
Some configuration is required in GCP.
- Login to GCP Console
- Create a new project (or select an existing one, it makes no difference really)
- **Note:** your chosen project must be linked to a billing account
- You will need the following GCP services enabled for your project
  - Cloud Functions  (Possibly [free](https://cloud.google.com/free/docs/gcp-free-tier/#cloud-functions))
  - Cloud Build (Possibly [free](https://cloud.google.com/free/docs/gcp-free-tier/#cloud-build))
  - Pub/Sub (Possibly [free](https://cloud.google.com/free/docs/gcp-free-tier/#pub-sub))

## Configuration
### Environment variables
Certain environment variables must be set for configuration of the Mailgun API at runtime.

Cloud Functions allows [various methods](https://cloud.google.com/functions/docs/configuring/env-var#using_runtime_environment_variables) to set environment variable values.

Create a file named `.env.yaml` in the root directory, and store credentials, for example:
```yaml
MAILGUN_HOST: api.mailgun.net
MAILGUN_DOMAIN: mg.example.net
MAILGUN_API_SENDING_KEY: your-mailgun-api-send-key
```
### Create a Schema
A schema is a format that messages must follow, creating a contract between publisher and subscriber that Pub/Sub will enforce.

See Documentation: [Creating and managing schemas ](https://cloud.google.com/pubsub/docs/schemas)

Create a schema with ID `MAIL_MESSAGE`, defined in Protocol Buffer 3 format:
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

Once GCP is configured, create a topic named `send-mail-message`, with the defined schema:
```
❯ gcloud pubsub topics create send-mail-message \
--message-encoding=json \
--schema=MAIL_MESSAGE

Created topic [projects/thirsty-sailor-290220/topics/send-mail-message].
```
## Setting up authentication
Configure auth for your local producer to connect to the Pub/Sub service. See [documentation](https://cloud.google.com/pubsub/docs/reference/libraries#setting_up_authentication)
```
❯ ACCOUNT_NAME=send-mail-message
❯ PROJECT_ID=$(gcloud config get-value core/project)
❯ gcloud iam service-accounts create $ACCOUNT_NAME
❯ gcloud projects add-iam-policy-binding ${PROJECT_ID} \
--member="serviceAccount:${ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
--role="roles/owner"
❯ gcloud iam service-accounts keys create send-mail-message.json \
--iam-account=${ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com
❯ export GOOGLE_APPLICATION_CREDENTIALS="${ACCOUNT_NAME}"
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
Update the deployment to change environment variable values.
```
gcloud functions deploy cloud_send_mail --update-env-vars MAILGUN_API_SENDING_KEY=bar
```
# Triggering the function
Publish a message to trigger the function and send an email
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
# Test using the producer
A test script `producer/send.py` can be used to create a Pub/Sub message in the defined topic, triggering the email send.

## Configure the producer script
- Create a file named `.env` in the `producer` directory
- This file must contain the following values
```
GCLOUD_PROJECT_ID=gcp-project-name
PUBSUB_TOPIC_ID=pubsub-topic-name
FROM_ADDR=noreply@example.com
```
## Set up authentication
> See [documentation](https://cloud.google.com/pubsub/docs/reference/libraries#setting_up_authentication)
1.Create a service account named `pubsub-email-function`
```
❯ SERVICE_ACCOUNT_NAME='pubsub-email-function'
❯ gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME
Created service account [pubsub-email-function].

```
2. Grant permissions to the service account.
```
❯ PROJECT_ID=$(gcloud config get-value core/project)
gcloud projects add-iam-policy-binding $PROJECT_ID \
--member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
--role="roles/owner"

```
3. Generate a local key file
```
KEY_FILE_PATH=~/.google/keys/${PROJECT_ID}-${SERVICE_ACCOUNT_NAME}.json
gcloud iam service-accounts keys create $KEY_FILE_PATH \
--iam-account=$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com
```
4. Provide authentication credentials to your application code by setting the environment variable
```
export GOOGLE_APPLICATION_CREDENTIALS=$KEY_FILE_PATH
```

## Run a test
Once the above configuration is in place, run a test like:
```
❯ python producer/send.py \
--to test@example.com \
--subject "Test from CLI producer" \
--message "<html>
  <head>
    <title>Test email</title>
  </head>
  <body>
    <h1>Test message</h1>
    <h2>Send from the CLI</h2>
    <p><strong>Lorem Ipsum</strong> is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.</p>
  </body>
</html>"
```
