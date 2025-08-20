#!/usr/bin/env python3
"""
Milvus Backup and Restore Tool
This tool provides functionality to backup and restore Milvus collections using Python SDK.
"""

import json
import os
import sys
import argparse
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

from pymilvus import (
    connections, 
    Collection, 
    utility,
    DataType,
    FieldSchema,
    CollectionSchema,
    Index
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MilvusBackupRestore:
    def __init__(self, host: str = "localhost", port: str = "19530", alias: str = "default"):
        """
        Initialize Milvus connection
        
        Args:
            host: Milvus server host
            port: Milvus server port
            alias: Connection alias
        """
        self.host = host
        self.port = port
        self.alias = alias
        self.connection = None
        
    def connect(self) -> bool:
        """
        Connect to Milvus server
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            connections.connect(
                alias=self.alias,
                host=self.host,
                port=self.port
            )
            logger.info(f"Connected to Milvus at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Milvus: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from Milvus server"""
        try:
            connections.disconnect(alias=self.alias)
            logger.info("Disconnected from Milvus")
        except Exception as e:
            logger.error(f"Error disconnecting: {e}")
    
    def list_collections(self) -> List[str]:
        """
        List all collections in Milvus
        
        Returns:
            List[str]: List of collection names
        """
        try:
            collections = utility.list_collections()
            logger.info(f"Found {len(collections)} collections: {collections}")
            return collections
        except Exception as e:
            logger.error(f"Error listing collections: {e}")
            return []
    
    def get_collection_schema(self, collection_name: str) -> Dict[str, Any]:
        """
        Get collection schema information
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Dict containing schema information
        """
        try:
            collection = Collection(collection_name)
            schema = collection.schema
            
            # Extract field information
            fields = []
            for field in schema.fields:
                field_info = {
                    "name": field.name,
                    "dtype": field.dtype.name if hasattr(field.dtype, 'name') else str(field.dtype),
                    "is_primary": field.is_primary,
                    "auto_id": field.auto_id,
                    "description": field.description
                }
                
                # Add dimension for vector fields
                if field.dtype in [DataType.FLOAT_VECTOR, DataType.BINARY_VECTOR]:
                    field_info["dim"] = field.params.get("dim", 0)
                
                # Add max_length for varchar fields
                if field.dtype == DataType.VARCHAR:
                    field_info["max_length"] = field.params.get("max_length", 0)
                
                fields.append(field_info)
            
            # Get index information
            indexes = []
            try:
                for field in schema.fields:
                    if field.dtype in [DataType.FLOAT_VECTOR, DataType.BINARY_VECTOR]:
                        index_info = collection.index(field.name)
                        if index_info:
                            indexes.append({
                                "field_name": field.name,
                                "index_type": index_info.params.get("index_type", ""),
                                "metric_type": index_info.params.get("metric_type", ""),
                                "params": index_info.params
                            })
            except Exception as e:
                logger.warning(f"Could not retrieve index info for {collection_name}: {e}")
            
            return {
                "collection_name": collection_name,
                "description": schema.description,
                "fields": fields,
                "indexes": indexes,
                "auto_id": schema.auto_id,
                "num_entities": collection.num_entities
            }
        except Exception as e:
            logger.error(f"Error getting schema for collection {collection_name}: {e}")
            return {}
    
    def backup_collection(self, collection_name: str, output_dir: str = "backups") -> bool:
        """
        Backup a single collection
        
        Args:
            collection_name: Name of the collection to backup
            output_dir: Directory to save backup files
            
        Returns:
            bool: True if backup successful, False otherwise
        """
        try:
            logger.info(f"Starting backup of collection: {collection_name}")
            
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Get collection schema
            schema_info = self.get_collection_schema(collection_name)
            if not schema_info:
                logger.error(f"Could not retrieve schema for {collection_name}")
                return False
            
            # Get collection data
            collection = Collection(collection_name)
            collection.load()
            
            # Query all data (be careful with large collections)
            # For very large collections, you might want to implement pagination
            try:
                results = collection.query(
                    expr="",
                    output_fields=["*"],
                    limit=16384  # Milvus default limit
                )
                
                # If collection has more data, implement pagination
                total_entities = collection.num_entities
                if total_entities > 16384:
                    logger.warning(f"Collection {collection_name} has {total_entities} entities. "
                                 f"Only first 16384 entities will be backed up. "
                                 f"Consider implementing pagination for complete backup.")
                
            except Exception as e:
                logger.error(f"Error querying collection {collection_name}: {e}")
                return False
            
            # Create backup data structure
            backup_data = {
                "metadata": {
                    "collection_name": collection_name,
                    "backup_timestamp": datetime.now().isoformat(),
                    "total_entities": len(results),
                    "milvus_version": "2.x"  # Update as needed
                },
                "schema": schema_info,
                "data": results
            }
            
            # Save to JSON file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{collection_name}_backup_{timestamp}.json"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Backup completed: {filepath}")
            logger.info(f"Backed up {len(results)} entities from collection {collection_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error backing up collection {collection_name}: {e}")
            return False
    
    def backup_all_collections(self, output_dir: str = "backups") -> bool:
        """
        Backup all collections in Milvus
        
        Args:
            output_dir: Directory to save backup files
            
        Returns:
            bool: True if all backups successful, False otherwise
        """
        collections = self.list_collections()
        if not collections:
            logger.warning("No collections found to backup")
            return True
        
        success_count = 0
        for collection_name in collections:
            if self.backup_collection(collection_name, output_dir):
                success_count += 1
        
        logger.info(f"Backup completed: {success_count}/{len(collections)} collections backed up successfully")
        return success_count == len(collections)
    
    def restore_collection(self, backup_file: str, force: bool = False) -> bool:
        """
        Restore a collection from backup file
        
        Args:
            backup_file: Path to the backup JSON file
            force: If True, drop existing collection before restore
            
        Returns:
            bool: True if restore successful, False otherwise
        """
        try:
            logger.info(f"Starting restore from backup file: {backup_file}")
            
            # Load backup data
            with open(backup_file, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            collection_name = backup_data["metadata"]["collection_name"]
            schema_info = backup_data["schema"]
            data = backup_data["data"]
            
            logger.info(f"Restoring collection: {collection_name}")
            logger.info(f"Backup contains {len(data)} entities")
            
            # Check if collection exists
            if utility.has_collection(collection_name):
                if force:
                    logger.warning(f"Collection {collection_name} exists. Dropping it due to force=True")
                    utility.drop_collection(collection_name)
                else:
                    logger.error(f"Collection {collection_name} already exists. Use force=True to overwrite")
                    return False
            
            # Create collection schema
            fields = []
            for field_info in schema_info["fields"]:
                # Map string dtype back to DataType enum
                dtype_mapping = {
                    "INT64": DataType.INT64,
                    "INT32": DataType.INT32,
                    "INT16": DataType.INT16,
                    "INT8": DataType.INT8,
                    "BOOL": DataType.BOOL,
                    "FLOAT": DataType.FLOAT,
                    "DOUBLE": DataType.DOUBLE,
                    "STRING": DataType.STRING,
                    "VARCHAR": DataType.VARCHAR,
                    "FLOAT_VECTOR": DataType.FLOAT_VECTOR,
                    "BINARY_VECTOR": DataType.BINARY_VECTOR,
                    "JSON": DataType.JSON
                }
                
                dtype = dtype_mapping.get(field_info["dtype"], DataType.NONE)
                if dtype == DataType.NONE:
                    logger.error(f"Unknown data type: {field_info['dtype']}")
                    return False
                
                # Create field schema
                field_params = {}
                if "dim" in field_info:
                    field_params["dim"] = field_info["dim"]
                if "max_length" in field_info:
                    field_params["max_length"] = field_info["max_length"]
                
                field = FieldSchema(
                    name=field_info["name"],
                    dtype=dtype,
                    is_primary=field_info.get("is_primary", False),
                    auto_id=field_info.get("auto_id", False),
                    description=field_info.get("description", ""),
                    **field_params
                )
                fields.append(field)
            
            # Create collection
            schema = CollectionSchema(
                fields=fields,
                description=schema_info.get("description", ""),
                auto_id=schema_info.get("auto_id", False)
            )
            
            collection = Collection(collection_name, schema)
            logger.info(f"Collection {collection_name} created successfully")
            
            # Insert data
            if data:
                collection.insert(data)
                logger.info(f"Inserted {len(data)} entities")
            
            # Create indexes
            for index_info in schema_info.get("indexes", []):
                try:
                    collection.create_index(
                        field_name=index_info["field_name"],
                        index_params={
                            "index_type": index_info["index_type"],
                            "metric_type": index_info["metric_type"],
                            "params": index_info.get("params", {})
                        }
                    )
                    logger.info(f"Created index on field {index_info['field_name']}")
                except Exception as e:
                    logger.warning(f"Could not create index on {index_info['field_name']}: {e}")
            
            logger.info(f"Collection {collection_name} restored successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error restoring collection from {backup_file}: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description="Milvus Backup and Restore Tool")
    parser.add_argument("--host", default="localhost", help="Milvus host")
    parser.add_argument("--port", default="19530", help="Milvus port")
    parser.add_argument("--action", choices=["backup", "restore", "list"], required=True,
                       help="Action to perform")
    parser.add_argument("--collection", help="Collection name (for single collection backup)")
    parser.add_argument("--output-dir", default="backups", help="Output directory for backups")
    parser.add_argument("--backup-file", help="Backup file path (for restore)")
    parser.add_argument("--force", action="store_true", help="Force overwrite existing collection")
    
    args = parser.parse_args()
    
    # Initialize backup/restore tool
    tool = MilvusBackupRestore(host=args.host, port=args.port)
    
    if not tool.connect():
        sys.exit(1)
    
    try:
        if args.action == "list":
            collections = tool.list_collections()
            print("\nAvailable collections:")
            for i, collection in enumerate(collections, 1):
                print(f"{i}. {collection}")
                
        elif args.action == "backup":
            if args.collection:
                success = tool.backup_collection(args.collection, args.output_dir)
            else:
                success = tool.backup_all_collections(args.output_dir)
            
            if not success:
                sys.exit(1)
                
        elif args.action == "restore":
            if not args.backup_file:
                logger.error("--backup-file is required for restore action")
                sys.exit(1)
            
            success = tool.restore_collection(args.backup_file, args.force)
            if not success:
                sys.exit(1)
                
    finally:
        tool.disconnect()

if __name__ == "__main__":
    main()


'''
1. List all collections
python milvus_backup_restore.py --action list --host localhost --port 19530

2. Backup a specific collection
python milvus_backup_restore.py --action backup --collection my_collection --output-dir ./backups

3. Backup all collections
python milvus_backup_restore.py --action backup --output-dir ./backups

4. Restore a collection from backup
python milvus_backup_restore.py --action restore --backup-file ./backups/my_collection_backup_20240101_120000.json

5. Force restore (overwrite existing collection)
python milvus_backup_restore.py --action restore --backup-file ./backups/my_collection_backup_20240101_120000.json --force


'''