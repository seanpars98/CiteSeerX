

class cluster:

	def __init__(self, cluster_id):
		''' Input: The specific cluster ID of a cluster
			Output: None
			Method: Build a value dictionary with all of the relevant schema information
		'''

		self.cluster_id = cluster_id
		self.values_dict = {

			"cluster_id": self.cluster_id, 
			"included_papers": [ 
				None,
				None
			],
			"included_authors": [ 
				None,
				None
			]

		}