"""
Graph embeddings and machine learning for ResilienceAI.
"""

import numpy as np
from typing import List, Dict, Any, Tuple, Optional
import torch
import torch.nn as nn
from app.infrastructure.graph.neo4j_manager import get_neo4j_manager


class GraphEmbeddingService:
    """Generate and manage graph embeddings."""
    
    def __init__(self):
        self.manager = get_neo4j_manager()
    
    def generate_fastRP_embeddings(
        self,
        graph_name: str = "county-network",
        embedding_dim: int = 128
    ) -> List[Dict[str, Any]]:
        """Generate FastRP node embeddings."""
        query = """
        CALL gds.fastRP.stream($graph_name, {
            embeddingDimension: $dim,
            iterationWeights: [0.0, 1.0, 1.0]
        })
        YIELD nodeId, embedding
        RETURN 
            gds.util.asNode(nodeId).fips_code AS node_id,
            gds.util.asNode(nodeId).name AS name,
            embedding
        """
        
        return self.manager.execute_read(query, {
            "graph_name": graph_name,
            "dim": embedding_dim
        })
    
    def generate_graphSAGE_embeddings(
        self,
        graph_name: str = "county-network",
        model_name: str = "county-sage-model",
        embedding_dim: int = 64
    ) -> List[Dict[str, Any]]:
        """Generate GraphSAGE embeddings."""
        # Train model if not exists
        train_query = """
        CALL gds.beta.graphSage.train($graph_name, {
            modelName: $model_name,
            featureProperties: ['risk_score', 'population', 'resilience_score'],
            embeddingDimension: $dim,
            aggregator: 'mean',
            activationFunction: 'sigmoid'
        })
        YIELD modelInfo
        RETURN modelInfo
        """
        
        try:
            self.manager.execute_write(train_query, {
                "graph_name": graph_name,
                "model_name": model_name,
                "dim": embedding_dim
            })
        except:
            pass  # Model may already exist
        
        # Generate embeddings
        embed_query = """
        CALL gds.beta.graphSage.stream($graph_name, {
            modelName: $model_name
        })
        YIELD nodeId, embedding
        RETURN 
            gds.util.asNode(nodeId).fips_code AS node_id,
            embedding
        """
        
        return self.manager.execute_read(embed_query, {
            "graph_name": graph_name,
            "model_name": model_name
        })
    
    def find_similar_nodes(
        self,
        node_id: str,
        embedding_type: str = "fastRP",
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """Find similar nodes using embeddings."""
        # Get embedding for target node
        query = """
        MATCH (c:County {fips_code: $node_id})
        RETURN c.embedding AS embedding
        """
        
        result = self.manager.execute_read(query, {"node_id": node_id})
        if not result or not result[0]['embedding']:
            return []
        
        target_embedding = np.array(result[0]['embedding'])
        
        # Find similar nodes using cosine similarity
        similarity_query = """
        MATCH (c:County)
        WHERE c.fips_code <> $node_id AND c.embedding IS NOT NULL
        RETURN 
            c.fips_code AS fips,
            c.name AS name,
            c.embedding AS embedding,
            gds.similarity.cosine($target_embedding, c.embedding) AS similarity
        ORDER BY similarity DESC
        LIMIT $top_k
        """
        
        return self.manager.execute_read(similarity_query, {
            "node_id": node_id,
            "target_embedding": target_embedding.tolist(),
            "top_k": top_k
        })
    
    def store_embeddings(self, graph_name: str, embedding_type: str = "fastRP") -> int:
        """Store embeddings as node properties."""
        query = """
        CALL gds.fastRP.stream($graph_name, {
            embeddingDimension: 128
        })
        YIELD nodeId, embedding
        WITH gds.util.asNode(nodeId) AS node, embedding
        SET node.embedding = embedding
        RETURN count(*) AS stored
        """
        
        result = self.manager.execute_write(query, {"graph_name": graph_name})
        return result[0]['stored'] if result else 0


class GraphNeuralNetwork(nn.Module):
    """PyTorch Geometric GNN for node classification."""
    
    def __init__(self, in_channels: int, hidden_channels: int, out_channels: int):
        super().__init__()
        self.conv1 = nn.Linear(in_channels, hidden_channels)
        self.conv2 = nn.Linear(hidden_channels, out_channels)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.5)
    
    def forward(self, x, edge_index):
        x = self.conv1(x)
        x = self.relu(x)
        x = self.dropout(x)
        x = self.conv2(x)
        return x


class NodeClassifier:
    """Node classification using graph embeddings."""
    
    def __init__(self):
        self.manager = get_neo4j_manager()
        self.model = None
    
    def prepare_training_data(
        self,
        graph_name: str,
        label_property: str = "risk_level"
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Prepare training data from graph."""
        # Get embeddings and labels
        query = f"""
        MATCH (c:County)
        WHERE c.embedding IS NOT NULL AND c.{label_property} IS NOT NULL
        RETURN 
            c.embedding AS embedding,
            c.{label_property} AS label,
            id(c) AS node_id
        """
        
        results = self.manager.execute_read(query)
        
        # Convert to tensors
        embeddings = torch.tensor([r['embedding'] for r in results], dtype=torch.float32)
        
        # Encode labels
        label_map = {label: idx for idx, label in enumerate(set(r['label'] for r in results))}
        labels = torch.tensor([label_map[r['label']] for r in results], dtype=torch.long)
        
        # Node IDs for edge index
        node_ids = torch.tensor([r['node_id'] for r in results], dtype=torch.long)
        
        return embeddings, labels, node_ids
    
    def train(self, graph_name: str, epochs: int = 100) -> Dict[str, Any]:
        """Train node classifier."""
        X, y, node_ids = self.prepare_training_data(graph_name)
        
        # Initialize model
        self.model = GraphNeuralNetwork(
            in_channels=X.shape[1],
            hidden_channels=64,
            out_channels=len(set(y.tolist()))
        )
        
        optimizer = torch.optim.Adam(self.model.parameters(), lr=0.01)
        criterion = nn.CrossEntropyLoss()
        
        # Training loop
        for epoch in range(epochs):
            self.model.train()
            optimizer.zero_grad()
            
            # Forward pass (simplified - no actual graph convolution)
            out = self.model(X, None)
            loss = criterion(out, y)
            
            loss.backward()
            optimizer.step()
            
            if epoch % 10 == 0:
                print(f"Epoch {epoch}, Loss: {loss.item():.4f}")
        
        return {"trained": True, "epochs": epochs, "final_loss": loss.item()}
    
    def predict(self, node_embedding: List[float]) -> Dict[str, Any]:
        """Predict label for a node."""
        if self.model is None:
            return {"error": "Model not trained"}
        
        self.model.eval()
        with torch.no_grad():
            x = torch.tensor([node_embedding], dtype=torch.float32)
            out = self.model(x, None)
            probs = torch.softmax(out, dim=1)
            predicted = torch.argmax(probs, dim=1)
        
        return {
            "prediction": predicted.item(),
            "confidence": probs.max().item(),
            "probabilities": probs.tolist()[0]
        }
