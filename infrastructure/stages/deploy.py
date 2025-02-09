import aws_cdk as cdk

from infrastructure.stacks.ecr_repos import EcrReposStack

class DeployStage(cdk.stage):
    def __init__(self, scope, id, ctx, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create the ECR repos stack
        EcrReposStack(
           self,
           construct_id=f"{ctx['app_name']}-ecr",
           ctx=ctx,
           description=f"{ctx['app_name']} managed ecr repos",
           stack_name=f"{ctx['app_name']}-ecr",
        )