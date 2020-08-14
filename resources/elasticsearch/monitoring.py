import psutil
from datetime import datetime
from pprint import pprint
import csv
import time
import pandas as pd
import pickle

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
		
		with open('cpus.p', 'wb') as f:
			pickle.dump(self.cpu_usage, f)
	
		with open('mem.p', 'wb') as f:
			pickle.dump(self.memory_usage, f)
		
	lines = []
	avail = 'available'
	for i in range(len(self.cpu_usage['cpu_usage'])):
		temp = str(self.cpu_usage['cpu_usage'][i][0]) + ',' + str(self.cpu_usage['cpu_usage'][i][1]) + ',' 
		temp += str(self.memory_usage['memory_usage'][i][1]['percent']) + ',' + str(self.memory_usage['memory_usage'][i][1]['active']) + ',' 
		temp += str(self.memory_usage['memory_usage'][i][1][avail]) + ',' + str(self.memory_usage['memory_usage'][i][1]['free']) + ','
		temp += str(self.memory_usage['memory_usage'][i][1]['inactive']) + ',' + str(self.memory_usage['memory_usage'][i][1]['total']) + ','
		temp += str(self.memory_usage['memory_usage'][i][1]['used'])
		lines.append(temp)

		filename = str(self.pid) + '.csv'
		
		with open(filename, 'w') as f:
			w = csv.writer(f, delimiter=',')
			w.writerows([x.split(',') for x in lines])

		df = pd.read_csv(filename)
		df.columns = ['timestamp', 'cpu', 'percent', 'active', 'available', 'free', 'inactive', 'total', 'used']
		df.to_csv(filename, index=False)

