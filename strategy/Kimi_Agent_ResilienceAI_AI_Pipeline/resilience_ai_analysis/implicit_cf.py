"""
Implicit Feedback Collaborative Filtering
For cases where explicit ratings are not available
"""

import numpy as np
from scipy.sparse import csr_matrix
from typing import Dict, List, Optional, Tuple


class ImplicitCollaborativeFiltering:
    """Implicit feedback collaborative filtering using ALS"""
    
    def __init__(
        self,
        factors: int = 50,
        regularization: float = 0.01,
        iterations: int = 30,
        use_gpu: bool = False
    ):
        self.factors = factors
        self.regularization = regularization
        self.iterations = iterations
        self.use_gpu = use_gpu
        self.model = None
        self.item_factors = None
        self.user_factors = None
        self.user_mapping = {}
        self.item_mapping = {}
    
    def fit(self, interaction_matrix: csr_matrix) -> None:
        """Train implicit ALS model"""
        
        try:
            import implicit
            
            # Initialize model
            self.model = implicit.als.AlternatingLeastSquares(
                factors=self.factors,
                regularization=self.regularization,
                iterations=self.iterations,
                use_gpu=self.use_gpu
            )
            
            # Fit model
            self.model.fit(interaction_matrix)
            
            # Store factors
            self.user_factors = self.model.user_factors
            self.item_factors = self.model.item_factors
            
        except ImportError:
            print("implicit library not available, using basic implementation")
            self._fit_basic_als(interaction_matrix)
    
    def _fit_basic_als(self, interaction_matrix: csr_matrix) -> None:
        """Basic ALS implementation without implicit library"""
        
        n_users, n_items = interaction_matrix.shape
        
        # Initialize factors randomly
        self.user_factors = np.random.normal(0, 0.01, (n_users, self.factors))
        self.item_factors = np.random.normal(0, 0.01, (n_items, self.factors))
        
        # Convert to dense for simplicity (not recommended for large matrices)
        R = interaction_matrix.toarray()
        
        # Confidence weights (for implicit feedback)
        alpha = 40  # Confidence scaling factor
        C = 1 + alpha * R
        
        # ALS iterations
        for iteration in range(self.iterations):
            # Fix items, solve for users
            for u in range(n_users):
                # Get items user has interacted with
                items = np.where(R[u] > 0)[0]
                
                if len(items) == 0:
                    continue
                
                # Build system
                A = self.item_factors[items].T @ np.diag(C[u, items]) @ self.item_factors[items]
                A += self.regularization * np.eye(self.factors)
                
                b = self.item_factors[items].T @ (C[u, items] * R[u, items])
                
                # Solve
                self.user_factors[u] = np.linalg.solve(A, b)
            
            # Fix users, solve for items
            for i in range(n_items):
                # Get users who interacted with item
                users = np.where(R[:, i] > 0)[0]
                
                if len(users) == 0:
                    continue
                
                # Build system
                A = self.user_factors[users].T @ np.diag(C[users, i]) @ self.user_factors[users]
                A += self.regularization * np.eye(self.factors)
                
                b = self.user_factors[users].T @ (C[users, i] * R[users, i])
                
                # Solve
                self.item_factors[i] = np.linalg.solve(A, b)
            
            if (iteration + 1) % 5 == 0:
                # Calculate reconstruction error
                pred = self.user_factors @ self.item_factors.T
                error = np.sum((R - pred) ** 2)
                print(f"Iteration {iteration + 1}, Error: {error:.4f}")
    
    def recommend(
        self,
        user_id: int,
        interaction_matrix: csr_matrix,
        n_recommendations: int = 10,
        filter_already_liked: bool = True
    ) -> List[Tuple[int, float]]:
        """Generate recommendations for a user"""
        
        if self.model is not None:
            # Use implicit library
            recommendations = self.model.recommend(
                userid=user_id,
                user_items=interaction_matrix,
                N=n_recommendations,
                filter_already_liked_items=filter_already_liked,
                recalculate_user=True
            )
            return recommendations
        else:
            # Use basic implementation
            user_vector = self.user_factors[user_id:user_id+1]
            scores = user_vector @ self.item_factors.T
            scores = scores.flatten()
            
            if filter_already_liked:
                # Filter already liked items
                user_items = interaction_matrix[user_id].toarray().flatten()
                scores[user_items > 0] = -np.inf
            
            # Get top recommendations
            top_indices = np.argsort(scores)[::-1][:n_recommendations]
            
            return [(int(idx), float(scores[idx])) for idx in top_indices]
    
    def similar_items(
        self,
        item_id: int,
        n_similar: int = 10
    ) -> List[Tuple[int, float]]:
        """Find similar items"""
        
        if self.model is not None:
            similar = self.model.similar_items(item_id, N=n_similar)
            return similar
        else:
            # Compute similarity using item factors
            item_vector = self.item_factors[item_id:item_id+1]
            similarities = item_vector @ self.item_factors.T
            similarities = similarities.flatten()
            
            # Get top similar (excluding self)
            top_indices = np.argsort(similarities)[::-1][1:n_similar+1]
            
            return [(int(idx), float(similarities[idx])) for idx in top_indices]
    
    def similar_users(
        self,
        user_id: int,
        n_similar: int = 10
    ) -> List[Tuple[int, float]]:
        """Find similar users"""
        
        # Compute user-user similarity
        user_vector = self.user_factors[user_id:user_id+1]
        similarities = user_vector @ self.user_factors.T
        similarities = similarities.flatten()
        
        # Get top similar (excluding self)
        top_indices = np.argsort(similarities)[::-1][1:n_similar+1]
        
        return [(int(idx), float(similarities[idx])) for idx in top_indices]
    
    def add_user(self, user_interactions: np.ndarray) -> np.ndarray:
        """Add a new user and compute their factors"""
        
        # Initialize random factors
        user_factors = np.random.normal(0, 0.01, self.factors)
        
        # Refine using ALS (single iteration)
        items = np.where(user_interactions > 0)[0]
        
        if len(items) > 0:
            alpha = 40
            C = 1 + alpha * user_interactions[items]
            
            A = self.item_factors[items].T @ np.diag(C) @ self.item_factors[items]
            A += self.regularization * np.eye(self.factors)
            
            b = self.item_factors[items].T @ (C * user_interactions[items])
            
            user_factors = np.linalg.solve(A, b)
        
        return user_factors


# Example usage
if __name__ == "__main__":
    from scipy.sparse import csr_matrix
    
    # Create sample implicit feedback data
    # Rows = users (counties), Columns = items (interventions)
    interaction_data = np.array([
        [5, 3, 0, 2, 0],  # county_1
        [4, 0, 4, 0, 3],  # county_2
        [0, 2, 5, 3, 0],  # county_3
        [3, 4, 0, 4, 2],  # county_4
        [0, 0, 3, 2, 5],  # county_5
    ])
    
    interaction_matrix = csr_matrix(interaction_data)
    
    # Initialize and train model
    model = ImplicitCollaborativeFiltering(
        factors=10,
        regularization=0.01,
        iterations=20,
        use_gpu=False
    )
    
    model.fit(interaction_matrix)
    
    # Generate recommendations for user 0
    recommendations = model.recommend(
        user_id=0,
        interaction_matrix=interaction_matrix,
        n_recommendations=3
    )
    
    print("Recommendations for user 0:")
    for item_id, score in recommendations:
        print(f"  Item {item_id}: {score:.3f}")
    
    # Find similar items
    similar = model.similar_items(item_id=0, n_similar=3)
    print("\nItems similar to item 0:")
    for item_id, score in similar:
        print(f"  Item {item_id}: {score:.3f}")
    
    # Find similar users
    similar_users = model.similar_users(user_id=0, n_similar=3)
    print("\nUsers similar to user 0:")
    for user_id, score in similar_users:
        print(f"  User {user_id}: {score:.3f}")
