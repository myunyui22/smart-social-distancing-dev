from .AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import logging
import time
import argparse
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class IoTCore:
	host = "a2fdzy4p41bk97-ats.iot.us-west-2.amazonaws.com"
	certPath = "libs/libs-cert/"
	clientId = "jetson"
	topic = "smart-social-distancing7"

	def __init__(self, message):
		self.message = message

	def publish(self):
		myAWSIoTMQTTClient = None
		myAWSIoTMQTTClient = AWSIoTMQTTClient(self.clientId)	
		myAWSIoTMQTTClient.configureEndpoint(self.host, 8883) 
		myAWSIoTMQTTClient.configureCredentials("{}aws-root-cert.pem".format(self.certPath), "{}a7c21c6245-private.pem.key".format(self.certPath), "{}a7c21c6245-certificate.pem.crt".format(self.certPath))


		myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
		myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1) 
		myAWSIoTMQTTClient.configureDrainingFrequency(2) 
		#myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10) 
		#myAWSIoTMQTTClient.configureMQTTOperationTimeout(5) 
		myAWSIoTMQTTClient.connect()
		messageJson = json.dumps(self.message)
		myAWSIoTMQTTClient.publish(self.topic, messageJson, 1)
		logger.info(f'Published topic %s: %s \n' % (self.topic, messageJson))
		print('Published topic %s: %s \n' % (self.topic, messageJson))
		myAWSIoTMQTTClient.disconnect()


