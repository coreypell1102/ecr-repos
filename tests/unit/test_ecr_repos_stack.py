import aws_cdk as core
import aws_cdk.assertions as assertions

from ecr_repos.ecr_repos_stack import EcrReposStack

# example tests. To run these tests, uncomment this file along with the example
# resource in ecr_repos/ecr_repos_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = EcrReposStack(app, "ecr-repos")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
