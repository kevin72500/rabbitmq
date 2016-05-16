import pika
import time

connection=pika.BlockingConnection(
	pika.ConnectionParameters('localhost'))
channel=connection.channel()

channel.queue_declare(queue='task_queue',durable=True)
print '[*] waiting for message . to exit press CTRL + C'

def callback(ch,method,properties, body):
	print '[x] receive %s ' % body
	time.sleep(body.count(b'.'))
	print '[x] done'
	ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback,queue='task_queue')
channel.start_consuming()