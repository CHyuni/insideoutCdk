from aws_cdk import (
    aws_s3 as s3,
    aws_cognito as cognito,
    Stack,
    aws_amplify_alpha as amplify,
    RemovalPolicy,
    aws_codebuild as codebuild,
    SecretValue,
    custom_resources as cr,
    aws_lambda as lambda_,
    aws_apigateway as apigateway
)
from constructs import Construct

class MyCdkStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        s3_bucket = s3.Bucket(self, "Audiofile",
                             bucket_name="audio-file-chyuni-20240608",
                             versioned=True,
                             removal_policy=RemovalPolicy.DESTROY,
                             auto_delete_objects=True)
        
        user_pool = cognito.UserPool(self, "MyUserPool",
                                    user_pool_name="my-cdk-user",
                                    self_sign_up_enabled=True,
                                    sign_in_aliases=cognito.SignInAliases(username=True, email=True))
        
        user_pool_client = cognito.UserPoolClient(
            self, "AmplifyCDKUserPoolClient",
            user_pool=user_pool, generate_secret=False
        )

        identity_pool = cognito.CfnIdentityPool(self, "AmplifyCDKIdentityPool",
            allow_unauthenticated_identities=True,
            cognito_identity_providers=[
                cognito.CfnIdentityPool.CognitoIdentityProviderProperty(
                    client_id=user_pool_client.user_pool_client_id,
                    provider_name=user_pool.user_pool_provider_name,
                )
            ]
        )

        github_token = SecretValue.secrets_manager("github-token", json_field="github-token")

        amplify_app = amplify.App(self, "MyApp",
                                source_code_provider=amplify.GitHubSourceCodeProvider(
                                    owner="CHyuni",
                                    repository="test_next",
                                    oauth_token=github_token,
                                ),
                                build_spec=codebuild.BuildSpec.from_object({
                                    "version": "1",
                                    "frontend": {
                                        "phases": {
                                            "preBuild": {
                                                "commands": [
                                                    "npm ci"
                                                ]
                                            },
                                            "build": {
                                                "commands": [
                                                    "npm install",
                                                    "npm run build"
                                                ]
                                            }
                                        },
                                        "artifacts": {
                                            "baseDirectory": ".next",
                                            "files": [
                                                "**/*"
                                            ]
                                        },
                                        "cache": {
                                            "paths": [
                                                "node_modules/**/*"
                                            ]
                                        }
                                    }
                                }),
                                auto_branch_creation=amplify.AutoBranchCreation(
                                    patterns=["feature/*", "test/*"]),
                                auto_branch_deletion=True)

        cfn_app = amplify_app.node.default_child
        cfn_app.platform = "WEB_COMPUTE"
        
        main_branch = amplify_app.add_branch("main", stage="PRODUCTION")

        cfn_branch = main_branch.node.default_child
        cfn_branch.framework = "Next.js - SSR"
        
        s3_bucket.grant_read_write(amplify_app)
        user_pool.grant(amplify_app, "cognito-idp:AdminCreateUser", "cognito-idp:ListUsers")

        fn = lambda_.Function(self, "MyFunction",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="index.handler",
            code=lambda_.Code.from_inline("""
def handler(event, context):
    result = 1 + 2
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT'
        },
        'body': str(result)
    }
""")
        )
        
        api = apigateway.RestApi(self, "MyApi",
            rest_api_name="test gateway",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=["GET", "POST", "OPTIONS", "PUT"],
                allow_headers=["Content-Type", "X-Amz-Date", "Authorization", "X-Api-Key"],
            )
        )

        get_integration = apigateway.LambdaIntegration(fn)
        resource = api.root.add_resource("test")
        resource.add_method("GET", get_integration)

        amplify_app.add_environment("NEXT_PUBLIC_AWS_USER_FILES_S3_BUCKET", s3_bucket.bucket_name)
        amplify_app.add_environment("NEXT_PUBLIC_AWS_PROJECT_REGION", self.region)
        amplify_app.add_environment("NEXT_PUBLIC_AWS_USER_POOLS_ID", user_pool.user_pool_id)
        amplify_app.add_environment("NEXT_PUBLIC_AWS_USER_POOLS_WEB_CLIENT_ID", user_pool_client.user_pool_client_id)
        amplify_app.add_environment("NEXT_PUBLIC_AWS_COGNITO_IDENTITY_POOL_ID", identity_pool.ref)
        amplify_app.add_environment("NEXT_PUBLIC_API_URL", api.url)

        build_trigger = cr.AwsCustomResource(self, 'triggerAppBuild',
            on_create=cr.AwsSdkCall(
                service="Amplify",
                action="startJob",
                parameters={
                    "appId": amplify_app.app_id,
                    "branchName": main_branch.branch_name,
                    "jobType": "RELEASE",
                    "jobReason": "Auto Start Build"
                },
                physical_resource_id=cr.PhysicalResourceId.of('app-build-trigger')
            ),
            policy=cr.AwsCustomResourcePolicy.from_sdk_calls(
                resources=cr.AwsCustomResourcePolicy.ANY_RESOURCE
            )
        )
