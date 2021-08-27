# smart-social-distancing-dev

- [Smart Social Distancing](#smart-social-distancing)
  - [Introduction](#Introduction)
  - [Getting Started](#getting-started)
    - [requirements](#requirements)
    - [docker start](#docker-start)
  - [Processor](#processor)
    - [docker run](#docker-run)
    - [run with video](#run-with-video)
    - [run with webcam](#run-with-webcam)
    - [aws s3 upload](#aws-s3-upload)
    - [bird's eye view(BEV)](#BEV)
    - [graph streaming](#graph-streaming)
  - [result](#result)

## Introduction


The importance of social distancing is also increasing as cotos and pandemics occur around the world. Except for some spaces, however, it is difficult to maintain social distancing and lack of surveillance personnel. Therefore, we need to think of ways to keep social distancing more effectively. Fortunately, most public institutions have CCTVs. Then can't we monitor social distancing using this ubiquitous CCTV? I would like to introduce a project that can monitor social distancing using small AI computer JETSON NANO.


This project is based entirely on [this place](https://github.com/neuralet/smart-social-distancing).


<div align="center">
  <img  width="100%" src="demo.gif">
</div>


The project is divided into areas that detect social distancing as a whole and areas where it can be monitored by websites.
The entire flow of the project is shown in the picture below.

<img width="950" alt="projectFlow" src="https://user-images.githubusercontent.com/65693240/130828219-19ef0d56-cfc5-4523-b778-59102b84e5dc.png">


## Getting Started


### requirements


jetpack 4.3


aiofiles==0.5.0

boto3==1.14.59

fastapi==0.61.1

pandas==1.1.2

pyhumps==1.6.1

pytest==6.0.1

pytest-mock==3.5.1

freezegun==1.1.0


python-dotenv==0.15.0

requests==2.24.0

schedule==0.6.0

slackclient==2.8.2

uvicorn==0.11.8

yagmail==0.11.224

passlib==1.7.2

bcrypt==3.2.0

python-jose==3.2.0


The necessary libraries can also be found in api/requirements.txt


### docker-start


In order to run this project, a docker must be installed in the jetson nano.
If you haven't installed the docker yet, please follow the instructions below.


#### Installable Environment
Ubuntu Groovy 20.10

Ubuntu Focal 20.04 (LTS)

Ubuntu Bionic 18.04 (LTS) <<me!

Ubuntu Xenial 16.04 (LTS)


#### Delete previously installed docker


Even if the docker is deleted, images and containers can be preserved.
```bash
$ sudo apt-get remove docker docker-engine docker.io containerd runc
```


#### Docker Installation


```bash
#Update Ubuntu Package
$ sudo apt-get update 

#Install the required package
$ sudo apt-get install apt-transport-https ca-certificates curl gnupg-agent software-properties-common

#Add official GPG key (copy with last –)
#return : ok
$ curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add – 

#Confirm Fingerprint Key
$ apt-key fingerprint 0EBFCD88

#Install Repository
#x86_64 / amd64
$ sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"
#armhf
$ sudo add-apt-repository \
   "deb [arch=armhf] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"
#arm64
$ sudo add-apt-repository \
   "deb [arch=arm64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"
   
#Install the latest version of Docker
$ sudo apt-get install docker-ce docker-ce-cli containerd.io

#Select a version to install
$ sudo apt-get install docker-ce=<VERSION_STRING> docker-ce-cli=<VERSION_STRING> containerd.io

#Check the list of versions that can be installed (write in the <VERSION_STRING>)
#('docker-ce' and 'docker-ce-cli' versions must be the same)
$ apt-cache madison docker-ce 
$ apt-cache madison docker-ce-cli

#run Docker example 'hello world'
$ sudo docker run hello-world 

#When executed, it should look like the picture below
```

  ![docker-hello_world](https://user-images.githubusercontent.com/65693240/130828191-04593538-7569-4f1f-90af-a59cfbd4eee8.png)

```bash
#Check Docker Version
$ docker -v

#Add dockers to user group (no sudo attachment required when running)
$ sudo usermod -aG docker $USER
$ sudo reboot
```


## processor


### docker-run

```bash
# 1) Download TensorRT engine file built with JetPack 4.3:
./download_jetson_nano_trt.sh

# 2) Build Docker image for Jetson Nano
docker build -f jetson-nano.Dockerfile -t "neuralet/smart-social-distancing:latest-jetson-nano" .

# 3) Run Docker container:
docker run -it --runtime nvidia --privileged -p HOST_PORT:8000 -v "$PWD":/repo -e TZ=`./timezone.sh` neuralet/smart-social-distancing:latest-jetson-nano
```


### run-with-video


You can modify VideoPath of categor [source_0] to the video path in config-jetson-nano.ini file.


### run-with-webcam


After connecting the webcam to jetson nano
```bash
$ v4l2-ctl --list-devices
```
Run the above command to find, copy, and paste the webcam address from the generated list into VIdeopath in category [source_0] of the config-jetson-nano.ini file.


### aws-s3-upload


When the project runs, the generated csv file can be uploaded to the s3 bucket.
In order to upload to S3, you need to provide AWS_BUCKET_REGION, AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY.
.env.example Download the file, enter the information in the bucket generated by aws s3, and save it under the name aws.env


There are four pieces of information that need to be entered.

1)aws bucket region
2)aws access key ID
3)aws secret access key
4)secret access key



After selecting the option, set Enable to Tru in category [PeriodicTask_1] of the config-jetson-nano.ini file, enter BackupInteval as the desired upload time (in minutes), and enter the name of the bucket you created in BackupS3Bucke. 


### BEV 


bird's eye view(BEV), which is used for black boxes and self-driving cars, is a technology that converts photos taken from perspective into vertical skies.
I added this bird's eye view method in a way that saves distance between people for distinction from the GitHub I referred to.
This method also allows for more accurate distance between people.

![bird's_eye_view](https://user-images.githubusercontent.com/65693240/130828136-fdb4e936-a4b4-48f8-95de-3e28ce091c64.png)
(https://deepnote.com/@deepnote/A-social-distancing-detector-using-a-Tensorflow-object-detection-model-Python-and-OpenCV-KBcEvWejRjGyjy2YnxiP5Q)


For the application method, enter 'birdViewDistance' in 'DistMethod' variable of category [source_0] in config-jetson-nano.ini file.
There are four ways to get distance and you can choose one of them.
CalibratedDistance
FourCornerPointsDistance
CenterPointsDistance
birdViewDistance


Detailed code for each option can be found in the libs/source_post_processors/social_distance.py file.

### graph-streaming


The csv file uploaded to s3 was imported, printed as a graph, and live streaming was established to check the video of the webcam in real time.
After running the docker project, open another terminal to move to the smart-social-distancing folder and execute the command below.
```bash
$ pyhon3 server.py -i YOUR_IP_ADDERESS -p YOUR_PORT
```


With jetson nano's server running, you can view live streaming by accessing jetson nano's IP address on your computer or mobile phone.


If you use multiple cameras, the location where the images of the webcam are stored may be different, so please check the 'path' variable in the server.py file.


## result


When you run the project, you can see that images of people recognizing and hitting bounding boxes are saved as ts files.

  ![result-ts_file](https://user-images.githubusercontent.com/65693240/130828240-131f6865-36d5-4b12-a52d-9c2f805f87b2.png)


If you set the video as an input image, you can see the results below.

![result-video](https://user-images.githubusercontent.com/65693240/130828399-7b02d591-b8d1-4376-bcbb-0d726ce2bad6.gif)

Finally, live streaming and graph visualizations using webcams can be found [here](https://user-images.githubusercontent.com/65693240/130826740-faacbdd9-a5d3-4db8-8524-7448c2961251.mp4).

