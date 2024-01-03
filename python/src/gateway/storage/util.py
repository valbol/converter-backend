import pika, json
import logging

def upload(f, fs, channel, access):
    logging.info("uploading file")
    try:
        fid = fs.put(f)
    except Exception as err:
        print(err)
        return "internal server error", 500

    message = {
        "video_fid": str(fid),
        "mp3_fid": None,
        "username": access["username"],
    }
    logging.info("sending message to queue")
    try:
        channel.basic_publish(
            exchange="",
            routing_key="video",
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )
    except Exception as err:
        logging.error(f" in upload: Failed to send message to queue: {err}")
        fs.delete(fid)
        return "internal server error", 500