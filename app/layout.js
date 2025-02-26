// 'use client'

// import { useEffect } from 'react';
// import { Amplify } from 'aws-amplify';
// import awsconfig from '../aws-exports';

export default function RootLayout({ children }) {
  // useEffect(() => {
  //   Amplify.configure(awsconfig);
  // }, []);

  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
