from pymongo import MongoClient
from pprint import pprint
from paper import paper
from author import author
from cluster import cluster
from monitoring import Monitor

class Mongo():

	def __init__(self):
		self.client = None
		self.db = None

	def establishMongoConnection(self):
		client = MongoClient('localhost', 27017)
		self.client = client
		self.db = self.client['citeseerx']

	def getCollection(self, colName):
		collection = self.db[colName]
		return collection

	def createDocument(self, collection, data):
		col = self.db[collection]

		# Did not assign ID, therefore mongo will give us a generated one
		result = col.insert_one(data)
		print('One post: {0}'.format(result.inserted_id))

	def upsertAuthorHelper(self, collection, data):

		col = self.db[collection]
		pprint(data)
		print(data['papers'])
		print(type(data['papers']))
		response = col.update_one(
			{
				"author_id": data['author_id']
			},

			{
				"$setOnInsert": {
									"papers": [],
									"author_id": data['author_id'],
	            					"cluster": [],
	            					"name": data['name'],
									"affiliation": data['affiliation'],
									"address": data['address'],
									"email": data['email']
								},
				"$push": 
								{
									"cluster": data['clusters'][0],
									"papers": data['papers'][0]
									
								}

							},
			upsert=True)

		#result = col.update_one(dict_)
		print(result.match_count)
		print(result.upserted_id)

	def upsertAuthor(self, paper, collection, db):

		for auth in paper.values_dict['authors']:

			author1 = author(auth['author_id'])

			author1.values_dict['clusters'] = [auth['cluster']]
			author1.values_dict['name'] = auth['name']
			author1.values_dict['papers'] = [paper.values_dict['paper_id']]

			author1.authors_table_fields(db)

			self.upsertAuthorHelper(collection, author1.values_dict)


	def upsertClusterHelper(self, collection, data):
		col = self.db[collection]

		dict_ = {

			{
				"cluster_id": data['cluster_id']
			},

			{
				"$setOnInsert": {
									#"papers": data['papers'],
									"cluster_id": data['cluster_id'],
									"included_papers": [],
									"included_authors": []

								},
				"$push": 
								{

									{
										"included_papers": data['included_papers']
									},

									{
										"included_authors": data['included_authors']
									}
								}

							},
			{"upsert": True}
		}

		result = col.update_one(dict_)
		print(result.match_count)
		print(result.upserted_id)



	def upsertCluster(self, paper, collection):
		cluster1 = cluster(paper.values_dict['cluster'])
		cluster1.values_dict['included_papers'] = [paper.values_dict['paper_id']]
		list_of_author_names = [auth['name'] for auth in paper.values_dict['authors']]
		cluster1.values_dict['included_authors'] = list_of_author_names
		self.upsertClusterHelper(collection, cluster1.values_dict)

'''

mongo1 = Mongo()
mongo1.establishMongoConnection()
papers = mongo1.getCollection("papers")

post_data = {
	'title': 'Python and MongoDB',
	'content': 'PyMongo is fun, you guys',
	'author': 'Scott'
}

post_data['_id'] = 1234

mongo1.createDocument(papers, post_data)

'''

