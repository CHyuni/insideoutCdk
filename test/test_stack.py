from aws_cdk import (
    aws_s3 as s3,
    Stack,
    aws_amplify_alpha as amplify,
    RemovalPolicy,
    SecretValue,
    aws_lambda as lambda_,
    aws_apigateway as apigateway,
    aws_dynamodb as dynamodb,
    custom_resources as cr,
    aws_lambda_event_sources as lambda_event_sources
)
from constructs import Construct

class TestStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        s3_play = s3.Bucket(
            self, "playBucket",
            bucket_name="audio-play-myeochoi",
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            public_read_access=True,
            block_public_access=s3.BlockPublicAccess(
                block_public_acls=False,
                block_public_policy=False,
                ignore_public_acls=False,
                restrict_public_buckets=False
            ),
            cors=[s3.CorsRule(
                allowed_methods=[
                    s3.HttpMethods.GET,
                    s3.HttpMethods.POST,
                    s3.HttpMethods.PUT,
                    s3.HttpMethods.DELETE,
                    s3.HttpMethods.HEAD,
                ],
                allowed_origins=["*"],  # 실제 운영 환경에서는 특정 도메인으로 제한하는 것이 좋습니다
                allowed_headers=["*"],
                max_age=3000
            )]
        )

        s3_dummy = s3.Bucket(
            self, "dummyBucket",
            bucket_name="audio-dummy-myeochoi",
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            cors=[s3.CorsRule(
                allowed_methods=[
                    s3.HttpMethods.GET,
                    s3.HttpMethods.POST,
                    s3.HttpMethods.PUT,
                    s3.HttpMethods.DELETE,
                    s3.HttpMethods.HEAD,
                ],
                allowed_origins=["*"],
                allowed_headers=["*"],
                max_age=3000
            )]
        )
        
        s3_learning = s3.Bucket(
            self, "learningBucket",
            bucket_name="audio-learning-myeochoi",
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            cors=[s3.CorsRule(
                allowed_methods=[
                    s3.HttpMethods.GET,
                    s3.HttpMethods.POST,
                    s3.HttpMethods.PUT,
                    s3.HttpMethods.DELETE,
                    s3.HttpMethods.HEAD,
                ],
                allowed_origins=["*"],
                allowed_headers=["*"],
                max_age=3000
            )]
        )
        
        audio_table = dynamodb.Table(
            self, "AudioTable_myeochoi",
            partition_key=dynamodb.Attribute(name="filename", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="label", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
            stream=dynamodb.StreamViewType.NEW_AND_OLD_IMAGES  # 스트림 활성화
        )

        captcha_lambda = lambda_.Function(
            self, "CaptchaProcessor",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="captcha.handler",
            code=lambda_.Code.from_asset("lambda"),
            environment={
                "PLAY_BUCKET": s3_play.bucket_name,
                "DUMMY_BUCKET": s3_dummy.bucket_name,
                "TABLE_NAME": audio_table.table_name,
            }
        )

        dummy_processor_lambda = lambda_.Function(
            self, "DummyProcessor",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="dummy_processor.handler",
            code=lambda_.Code.from_asset("lambda"),
            environment={
                "TABLE_NAME": audio_table.table_name,
                "DUMMY_BUCKET": s3_dummy.bucket_name
            }
        )

        db_update_lambda = lambda_.Function(
            self, "DbUpdater",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="db_updater.handler",
            code=lambda_.Code.from_asset("lambda"),
            environment={
                "TABLE_NAME": audio_table.table_name
            }
        )
        
        learning_mover_lambda = lambda_.Function(
            self, "LearningMover",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="learning_mover.handler",
            code=lambda_.Code.from_asset("lambda"),
            environment={
                "TABLE_NAME": audio_table.table_name,
                "DUMMY_BUCKET": s3_dummy.bucket_name,
                "LEARNING_BUCKET": s3_learning.bucket_name
            }
        )

        # DynamoDB 스트림을 Lambda 함수의 이벤트 소스로 추가
        learning_mover_lambda.add_event_source(
            lambda_event_sources.DynamoEventSource(audio_table,
                starting_position=lambda_.StartingPosition.TRIM_HORIZON,
                batch_size=1,
                bisect_batch_on_error=True,
                retry_attempts=10
            )
        )

        api = apigateway.RestApi(self, "AudioApi",
                                default_cors_preflight_options=apigateway.CorsOptions(
                                allow_origins=apigateway.Cors.ALL_ORIGINS,
                                allow_methods=["GET", "POST", "OPTIONS"],
                                allow_headers=["Content-Type", "X-Amz-Date", "Authorization", "X-Api-Key", "X-Amz-Security-Token"],
                                allow_credentials=True))

        captcha = api.root.add_resource("captcha")
        captcha.add_method("POST", apigateway.LambdaIntegration(captcha_lambda))
        dummy = api.root.add_resource("dummy")
        dummy.add_method("POST", apigateway.LambdaIntegration(dummy_processor_lambda))
        db_update = api.root.add_resource("db_update")
        db_update.add_method("POST", apigateway.LambdaIntegration(db_update_lambda))
        learning = api.root.add_resource("learning")
        learning.add_method("POST", apigateway.LambdaIntegration(learning_mover_lambda))

        github_token = SecretValue.secrets_manager("aws", json_field="aws")

        amplify_app = amplify.App(self, "Myapp2",
                                source_code_provider=amplify.GitHubSourceCodeProvider(
                                    owner="1107c",
                                    repository="test_next",
                                    oauth_token=github_token),
                                auto_branch_creation=amplify.AutoBranchCreation(
                                    patterns=["feature/*", "test/*"]),
                                auto_branch_deletion=True)
        
        cfn_app = amplify_app.node.default_child
        cfn_app.platform = "WEB_COMPUTE"

        main_branch = amplify_app.add_branch("main", stage="PRODUCTION")

        cfn_branch = main_branch.node.default_child
        cfn_branch.framework = "Next.js - SSR"

        s3_play.grant_read(captcha_lambda)
        s3_dummy.grant_read(captcha_lambda)
        s3_dummy.grant_read_write(dummy_processor_lambda)
        s3_dummy.grant_read_write(learning_mover_lambda)
        s3_learning.grant_write(learning_mover_lambda)
        audio_table.grant_read_write_data(captcha_lambda)
        audio_table.grant_read_write_data(db_update_lambda)
        audio_table.grant_read_write_data(dummy_processor_lambda)
        audio_table.grant_read_write_data(learning_mover_lambda)

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