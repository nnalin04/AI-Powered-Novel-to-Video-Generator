import json
import os
from typing import List, Dict
import chromadb
from ai_film_studio.providers.factory import ProviderFactory

class MemoryStore:
    def __init__(self):
        # Initialize chroma DB client (embedded)
        os.makedirs("assets/db", exist_ok=True)
        self.client = chromadb.PersistentClient(path="assets/db")
        self.embedding_provider = ProviderFactory.get_embedding()
        
        # Get or create the main collection
        self.collection = self.client.get_or_create_collection(
            name="film_studio_assets"
        )

    async def add_asset(self, name: str, asset_type: str, metadata: Dict, context_text: str):
        """Stores an asset with its embedding."""
        try:
            # We get the embedding manually to keep the embedding provider pattern
            embedding = await self.embedding_provider.get_embedding(context_text)
            
            # ChromaDB requires string IDs. We'll use a hash or composite of name and type.
            # Convert any complex objects in metadata to strings since Chroma expects strings/ints/floats
            safe_metadata = {}
            for k, v in metadata.items():
                if isinstance(v, (dict, list)):
                    safe_metadata[k] = json.dumps(v)
                else:
                    safe_metadata[k] = v
                    
            safe_metadata["asset_type"] = asset_type
            safe_metadata["name"] = name
            
            # Generate ID
            asset_id = str(hash(name + asset_type + context_text))
            
            # Add to chromadb
            self.collection.add(
                embeddings=[embedding],
                documents=[context_text],
                metadatas=[safe_metadata],
                ids=[asset_id]
            )
            print(f"Memory: Added asset {name} ({asset_type})")
        except Exception as e:
            print(f"Memory Add Error: {e}")

    async def search_assets(self, query: str, asset_type: str = "character", limit: int = 1) -> List[Dict]:
        """Searches for assets semantically using ChromaDB."""
        try:
            embedding = await self.embedding_provider.get_embedding(query)
            
            # Search chromadb
            results = self.collection.query(
                query_embeddings=[embedding],
                n_results=limit,
                where={"asset_type": asset_type} # Filter by asset type
            )
            
            hits = []
            if results["ids"] and len(results["ids"]) > 0:
                # results returned by Chroma are lists of lists
                for i in range(len(results["ids"][0])):
                    doc_metadata = results["metadatas"][0][i]
                    
                    # Convert stringified lists/dicts back to objects in metadata
                    parsed_metadata = {}
                    for k, v in doc_metadata.items():
                        if isinstance(v, str) and (v.startswith('{') or v.startswith('[')):
                            try:
                                parsed_metadata[k] = json.loads(v)
                            except:
                                parsed_metadata[k] = v
                        else:
                            parsed_metadata[k] = v

                    # Distances are returned by query, lower is better
                    distance = results["distances"][0][i] if results["distances"] else 0.0
                    
                    hits.append({
                        "name": doc_metadata.get("name", "Unknown"),
                        "type": doc_metadata.get("asset_type", asset_type),
                        "metadata": parsed_metadata,
                        "distance": distance
                    })
                    
            return hits
        except Exception as e:
            print(f"Memory Search Error: {e}")
            return []

memory_store = MemoryStore()
