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
		#print('One post: {0}'.format(result.inserted_id))

	def checkIfDocExists(self, collection, idType, idValue):
		#print(self.db[collection].count_documents({idType: idValue}, limit=1) != 0)
		if self.db[collection].find({idType: idValue}).count() > 0:
			return True
		else:
			return False


	def updateAuthorHelper(self, collection, data):

		col = self.db[collection]
		response = col.update_one(
			{
				"author_id": data['author_id']
			},
			{	"$addToSet": { "clusters": { "$each": data['clusters'][0]},
					       "papers": { "$each": data['papers'][0]}
					}
			})

		#print(response.match_count)
		#print(response.upserted_id)

	def insertAuthorHelper(self, collection, data):

		col = self.db[collection]
		response = col.insert_one(data)
		#print(response)

	def upsertAuthor(self, paper, collection, db):

		for auth in paper.values_dict['authors']:

			author1 = author(auth['author_id'])

			author1.values_dict['clusters'] = [auth['cluster']]
			author1.values_dict['name'] = auth['name']
			author1.values_dict['papers'] = [paper.values_dict['paper_id']]

			author1.authors_table_fields(db)

			# Now that author is prepared, time to switch logic depending on if the
			# entry exists already
			if self.checkIfDocExists("authors", "author_id", author1.values_dict['author_id']):
				# Append paper and cluster to author entry!
				self.updateAuthorHelper(collection, author1.values_dict)
			else:
				# Insert the brand new document!
				self.insertAuthorHelper(collection, author1.values_dict)

				

	def updateClusterHelper(self, collection, data):
		col = self.db[collection]

		result = col.update_one(
			{
				"cluster_id": data['cluster_id']
			},
			{       "$addToSet": { "included_papers": { "$each": data['included_papers']},
                                               "included_authors": { "$each": data['included_authors']}
                                        }
                        })

		#result = col.update_one(dict_)
		#print(result.match_count)
		#print(result.upserted_id)

	def insertClusterHelper(self, collection, data):

		col = self.db[collection]
		response = col.insert_one(data)
		#print(response)

	def upsertCluster(self, paper, collection):
		cluster1 = cluster(paper.values_dict['cluster'])
		cluster1.values_dict['included_papers'] = [paper.values_dict['paper_id']]
		list_of_author_names = [auth['name'] for auth in paper.values_dict['authors']]
		cluster1.values_dict['included_authors'] = list_of_author_names


		if self.checkIfDocExists("clusters", "cluster_id", cluster1.values_dict['cluster_id']):
			# If the document exists, then append values
			self.updateClusterHelper(collection, cluster1.values_dict)
		else:
			# Create the document from scratch!
			self.insertClusterHelper(collection, cluster1.values_dict)

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

