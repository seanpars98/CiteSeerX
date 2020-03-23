# Import SQL capabilities
import MySQLdb

# Import ElasticSearch capabilities
#import elasticpython

# Import MongoDB capabilities
from mongo import Mongo

# Import each of the schemas and associated methods for each index
from paper import paper
from author import author
from cluster import cluster
from monitoring import Monitor


def get_ids(cur, n):	
	''' Input: Database cursor (database connection), n number of papers to retrieve
		Output: Returns a list of first 'n' number of paper ids from the SQL DB 
		Method: Queries the database for the paper ids and returns a list of length 'n'

	'''
	statement = "SELECT id FROM papers LIMIT %d;" % (n)
	cur.execute(statement)
	return [tup[0] for tup in cur.fetchall()]

def connect_to_citeseerx_db():
	''' Input: None
		Output: Returns the cursor (connection) to the citeseerx database
		Method: Using the python MySQL API, establishes a connection with the citeseerx DB

	'''
	db = MySQLdb.connect(host="csxdb02.ist.psu.edu",
                        user="csx-prod",
                        passwd="csx-prod",
                        db="citeseerx",
			charset='utf8')

	return db.cursor()

def connect_to_csx_citegraph():
	''' Input: None
		Output: Returns the cursor (connection) to the csx_citegraph DB
		Method: Using the python MySQL API, connects to the csx_citegraph database

	'''
	db = MySQLdb.connect(host="csxdb02.ist.psu.edu",
                        user="csx-prod",
                        passwd="csx-prod",
                        db="csx_citegraph",
			charset='utf8')
	return db.cursor()

if __name__ == "__main__":
	''' Main Method
		Method: Call all above methods then sets the number of papers to index.
				Iterates through each paper and indexes the paper, all authors, and the cluster
				of said paper.


	'''
	# Establish connections to databases and ElasticSearch
	citeseerx_db_cur = connect_to_citeseerx_db()
	csx_citegraph_cur = connect_to_csx_citegraph()

	#es = elasticpython.establish_ES_connection()

	mongo = Mongo()
	try:
		mongo.establishMongoConnection()
	except:
		print('Connection to Mongo could not be made')

	#elasticpython.test_ES_connection()

	# Set the number of papers to index by this migration script
	number_of_papers_to_index = 200000

	# Input the process ID of the MongoDB Process!
	moni = Monitor(9978)

	# Retrieve the list of paper ids
	list_of_paper_ids = get_ids(citeseerx_db_cur, number_of_papers_to_index)

	# Set counter so we can keep track of how many papers have migrated in real-time
	paper_count = 0

	# Iterate through each of the paper_ids selected and add them to the index
	for paper_id in list_of_paper_ids:

		# Every 100 papers print out our current progress
		if paper_count % 100 == 0:
			print('Total paper count: ', str(paper_count))
		
		# Every 10,000 papers, record the metrics we want
		if paper_count % 10000 == 0:
			moni.getData()


		# Extract all the fields neccessary for the paper type from the MySQL DBs
		paper1 = paper(paper_id)
		paper1.paper_table_fields(citeseerx_db_cur)
		paper1.authors_table_fields(citeseerx_db_cur)
		paper1.keywords_table_fields(citeseerx_db_cur)
		paper1.csx_citegraph_query(csx_citegraph_cur)
		paper1.retrieve_full_text()

		# Load the paper JSON data into ElasticSearch
		#elasticpython.create_document(es, index='citeseerx', doc_id=paper1.values_dict['paper_id'], doc_type='paper', data=paper1.values_dict)

		# THIS IS WHERE THE MONGO INGESTION TAKES PLACE
		mongo.createDocument("papers", paper1.values_dict)

		# We also need to update the other indices like author and cluster
		# By using the update and upserts command in ElasticSearch, we can do this easily
		#authorHelperUpsert(paper1, citeseerx_db_cur)
		#clusterHelperUpsert(paper1)
		mongo.upsertAuthor(paper1, "authors", citeseerx_db_cur)
		mongo.upsertCluster(paper1, "clusters")

		# Increment counter so we can keep track of migration progress
		paper_count += 1

	moni.toCSV()
