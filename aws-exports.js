const awsconfig = {
	"aws_project_region": process.env.NEXT_PUBLIC_AWS_PROJECT_REGION,
	// "aws_user_files_s3_bucket": process.env.NEXT_PUBLIC_AWS_USER_FILES_S3_BUCKET,
	// "aws_user_files_s3_bucket_region": process.env.NEXT_PUBLIC_AWS_PROJECT_REGION,
	// "aws_user_pools_id": process.env.NEXT_PUBLIC_AWS_USER_POOLS_ID,
	// "aws_user_pools_web_client_id": process.env.NEXT_PUBLIC_AWS_USER_POOLS_WEB_CLIENT_ID,
	// "aws_cognito_identity_pool_id": process.env.NEXT_PUBLIC_AWS_COGNITO_IDENTITY_POOL_ID,
	// "aws_cognito_region": process.env.NEXT_PUBLIC_AWS_PROJECT_REGION,
	"aws_api_gateway_url": process.env.NEXT_PUBLIC_API_URL,
    // "ec2_public_ip": process.env.NEXT_PUBLIC_EC2_PUBLIC_IP,
    // "ec2_private_ip": process.env.NEXT_PUBLIC_EC2_PRIVATE_IP,
	// "oauth": {
    //     "domain": process.env.NEXT_PUBLIC_AWS_COGNITO_DOMAIN,
    //     "scope": [
    //         "phone",
    //         "email",
    //         "openid",
    //         "profile",
    //         "aws.cognito.signin.user.admin"
    //     ],
    //     "redirectSignIn": "http://localhost:3000/",
    //     "redirectSignOut": "http://localhost:3000/",
    //     "responseType": "code" // or "token" if you prefer implicit grant
    // },
}
export default awsconfig;