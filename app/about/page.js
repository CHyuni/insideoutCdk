import Image from "next/image";

export default function envtest() {
  return (
    <div>
      <p>region: {process.env.NEXT_PUBLIC_AWS_PROJECT_REGION}</p>
      <p>bucket: {process.env.NEXT_PUBLIC_AWS_USER_FILES_S3_BUCKET}</p>
      <p>user_pool: {process.env.NEXT_PUBLIC_AWS_USER_POOLS_ID}</p>
      <p>identity_pool: {process.env.NEXT_PUBLIC_AWS_COGNITO_IDENTITY_POOL_ID}</p>
      <p>user_pool_client_id: {process.env.NEXT_PUBLIC_AWS_USER_POOLS_WEB_CLIENT_ID}</p>
      <p>api_url: {process.env.NEXT_PUBLIC_API_URL}</p>
    </div>
  );
}
