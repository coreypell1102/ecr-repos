import aws_cdk as cdk
from aws_cdk import(
    Stack,
    aws_ecr as ecr,
)
from constructs import Construct

class EcrReposStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, ctx, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        for repo in ctx["repos"]:
            
            ecr_repo = ecr.Repository(
                self,
                id=f"{repo['name']}",
                image_scan_on_push=True,
                repository_name=f"{repo['name']}",
                removal_policy=cdk.RemovalPolicy.DESTROY,
                empty_on_delete=True,
                lifecycle_rules=[
                    ecr.LifecycleRule(
                        description="Keep last 10 images",
                        max_image_count=10,
                    )
                ]
            )
