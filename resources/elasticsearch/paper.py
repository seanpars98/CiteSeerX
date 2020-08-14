# Import SQL capabilities
import MySQLdb

# Import basic system libraries
import sys
import time
 
# Reload sys and make sure the encoding is set properly to utf8
reload(sys)
sys.setdefaultencoding('utf8')

class paper:

	def __init__(self, paper_id):
		''' Input: The specific paper ID of a paper
			Output: None
			Method: Build a value dictionary with all of the relevant schema information
		'''

		self.paper_id = paper_id
		self.values_dict = {

			"paper_id": self.paper_id,	
			"title": '',	
			"cluster": '', 
			"authors": [
				{
				"name": '', 
				"author_id": '', 
				"cluster": '' 
				}
			], 
			"keywords": [
				{
					"keyword": '',
					"keyword_id": '' 
				}
			], 
			"abstract": '', 
			"year": 0, 
			"venue": '', 
			"ncites": 0, 
			"scites": 0, 
			"doi": '', 
			"incol": None, 
			"authorNorms": None, 
			"text": '',
			"cites": [	
					None,
					None
			], 
			"citedby":[	
					None,
					None
			], 
			"vtime": None, 

		}


	def paper_table_fields(self, cur):
		''' Input: MySQL database connection
			Output: None
			Method: Query the MySQL database for a specific paperID and properly organize 
					the data returned in the values_dict data structure. 

		'''

		statement = "SELECT title, abstract, year, venue, ncites, selfCites, cluster, versionTime FROM papers WHERE id='" + self.paper_id + "';"

		cur.execute(statement)

		result_tuple = cur.fetchall()[0]

		self.values_dict['title'] = str(result_tuple[0])
		self.values_dict['abstract'] = str(result_tuple[1])
		if result_tuple[2]:
			self.values_dict['year'] = int(result_tuple[2])
		self.values_dict['venue'] = str(result_tuple[3])
		self.values_dict['ncites'] = int(result_tuple[4])
		self.values_dict['selfCites'] = int(result_tuple[5])
		self.values_dict['cluster'] = int(result_tuple[6])
		self.values_dict['vtime'] = result_tuple[7].strftime('%Y-%m-%d %H:%M:%S')


	def authors_table_fields(self, cur):
		''' Input: MySQL database connection
			Output: None
			Method: Query the MySQL database (authors table specifically) for a specific 
			paperID and properly organize the author data returned 
			in the values_dict data structure. 

		'''

		statement = "SELECT name, id, cluster FROM authors WHERE paperid='" + self.paper_id + "';"

		cur.execute(statement)

		result_tuple = cur.fetchall()

		for author in result_tuple:
	
			temp_dict = {	"name": str(author[0]), 
							"author_id": int(author[1]), 
							"cluster": int(author[2]) 
						}
			self.values_dict['authors'].append(temp_dict)
		
		del self.values_dict['authors'][0]
	

	def keywords_table_fields(self, cur):
		''' Input: MySQL database connection
			Output: None
			Method: Query the MySQL database (keywords table specifically) for a specific 
			paperID and properly organize the keyword data returned 
			in the values_dict data structure. 

		'''

		statement = "SELECT keyword, id FROM keywords WHERE paperid='" + self.paper_id + "';"

		cur.execute(statement)

		result_tuple = cur.fetchall()

		for keyword in result_tuple:
			temp_dict = {	"keyword": str(keyword[0]),
							"keyword_id": int(keyword[1]) 
						}
			self.values_dict['keywords'].append(temp_dict)

		del self.values_dict['keywords'][0]


	def csx_citegraph_query(self, cur):
		''' Input: MySQL database connection for the csx_citegraph database
			Output: None
			Method: Query the MySQL database for the citegraph data based off of
			clusterID.

		'''
		
		#this statement grabs the cluster ids who have cited this cluster
		statement = "SELECT citing FROM citegraph WHERE cited=" + str(self.values_dict['cluster']) + ";"
		cur.execute(statement)

		result_citedby_tuple = cur.fetchall()

		#this statement grabs the cluster ids who are cited by this cluster
		statement2 = "SELECT cited FROM citegraph WHERE citing=" + str(self.values_dict['cluster']) + ";"

		cur.execute(statement2)

		result_cites_tuple = cur.fetchall()

		self.values_dict['citedby'] = [int(cite[0]) for cite in result_citedby_tuple]
		self.values_dict['cites'] = [int(cite[0]) for cite in result_cites_tuple]


	def retrieve_full_text(self):
		''' Input: None
			Output: None
			Method: We traverse through the local filesystem to find the full text
					.txt file. Then, we open this file and populate the values
					dictionary with the full text.

		'''

		d_path = self.paper_id.split('.')
	
		text_file_path = "/mnt/rep1/%s/%s/%s/%s/%s/%s.txt" % (d_path[0], d_path[1], d_path[2], d_path[3], d_path[4], self.paper_id)
		
		try:

			with open(text_file_path, "r") as text_file:
	
				contents = text_file.read()
				resp = ''.join(contents)
				self.values_dict['text'] = str(resp)

		except IOError:
			print("full text file could not be found")


