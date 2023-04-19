
from typing import Any, Callable, Optional, Union
from pymilvus import Collection, utility, connections, DataType
from copy import deepcopy
import threading
import logging

logger = logging.getLogger(__name__)


class MilvusClient:
    def __init__(
        self,
        pk_field: str = None,
        vector_field: str = None,
        connection_address: str = 'localhost:19530', # Assume connection handling will allow to connect to any instance type based on one string
        collection_name: str = "ClientCollection",
        shards: int = 2,
        partitions: list[str] = [],
        consistency_level: str = "Session",
        replica_count: int = 1,
        index_params: dict = {},
        search_params: dict = {},
        timeout: Optional[int] = None,
        drop_old: bool = False,
    ):
        
        self.connection_address = connection_address
        self.collection_name = collection_name
        self.shards = shards
        self.partitions = partitions
        self.consistency_level = consistency_level
        self.replica_count = replica_count
        self.index_params = index_params
        self.search_params = search_params
        self.timeout = timeout

        self.alias = self._generate_alias()
        
        self.collection = None
        self.pk_field = pk_field
        self.vector_field = vector_field
        self.auto_id = None
        # TODO: If moving back to 3.6, use ordereddict
        self.fields = {}
        self.collection_lock = threading.RLock()

        if drop_old:
            self.delete_collection(drop_collection=True)
        
        if utility.has_collection(self.collection_name):
            self._init()

    
    def insert_data(
        self,
        embeddings: list[any],
        metdata: list[dict[str, any]] = None,
        timeout: int = None,
        batch_size: int = 100,
        progress_bar: bool = False,
    ) -> list[Union[str, int]]:
        raise NotImplementedError
    
    def upsert_data(
        self,
        data: list[any],
        metdata: list[dict[str, any]] = None,
        timeout: int = None,
        batch_size: int = 100,
        progress_bar: bool = False,
    ) -> list[Union[str, int]]:
        raise NotImplementedError


    def delete_data(
        self,
        expression,
    ) -> int:
        raise NotImplementedError
    
    def delete_collection(
        self,
        drop_collection = False,
    ) -> None:
        with self.collection_lock:
            if utility.has_collection(self.collection_name, using=self.alias):
                utility.drop_collection(self.collection_name, using=self.alias)
                self.collection = None
            if drop_collection == False:
                self._init()
        

    def _generate_alias(self):
        raise NotImplementedError
    
    def _init(self):
        raise NotImplementedError
    
    def _init_existing(self):
        with self.collection_lock:
            self.collection = Collection(self.collection_name)
            self._extract_fields()
            self._create_index()

    def _extract_fields(self) -> None:
        """Grab the existing fields from the Collection"""
        if isinstance(self.collection, Collection):
            schema = self.collection.schema
            for field in schema.fields:
                field_dict = field.to_dict()
                if field_dict.get("is_primary", None) is not None:
                    if self.pk_field is not None:
                        logger.debug("Replacing pk_field provided with one from collection.")
                    self.pk_field = field_dict["name"]
                    self.auto_id = field_dict["auto_id"]
                if field["type"] in (DataType.FLOAT_VECTOR, DataType.BINARY_VECTOR):
                    if self.vector_field is not None:
                        logger.debug("Replacing vector_field provided with one from collection.")
                    self.vector_field = field["name"]
                self.fields[field_dict["name"]] = field_dict["type"]


    def _create_index(self) -> None:
        """Create a index on the collection"""
        if isinstance(self.collection, Collection) and self._get_index() is None:
            try:
                # If no index params, use a default HNSW based one
                if self.index_params is None:
                    self.index_params = {
                        "metric_type": "L2",
                        "index_type": "HNSW",
                        "params": {"M": 8, "efConstruction": 64},
                    }

                try:
                    self.col.create_index(
                        self._vector_field,
                        index_params=self.index_params,
                        using=self.alias,
                    )

                # If default did not work, most likely on Zilliz Cloud
                except MilvusException:
                    # Use AUTOINDEX based index
                    self.index_params = {
                        "metric_type": "L2",
                        "index_type": "AUTOINDEX",
                        "params": {},
                    }
                    self.col.create_index(
                        self._vector_field,
                        index_params=self.index_params,
                        using=self.alias,
                    )
                logger.debug(
                    "Successfully created an index on collection: %s",
                    self.collection_name,
                )

            except MilvusException as e:
                logger.error(
                    "Failed to create an index on collection: %s", self.collection_name
                )
                raise e
    def _get_index(self):
        if isinstance(self.col, Collection):
            for x in self.col.indexes:
                if x.field_name == self._vector_field:
                    return x.to_dict()
        return None

        

if __name__ == "__main__":
    pass