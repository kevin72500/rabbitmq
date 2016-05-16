import pika

connection = pika.BlockingConnection(pika.ConnectionParameters(
               '192.168.56.102',5672,"",pika.credentials.PlainCredentials('kevin','kevin')))
channel = connection.channel()
channel.queue_declare(queue='hello')
channel.basic_publish(exchange='',
	routing_key='hello',body='Hello World')
print("[X] sent 'hello world")
connection.close()
