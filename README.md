# Inside Out: CAPTCHA using SER (Speech Emotion Recognition)

## Overview
Emotion CAPTCHA enhances security by using Speech Emotion Recognition (SER) to distinguish humans from bots. Users identify emotions in speech, a task easy for humans but difficult for AI, improving both security and accessibility.

## Features
- **Emotion-Based Authentication**: Uses speech emotion recognition to differentiate humans from bots.
- **AI-Resistant Security:** Harder for AI to bypass compared to traditional text or image-based CAPTCHA.
- **Improved Accessibility:** Provides an easy authentication method for visually impaired users.
- **Secure and Scalable**: Built on AWS infrastructure, ensuring high security and scalability.

## Architecture
The Inside Out architecture integrates multiple components to ensure secure and efficient emotion-based authentication. Below is a detailed breakdown of the architecture:
![Image](https://github.com/user-attachments/assets/1fa365e4-152b-47c8-ba43-71a022dcbe29)


### Components
1. **Frontend Component**
	- **AWS Amplify**: Distributes the Next.js-based web application to mobile and desktop devices.
	- **Amazon S3**: Stores generated audio files in PlayBucket, dummy audio files in Dummy Bucket, and training data in Learning Bucket.
	- **Amazon API Gateway**: Facilitates communication between the frontend and backend by invoking CAPTCHA Lambda and Learning Mover Lambda functions over HTTPS.
2. **AWS Step Functions Workflow**
	- **Text-to-Mel Spectrogram Conversion**: Converts text to mel spectrograms using Tacotron2, representing audio signals in frequency domain.
	- **Mel Spectrogram-to-Speech Conversion**: Transforms mel spectrograms into real audio using HiFi-GAN.
	- **Data Labeling and Storage**: Stores user-labeled emotion data from the second test in DynamoDB.
	- **Data Movement**: Moves audio files from Dummy Bucket to Learning Bucket via Learning Mover Lambda when labeling thresholds are met.
3. **Supporting Services**
	- **AWS Lambda**: Executes serverless CAPTCHA Lambda for audio processing and Learning Mover Lambda for data management.
	- **Amazon DynamoDB**: Stores and manages user-labeled data from the second test until predefined conditions trigger data movement.
	- **AWS CDK**: Enables continuous integration and deployment of all service components.
### Workflow
1. **User Interaction**: Users access the Next.js-based application via mobile or desktop devices through AWS Amplify.	-
2. **Audio Generation**: Text is converted to mel spectrograms using Tacotron2, then to audio via HiFi-GAN, and stored in PlayBucket on Amazon S3.
3. **API Invocation**: API Gateway connects the frontend to CAPTCHA Lambda, which processes audio and integrates with the workflow.
4. **First Test**: Users pass the initial test, triggering retrieval of dummy audio from Dummy Bucket for the second test.
5. **Second Test and Labeling**: Users label emotions in the audio, with results stored in DynamoDB.
6. **Data Management**: Learning Mover Lambda monitors DynamoDB, deleting entries and moving audio files to Learning Bucket when labeling thresholds are reached.
7. **Infrastructure Management**: AWS CDK builds and deploys all components, ensuring seamless integration and continuous delivery.

## Getting Started

**Note: This project is not currently configured to operate.**

**Inside Out isn't fully operational yet, it's in development or needs further setup. Look forward to future updates! (AWS backend hasn't been deployed yet, currently no update scheduled (2025-02-26))**

## Contributing
We welcome contributions to enhance the Inside Out platform. Please read our [Contributing Guide](CONTRIBUTING.md) for more details.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE.md) file for details.

## Acknowledgements
- **Disney Pixar's Inside Out**: Inspiration for the project’s theme.
- **AWS**: Providing the robust infrastructure and services that power the platform.

---

![Inside Out Poster](https://github.com/wonhyeongseo/inside-out/assets/29195190/29734aa2-fd39-4e7e-94e0-697efee09af8)

_Disclaimer: Inside Out references and imagery are the property of Disney Pixar._
