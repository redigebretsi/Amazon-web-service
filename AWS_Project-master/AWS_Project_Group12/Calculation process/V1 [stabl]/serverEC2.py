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

from logging.handlers import RotatingFileHandler

# Variable global pour les noms des queues d'entrée et de sortie.
AWS_SQS_QUEUE_NAME_INPUT = "InputQueue"
AWS_SQS_QUEUE_NAME_OUTPUT = "OutputQueue"
AWS_S3_BUCKET ="mybucket3079911"

class worker(object):

    def __init__(self):
        try:
            # Create the queue. This returns an SQS.Queue instance
            self.flag = 0
            self.s3 = boto3.client('s3')
            self.s3.create_bucket(Bucket=AWS_S3_BUCKET)

            self.queue = sqs.create_queue(QueueName=AWS_SQS_QUEUE_NAME_OUTPUT)
        except Exception:
            print(e)
        # Get the queue
        self.inputqueue = sqs.get_queue_by_name(QueueName=AWS_SQS_QUEUE_NAME_INPUT)
        print("You are connected to the SQS service ...")

    def upload_file(Self,file_name, bucket, object_name):
        """Upload a file to an S3 bucket

        :param file_name: File to upload
        :param bucket: Bucket to upload to
        :param object_name: S3 object name. If not specified then file_name is used
        :return: True if file was uploaded, else False
        """
        # If S3 object_name was not specified, use file_name
        if object_name is None:
            object_name = file_name

        # Upload the file
        s3_client = boto3.client('s3')
        try:
            
            response = s3_client.upload_file(file_name, bucket, object_name)
        except ClientError as e:
            logging.error(e)
            # return False
        # return True

    def send(self, message=None):
        try:
            # Create the queue. This returns an SQS.Queue instance
            self.queue = sqs.create_queue(QueueName=AWS_SQS_QUEUE_NAME_OUTPUT)
        except Exception:
            print(e)
        # Create a new message
        response = self.queue.send_message(MessageBody=message)
        if self.flag == 0:
            self.logFile()
            self.flag = 1
            
        self.upload_file("DesciptionLogFile.log",AWS_S3_BUCKET,"logfile")
        print("The logfile is saved in the S3 !")
        #self.logFile()
        return response

    def receive(self):
        try:
            queue = sqs.get_queue_by_name(QueueName=AWS_SQS_QUEUE_NAME_OUTPUT)
            print("You are connected to the response Queue ...")
            queue = self.resource.get_queue_by_name(QueueName=self.QueueName)
            for message in queue.receive_messages():
                data = message.body
                message.delete()
        except Exception:

            return []
        return data

    def transIntoList(self, message=None):
        # input comma separated elements as string
        str = message


        # conver to the list
        list = str.split(",")
        print("list: ", list)

        # convert each element as integers
        li = []
        for i in list:
            li.append(int(i))
        return li
        # print list as integers
        print("list (li) : ", li)

   #Fonction du process
    def process(self,list=[]):
        max = list[0]
        min = list[0]
        mean = 0
        median = 0
        for i in list:
            if i >= max:
                max = i
            if i <= min:
                min = i
            mean = mean + i
        mean = mean/len(list)
        n = len(list)
        list.sort()

        if n % 2 == 0:
            median1 = list[n // 2]
            median2 = list[n // 2 - 1]
            median = (median1 + median2) / 2
        else:
            median = list[n // 2]
        print("Resultat : \n Le Max de votre list est : ",max,"\n Le Min de votre list est : ",
              min,"\n Le Mean de votre list est :",mean,"\n La Median de votre list est :",median)
        msg = "Resultat : Le Max de votre list est : "+str(max)+" Le Min de votre list est : "+str(min)+" Le Mean de votre list est :"+str(mean)+" La Median de votre list est :"+str(median)
        self.send(msg)
        print("La reponse a été envoyer !!")
        return msg

    def logFile(self):
        # création de l'objet logger qui va nous servir à écrire dans les logs
        logger = logging.getLogger()
        # on met le niveau du logger à DEBUG, comme ça il écrit tout
        logger.setLevel(logging.DEBUG)

        # création d'un formateur qui va ajouter le temps, le niveau
        # de chaque message quand on écrira un message dans le log
        formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
        # création d'un handler qui va rediriger une écriture du log vers
        # un fichier en mode 'append', avec 1 backup et une taille max de 1Mo
        file_handler = RotatingFileHandler('DesciptionLogFile.log', 'a', 1000000, 1)
        # on lui met le niveau sur DEBUG, on lui dit qu'il doit utiliser le formateur
        # créé précédement et on ajoute ce handler au logger
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # création d'un second handler qui va rediriger chaque écriture de log
        # sur la console
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)
        logger.addHandler(stream_handler)

        # Après 3 heures, on peut enfin logguer
        # Il est temps de spammer votre code avec des logs partout :
        logger.info('Log file ')
        logger.warning('Testing %s', 'foo')


if __name__ == "__main__":
    # Get the service resource
    sqs = boto3.resource('sqs')
    #s3 = boto3.resource('s3')
    print("You are connected to the AWS service ...")
    q = worker()
    while True :
        print("waiting for message ...")
        time.sleep(0.5)
        for message in q.inputqueue.receive_messages():
            #time.sleep(5)
            print(message.body)
            li = q.transIntoList(str(message.body))
            q.process(li)
            message.delete()
            
            
            
            
            
            
            
            
