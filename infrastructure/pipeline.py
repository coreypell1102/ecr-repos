import aws_cdk as cdk
from aws_cdk import (
    Stack,
    aws_logs as logs,
    aws_s3 as s3,
    aws_codebuild as codebuild,
)
from constructs import Construct

from infrastructure.stages.deploy import DeployStage

class PipelineStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, ctx, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        bucket = s3.Bucket.from_bucket_name(
            self,
            f"artifacts_bucket",
            ctx["artifact_bucket"]
        )
        
        # Assume github token has been set in SSM
        oauth = cdk.SecretValue.secrets_manager(
            secret_id=ctx["github_token_secret"],
            json_field=(
                ctx["github_token_secret_key"]
                if ctx["github_token_secret_key"].strip()
                else None
            ),
        )
        
        # Create the pipeline
        pipeline = cdk.pipelines.CodePipeline(
            self,
            id=ctx["app_name"] + "Pipeline",
            artifact_bucket=bucket,
            pipeline_name=self.stack_name,
            self_mutation=True,
            synth=cdk.pipelines.ShellStep(
                id="Synth",
                input=cdk.pipelines.CodePipelineSource.git_hub(
                    repo_string=ctx["infra_pipeline_repo"],
                    branch=ctx["infra_pipeline_branch"],
                    authentication=oauth,
                ),
                commands=[
                    "npm install -g aws-cdk cdk-assume-role-credential-plugin",
                    "pip3 install --upgrade pip && pip3 install -r requirements.txt",
                    "cdk synth -v --output cdk.out",
                ],
                primary_output_directory="cdk.out",
            ),
            synth_code_build_defaults=cdk.pipelines.CodeBuildOptions(
                logging=codebuild.LoggingOptions(
                    cloud_watch=codebuild.CloudWatchLoggingOptions(
                        enabled=True,
                        log_group=logs.LogGroup(
                            self,
                            id=f"{ctx['app_name']}-Pipeline-Synth-Logs",
                            log_group_name=f"codebuild/{ctx['app_name']}/PipelineSynth",
                            retention=logs.RetentionDays.ONE_MONTH,
                            removal_policy=cdk.RemovalPolicy.DESTROY,
                        ),
                    )
                )
            ),
        )
        
        deployStage = DeployStage(
            scope=self,
            id=f"{ctx['app_name']}-DeployStage",
            ctx=ctx,
            env=kwargs["env"],
            stage_name=f"{ctx['app_name']}-Deploy",
        )
        
        pipeline.add_stage(deployStage)
        
        pipeline.build_pipeline()