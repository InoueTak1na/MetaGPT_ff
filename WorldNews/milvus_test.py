from pymilvus import connections
from pymilvus import FieldSchema, CollectionSchema, DataType, Collection

connections.connect("default", host="127.0.0.1", port="19530")

print("Connected to Milvus")

field1 = FieldSchema(name="id", dtype=DataType.INT64, is_primary=True)
field2 = FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1536)

schema = CollectionSchema(fields=[field1, field2], description="Test collection")

collection = Collection("test_collection", schema)

print("Collection created")

import numpy as np

data = [
    [i for i in range(10)],
    [np.random.rand(1536).tolist() for _ in range(10)],
]

collection.insert(data)

print("Data inserted")

index_params = {
    "metric_type": "COSINE",
    "index_type": "IVF_FLAT",
    "params": {"nlist": 128}
}
collection.create_index("embedding", index_params)
print("Index created")

collection.load()

query_vectors = [np.random.rand(1536).tolist()]
search_params = {"metric_type": "COSINE", "params": {"nprobe": 10}}

results = collection.search(query_vectors, "embedding", search_params, limit=5)

print("Results: ", results)
