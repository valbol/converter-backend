import pika, sys, os, time
from pymongo import MongoClient
import gridfs
from convert import to_mp3

def main():
  client = MongoClient('host.minikube.internal', 27017)
  db_videos = client.videos
  db_mp3s = client.mp3s
  # ! gridfs
  fs_videos = gridfs.GridFS(db_videos)
  fs_mp3s = gridfs.GridFS(db_mp3s)
  
  # ! rabbitmq connection
  connection = pika.BlockingConnection(
    # !!! host="rabbitmq" this is possible because our service name and it will resolve to the host ip of the rabbitmq service 
      pika.ConnectionParameters(host="rabbitmq")
  )
  channel = connection.channel()
  
  def callback(ch, method, properties, body):
    err = to_mp3.start(body, fs_videos, fs_mp3s, ch)
    if err:
      # no-ack - so it will not removed from the queue and other process will try to execute it 
      ch.basic_nack(delivery_tag=method.delivery_tag)
    else:
      ch.basic_ack(delivery_tag=method.delivery_tag)

  channel.basic_consume(
      queue=os.environ.get("VIDEO_QUEUE"),
      # ! we need a callback func that will be executed every-time a message is pulled from the queue
      on_message_callback=callback
  )
  
  print('Waiting for messages, To exit press ctrl+c')
  
  channel.start_consuming()

if __name__ == "__main__":
  try: 
    main()
  except KeyboardInterrupt:
    print("Interrupted")
    try:
      sys.exit(0)
    except SystemExit:
      os._exit(0)
    