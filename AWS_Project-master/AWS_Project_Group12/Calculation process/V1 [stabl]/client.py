try:
    import boto3
    import botocore
    import os
    import sys
    import json
    import time
except Exception as e:
    print(e)


# Variable global pour les noms des queues d'entrée et de sortie.
AWS_SQS_QUEUE_NAME_INPUT = "InputQueue"
AWS_SQS_QUEUE_NAME_OUTPUT = "OutputQueue"

#Class de type Client.
class client(object):

    def __init__(self):
        self.flag=0
        try:
            # Create the queue. This returns an SQS.Queue instance
            self.inputqueue = sqs.create_queue(QueueName=AWS_SQS_QUEUE_NAME_INPUT)
        except Exception:
            print(e)

        # Get the queue
        self.inputqueue = sqs.get_queue_by_name(QueueName=AWS_SQS_QUEUE_NAME_INPUT)
        print("You are connected to the SQS service ...")

    def send(self, message=None):
        # Create a new message
        response = self.inputqueue.send_message(MessageBody=message)
        return response

    def receive(self):
        try:
            self.queue = sqs.get_queue_by_name(QueueName=AWS_SQS_QUEUE_NAME_OUTPUT)
            for message in self.queue.receive_messages():
                data = message.body
                print(str(data))
                message.delete()
                self.flag=1
        except Exception:

            return []

if __name__ == "__main__":
    # Get the service resource
    sqs = boto3.resource('sqs')
    print("You are connected to the AWS service ...")
    q = client()
    while True:
        command = int(input("Hi, Dear Client choose one option : "
                         "Tap \n1) for sending your list of interger \n"
                         "2) To exit \nWrite the number of your choice :"))
        if command == 1 :
            msg = input("Enter your List of integer sepreted by comma and at list with 2 Integers : ")
            while(len(msg)<=2):
                print("Problem with your list restart again ...")
                msg = input("Enter your List of integer sepreted by comma and at list with 2 Integers : ")
            response = q.send(message=msg)
            print("The List is sended to the Ec2 Worker !!")
            while q.flag==0:
                time.sleep(0.5)
                print("Wait for response ...")
                q.receive()
            q.flag=0

        elif command == 2:
            print("See you, Bye!")
            exit()
