#!/usr/bin/env python3
import aws_cdk as cdk
import boto3
from botocore.exceptions import NoCredentialsError

from infrastructure.pipeline import PipelineStack

#from keycloak_infra.keycloak_infra_stack import KeycloakInfraStack


app = cdk.App()

#Define possible app environments
app_envs = {
    "211125306454": {"ctx": "dev", "region": "us-east-1"},
    "123456789012": {"ctx": "prod", "region": "us-east-1"},
}

sts_client = boto3.Session().client('sts')
account = None

try:
    account = sts_client.get_caller_identity().get("Account")
except NoCredentialsError:
    print("No AWS credentials found. Please configure your credentials.")
except Exception as e:
    print("An error occurred: ", e)
    
if not account:
    print("Assuming this is being run locally and will use the dev account")
    account = next(iter(app_envs)) # Use the first account in the list

print(f"Using account: {account}")
print(f"Using environment: {app_envs[account]}")

env = cdk.Environment(account=account, region=app_envs[account]["region"])

ctx = app.node.try_get_context(app_envs[account]["ctx"])
if ctx is None:
    raise ValueError(f"Context {app_envs[account]['ctx']} not found in cdk.context.json")

pipeline = PipelineStack(
    app,
    construct_id=f"{ctx['app_name']}-Pipeline",
    ctx=ctx,
    env=env,
    stack_name=f"{ctx['app_name']}-Pipeline",
    description=f"{ctx['app_name']} Infrastructure Pipeline",
)

app.synth()
