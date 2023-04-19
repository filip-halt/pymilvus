"""Default vectorstore args."""

DEFAULT_COLLECTION_ARGS = {
    "collection_name": "ClientStore",
}
DEFAULT_LOAD_ARGS = {
    "partition": None,
    "replica_count": 1,
}

DEFAULT_CONNECTION_ARGS ={
    "alias": 'default',
    
}
 
DEFAULT_SEARCH_PARAMS = {
    "IVF_FLAT": {"metric_type": "L2", "params": {"nprobe": 10}},
    "IVF_SQ8": {"metric_type": "L2", "params": {"nprobe": 10}},
    "IVF_PQ": {"metric_type": "L2", "params": {"nprobe": 10}},
    "HNSW": {"metric_type": "L2", "params": {"ef": 10}},
    "RHNSW_FLAT": {"metric_type": "L2", "params": {"ef": 10}},
    "RHNSW_SQ": {"metric_type": "L2", "params": {"ef": 10}},
    "RHNSW_PQ": {"metric_type": "L2", "params": {"ef": 10}},
    "IVF_HNSW": {"metric_type": "L2", "params": {"nprobe": 10, "ef": 10}},
    "ANNOY": {"metric_type": "L2", "params": {"search_k": 10}},
    "AUTOINDEX": {"metric_type": "L2", "params": {}},
}
