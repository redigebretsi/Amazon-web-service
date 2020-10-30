# Image Process

try:
    import boto3
    from botocore.exceptions import ClientError
    import botocore
    import os
    import sys
    import json
except Exception as e:
    print(e)
import time
import logging
import PIL.Image
from logging.handlers import RotatingFileHandler


# Variable global pour les noms des queues d'entrée et de sortie.
AWS_SQS_QUEUE_NAME_INPUT = "Inbox"
AWS_SQS_QUEUE_NAME_OUTPUT = "Outbox"
AWS_S3_BUCKET ="mybucket307991"

#Class de type Client.
class client(object):

    def __init__(self):
        self.flag=0
        try:
            # Create the queue. This returns an SQS.Queue instance
            self.inputqueue = sqs.create_queue(QueueName=AWS_SQS_QUEUE_NAME_INPUT)
            self.receivedKeyName = None  #The key Name of the processed Image
        except Exception:
            print("Connexion Failed !")

        # Get the queue
        self.inputqueue = sqs.get_queue_by_name(QueueName=AWS_SQS_QUEUE_NAME_INPUT)
        print("You are connected to the SQS service ...")

    def upload_image(Self, file_name, bucket, key_name):
        s3 = boto3.client('s3')
        s3.upload_file(file_name, bucket, key_name)

        # Upload the image
        try:
        	response = s3.upload_file(file_name, bucket, key_name)
        	print("The image is sent !!")
        except ClientError as e:
            logging.error(e)
        # return False
        
	#Download the image
    def download_image(self, bucket, key_name, local_name):
        s3 = boto3.resource('s3')
        try:
            s3.Bucket(bucket).download_file(key_name,local_name)
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                print("The object does not exist.")
            else:
                raise
    #Send message
    def send(self, message=None):
        # Create a new message
        response = self.inputqueue.send_message(MessageBody=message)
        print("The Key of your image is sent !!")
        return response
        
    # Receive the Key Name of the processed Image from the sqs (OutboxQueue)        
    def receive(self):
        try:
            self.queue = sqs.get_queue_by_name(QueueName=AWS_SQS_QUEUE_NAME_OUTPUT)
            for message in self.queue.receive_messages():
                data = message.body
                print("Here is the name of your processed image : ",str(data),".jpg, check the directory from where you started your client program :)\n")
                self.receivedKeyName = str(data)
                #Download the processed Image by his Key Name
                self.download_image(AWS_S3_BUCKET, str(q.receivedKeyName), str(q.receivedKeyName)+".jpg")
                processedImageDisplay = PIL.Image.open(str(data)+".jpg")
                processedImageDisplay.show()
                message.delete()
                
                self.flag=1
        except Exception:

            return []

if __name__ == "__main__":
    # Get the service resource
    sqs = boto3.resource('sqs')
    print("You are connected to the AWS service ...")
    flag = 0
    q = client()
    while True:
        if flag == 0 :
            command = int(input("Hi, Dear Client choose one option Tap : \n"
                         "1) For sending the key of your image that you want to proccess \n"
                         "2) To exit\n"))
            flag=flag+1
        
        else :
            command = int(input("Hi again, Dear Client choose one option Tap : \n"
                         "1) For sending the key of your image that you want to proccess \n"
                         "2) To exit\n"))
        
        if command == 1 :
            ImageName = input("Enter your image name (that exist in same directory of the program) : ")
            keyName = input("Enter your key image (that exist in same directory of the program) : ")
            q.upload_image( ImageName, AWS_S3_BUCKET, keyName)
            response = q.send(message=keyName)
            while q.flag==0:
                time.sleep(0.5)
                print("Waiting for the processed Image ...")
                #Receive the Key name of the Key Name from Outbox Queue and saved in "q.receivedKeyName" self variable .
                q.receive()
            q.flag=0
        elif command == 2:
            print("See you, Bye!")
            exit()
