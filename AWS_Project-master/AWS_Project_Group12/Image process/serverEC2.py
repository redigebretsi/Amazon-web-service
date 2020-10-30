try:
    import boto3
    from botocore.exceptions import ClientError
    import botocore
    import os
    import sys
    import json
except Exception as e:
    print(e)
    
import png
import time
import logging
from PIL import Image
import numpy as np
import skimage.io
import os
import matplotlib.pyplot as plt
from skimage import exposure
import sys
import os
#import scipy.misc
import imageio


# Variable global pour les noms des queues d'entrée et de sortie.
AWS_SQS_QUEUE_NAME_INPUT = "Inbox"
AWS_SQS_QUEUE_NAME_OUTPUT = "Outbox"
AWS_S3_BUCKET ="mybucket307991"

class worker(object):

    def __init__(self):
        try:
            # Create the queue. This returns an SQS.Queue instance
            self.s3 = boto3.client('s3')
            self.s3.create_bucket(Bucket=AWS_S3_BUCKET)
            self.queue = sqs.create_queue(QueueName=AWS_SQS_QUEUE_NAME_OUTPUT)
        except Exception:
            print(e)
        # Get the queue
        self.inputqueue = sqs.get_queue_by_name(QueueName=AWS_SQS_QUEUE_NAME_INPUT)
        print("You are connected to the SQS service ...")

    def upload_image(Self, file_name, bucket, key_name):
        s3 = boto3.client('s3')
        s3.upload_file(file_name, bucket, key_name)

        # Upload the image
        try:
        	response = s3.upload_file(file_name, bucket, key_name)
        	print("The image is sended !!")
        except ClientError as e:
            logging.error(e)
        # return False
       

    # download the image to process
    def download_image(self, bucket, key_name, local_name):
        s3 = boto3.resource('s3')
        try:
            s3.Bucket(bucket).download_file(key_name,local_name)
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                print("The object does not exist.")
            else:
                raise
                
    def send(self, message=None):
        try:
            # Create the queue. This returns an SQS.Queue instance
            self.queue = sqs.create_queue(QueueName=AWS_SQS_QUEUE_NAME_OUTPUT)
        except Exception:
            print(e)
        # Create a new message
        response = self.queue.send_message(MessageBody=message)
        #self.upload_file("activity.log",AWS_S3_BUCKET,"logfile")
        print("The new keyname is sent to outbox queue !!")
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

    #Process Image functionnality
    
    def adjust_gamma(self,image,gamma):
         I=skimage.color.rgb2gray(image);
         I = I / np.max(I) ;
         I2= exposure.adjust_gamma(I, gamma);
         return I2

    def contrast_stretching(self, image ,E) :
         I=skimage.color.rgb2gray(image);
         epsilon=sys.float_info.epsilon ;
         m=np.mean(I) ;
         I=I.astype("float") ;
         Ar=1./(1.+( m/(I+epsilon ) )**E) ;
         return Ar;
     
    def Sauvola_Method(self,image,Wind_size,R=128,k=0.5):
         imsize=image.shape
         if(len(imsize)==3):
             Image=skimage.color.rgb2gray(image)
             imsize=Image.shape
         Mask=np.zeros(imsize)
         nrows=imsize[0]
         ncols=imsize[1]
         #detrminig the mean and the sd for each pixel
         half_wind=Wind_size//2
         for i in range(half_wind,nrows): 
             for j in range(half_wind,ncols): 
                 Window=Image[(i-half_wind):(i+half_wind),(j-half_wind):(j+half_wind)]
                 mean=np.mean(Window)
                 std=np.std(Window)
                 Mask[i][j]=mean*(1+k*((std/R)-1))
         return Mask


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
        file_handler = RotatingFileHandler('activity.log', 'a', 1000000, 1)
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
    i = None
    if len(sys.argv) < 2 :
         print("You should add a type of process \nTap \"gamma\" to adjust the gamma of the image\nTap \"contrast\" to adjust the contrast of the image\nTap \"sauvola\" to apply the Sauvola method to the image\n\n**************************************************************\nexample : python3 serverEC2.py gamma \n(This is a command for adjusting the gamma for an image).\n**************************************************************\n\nTry again, Bye :)")
         exit()
    else:
         if str(sys.argv[1]) == "gamma" or str(sys.argv[1]) == "contrast" or str(sys.argv[1]) == "sauvola":
             i = str(sys.argv[1])
         else:
             print("You should add a type of process \nTap \"gamma\" to adjust the gamma of the image\nTap \"contrast\" to adjust the contrast of the image\nTap \"sauvola\" to apply the Sauvola method to the image\n\n**************************************************************\nexample : python3 serverEC2.py gamma \n(This is a command for adjusting the gamma for an image).\n**************************************************************\n\nTry again, Bye :)")
             exit()
         
         
    
    # Get the service resource
    sqs = boto3.resource('sqs')
    #s3 = boto3.resource('s3')
    print("You are connected to the AWS service ...")
    # we go to the dossier to process the image 
    os.chdir("ProcessingImageDirectory")
    q = worker()
    if i == "gamma":
        while True :
            print("waiting for an image ...")
            time.sleep(0.5)
            for keyname in q.inputqueue.receive_messages():
                time.sleep(0.5)
                print(keyname.body,"Image Processing ...")
                q.download_image(AWS_S3_BUCKET, keyname.body,"ImageToProcess.jpg")
                Ima=skimage.io.imread("ImageToProcess.jpg")
                plt.imshow(Ima,cmap='gray')
                Ima.shape
                #plt.show();
                I2 = q.adjust_gamma(Ima,5)
                #We show the Processed Image and we save it with the Name (Keyname+"Processed.jpg") Manually with the save Button, and
                #plt.show();            
                NameProcessedImage = str(keyname.body)+"Processed.jpg"
                KeyNameProcessedImage = str(keyname.body)+"Processed"           
                #Save the Process Image in the local reprosetery of the worker.
                binary_transform = np.array(I2)
                imageio.imwrite(NameProcessedImage, binary_transform)
                print("The image is processed !! ")
                #Send the keyname of the Processed image in the sqs (outbox) Queue.
                q.send(KeyNameProcessedImage)
                #Send the processed Image in the S3
                q.upload_image(NameProcessedImage, AWS_S3_BUCKET, KeyNameProcessedImage)
      	        #Delete the key name of the Original Image from the Inbox Queue. 
                keyname.delete()     
      
    if i == "contrast":
        while True :
            print("waiting for an image ...")
            time.sleep(0.5)
            for keyname in q.inputqueue.receive_messages():
                time.sleep(0.5)
                print(keyname.body,"Image Processing ...")
                q.download_image(AWS_S3_BUCKET, keyname.body,"ImageToProcess.jpg")
                Ima=skimage.io.imread("ImageToProcess.jpg")
                plt.imshow(Ima,cmap='gray')
                Ima.shape
                #plt.show();
                I2 = q.contrast_stretching(Ima,0.8)
                #We show the Processed Image and we save it with the Name (Keyname+"Processed.jpg") Manually with the save Button, and
                #plt.show();            
                NameProcessedImage = str(keyname.body)+"Processed.jpg"
                KeyNameProcessedImage = str(keyname.body)+"Processed"           
                #Save the Process Image in the local reprosetery of the worker.
                binary_transform = np.array(I2)
                imageio.imwrite(NameProcessedImage, binary_transform)
                print("The image is processed !! ")
                #Send the keyname of the Processed image in the sqs (outbox) Queue.
                q.send(KeyNameProcessedImage)
                #Send the processed Image in the S3
                q.upload_image(NameProcessedImage, AWS_S3_BUCKET, KeyNameProcessedImage)
      	        #Delete the key name of the Original Image from the Inbox Queue. 
                keyname.delete()                               
         
    if i == "sauvola":
        while True :
            print("waiting for an image ...")
            time.sleep(0.5)
            for keyname in q.inputqueue.receive_messages():
                time.sleep(0.5)
                print(keyname.body,"Image Processing ...")
                q.download_image(AWS_S3_BUCKET, keyname.body,"ImageToProcess.jpg")
                Ima=skimage.io.imread("ImageToProcess.jpg")
                plt.imshow(Ima,cmap='gray')
                Ima.shape
                #plt.show();
                Mask = q.Sauvola_Method(Ima,16)
                I2 = skimage.color.rgb2gray(Ima)
                I2 = I2>Mask
                #We show the Processed Image and we save it with the Name (Keyname+"Processed.jpg") Manually with the save Button, and
                #plt.show();            
                NameProcessedImage = str(keyname.body)+"Processed.jpg"
                KeyNameProcessedImage = str(keyname.body)+"Processed"           
                #Save the Process Image in the local reprosetery of the worker.
                binary_transform = np.array(I2)
                imageio.imwrite(NameProcessedImage, img_as_uint(binary_transform))
                print("The image is processed !! ")
                #Send the keyname of the Processed image in the sqs (outbox) Queue.
                q.send(KeyNameProcessedImage)
                #Send the processed Image in the S3
                q.upload_image(NameProcessedImage, AWS_S3_BUCKET, KeyNameProcessedImage)
      	        #Delete the key name of the Original Image from the Inbox Queue. 
                keyname.delete()                 
