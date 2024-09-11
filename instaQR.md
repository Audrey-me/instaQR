Local Deployment
1. prepare the frontend by creating a nextjs project using this command
- npx create-next-app@latest
2. update your node version to the latest(Node.js version >= v18.17.0) by downloading and installing
- https://nodejs.org/en
3. cd into the frontend folder and install react-icons
- npm install react-icons
- run "npm run dev" to start the frontend app
4. cd into the backend folder and install fastapi
- run the requirements.txt file to be able to install all the dependencies
- set up your AWS Credentials
5. Run the backend code "python index.py"

** Containerisation
You can see the Dockerfile on the backend and frontend folder, as well as a docker compose file in the root directory. The docker compose will help us run our containers locally for testing purposes.
1. Create a ".env" file in the root directory, where you have your docker compose file and setup your AWS Credentials
An example 
```
AWS_ACCESS_KEY_ID=<your-access-key>
AWS_SECRET_ACCESS_KEY=<your-secret-access-key>
AWS_REGION=us-west-2
S3_BUCKET_NAME=<replace-with-your-bucketname> 
```

2. Push your images to ECR
- push to ecr using the commands on the ecr repository you created to be able to generate an image uri for your containers(434514414684.dkr.ecr.us-west-2.amazonaws.com/insta-backend:latest)


3. Orchestration using AWS EKS
3.1.  Launch a vm so as not to install on your local machine
   - install aws cli and configure your credentials
   - sudo yum install awscli -y
   - aws configure

- install the required tools kubectl(to interact with kubernetes cluster),eksctl(To easily create and manage EKS clusters)
- curl -o kubectl https://s3.us-west-2.amazonaws.com/amazon-eks/1.21.2/2021-10-11/bin/linux/amd64/kubectl
chmod +x ./kubectl
mkdir -p $HOME/bin && cp ./kubectl $HOME/bin/kubectl && export PATH=$HOME/bin:$PATH

- curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
sudo mv /tmp/eksctl /usr/local/bin

4. Create an EKS cluster
- eksctl create cluster --name instaQR-eks-cluster --region us-west-2 --nodegroup-name standard-workers --node-type t3.medium --nodes 3 --nodes-min 1 --nodes-max 3

5. update your cluster to be able to use kubectl
- aws eks --region us-west-2 update-kubeconfig --name instaQR-eks-cluster
