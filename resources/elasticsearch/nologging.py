import psutil
from datetime import datetime
from pprint import pprint
import csv
import time
import pandas as pd

class Monitor:

	def __init__(self, pid):

		self.pid = pid
		self.cpu_usage = {'cpu_usage': []}
		self.memory_usage = {'memory_usage': []}


	def getData(self):
		timestamp = datetime.now().strftime("%d-%m-%Y (%H:%M:%S.%f)")
		self.getCPU(timestamp)
		self.getMemory(timestamp)

	def getCPU(self, timestamp):
		cpus = []
		p = psutil.Process(pid=self.pid)
		for i in range(10):
			p_cpu = p.cpu_percent(interval=.1)
			cpus.append(p_cpu)
		self.cpu_usage['cpu_usage'].append([timestamp, float(sum(cpus))/len(cpus)])  


	def getMemory(self, timestamp):
		self.memory_usage['memory_usage'].append([timestamp, dict(psutil.virtual_memory()._asdict())]) 


	def toCSV(self):

		lines = []
		for i in range(len(self.cpu_usage['cpu_usage'])):
			temp = self.cpu_usage['cpu_usage'][0][0] + ',' + str(self.cpu_usage['cpu_usage'][0][1]) + ',' 
			temp += str(self.memory_usage['memory_usage'][0][1]['percent']) + ',' + str(self.memory_usage['memory_usage'][0][1]['active']) + ',' 
			temp += str(self.memory_usage['memory_usage'][0][1]['available']) + ',' + str(self.memory_usage['memory_usage'][0][1]['free']) + ','
			temp += str(self.memory_usage['memory_usage'][0][1]['inactive']) + ',' + str(self.memory_usage['memory_usage'][0][1]['total']) + ','
			temp += str(self.memory_usage['memory_usage'][0][1]['used']) + ',' + str(self.memory_usage['memory_usage'][0][1]['wired'])
			lines.append(temp)

		filename = str(self.pid) + '.csv'

		with open(filename, 'w') as f:
			w = csv.writer(f, delimiter=',')
			w.writerows([x.split(',') for x in lines])

		df = pd.read_csv(filename)
		df.columns = ['timestamp', 'cpu', 'percent', 'active', 'available', 'free', 'inactive', 'total', 'used', 'wired']
		df.to_csv(filename, index=False)


moni = Monitor(88694)


for i in range(2):
	moni.getData()
	time.sleep(1)

moni.toCSV()

