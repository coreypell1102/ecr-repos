#!/usr/bin/env python3
import aws_cdk as cdk
import boto3
from botocore.exceptions import NoCredentialsError

from infrastructure.pipeline import PipelineStack

#from keycloak_infra.keycloak_infra_stack import KeycloakInfraStack


app = cdk.App()

#Define possible app environments
app_env = {
    "730335265357": {"ctx": "dev", "region": "us-east-1"},
    "123456789012": {"ctx": "prod", "region": "us-east-1"},
}

sts_client = boto3.Session().client("sts")
account = None

try:
    account = sts_client.get_caller_identity().get("Account")
except NoCredentialsError:
    print("No valid credentials found")
except Exception as e:
    print(f"Error: {e}")

if not account:
    print(f"Assuming this is being run locally and will use 'dev' account")
    account = next(iter(app_env))  # dev account

print(f"Account: {account}")
print(f"Using environment: {app_env[account]}")

env = cdk.Environment(account=account, region=app_env[account]["region"])

ctx = app.node.try_get_context(app_env[account]["ctx"])
if ctx is None:
    raise ValueError(f"Context for '{app_env[account]['ctx']}' not found! Check your cdk.json file.")

pipeline = PipelineStack(
    app,
    construct_id=f"{ctx['app_name']}-Pipeline",
    ctx=ctx,
    env=env,
    stack_name=f"{ctx['app_name']}-Pipeline",
    description=f"{ctx['app_name']} Infrastructure Pipeline",
)


# Add tags to the entire app (all resources created by this app)
cdk.Tags.of(pipeline).add("APPLICATION", ctx["app_name"])

app.synth()
