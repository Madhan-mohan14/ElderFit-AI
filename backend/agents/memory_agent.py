import numpy as np
from typing import List, Dict, Any
from datetime import datetime
from backend.models.schemas import WellnessEpisode, Mood, AppetiteLevel, EnergyLevel

class MemoryAgent:
    """Hopfield-style associative memory for wellness episodes"""
    
    def __init__(self):
        self.episodes: List[Dict[str, Any]] = []
        self.max_episodes = 100
    
    def store_episode(self, episode: Dict[str, Any]):
        """Store a wellness episode"""
        episode_with_id = {
            **episode,
            "id": len(self.episodes),
            "timestamp": datetime.now().isoformat()
        }
        self.episodes.append(episode_with_id)
        
        # Keep only recent episodes
        if len(self.episodes) > self.max_episodes:
            self.episodes = self.episodes[-self.max_episodes:]
    
    def _episode_to_vector(self, episode: Dict[str, Any]) -> np.ndarray:
        """Convert episode to feature vector for similarity"""
        # Encode categorical features
        mood_map = {m.value: i for i, m in enumerate(Mood)}
        appetite_map = {a.value: i for i, a in enumerate(AppetiteLevel)}
        energy_map = {e.value: i for i, e in enumerate(EnergyLevel)}
        
        vector = np.array([
            mood_map.get(episode.get("mood", "neutral"), 1),
            appetite_map.get(episode.get("appetite", "normal"), 1),
            energy_map.get(episode.get("energy", "medium"), 1),
            episode.get("adherence", 50) / 100.0,  # Normalize to 0-1
            episode.get("plan_score", 0.5),
            len(episode.get("liked_foods", [])) / 10.0,  # Normalize
            len(episode.get("liked_videos", [])) / 5.0,  # Normalize
            float(episode.get("nutrients_met", {}).get("fiber", False)),
            float(episode.get("nutrients_met", {}).get("calcium", False)),
        ])
        return vector
    
    def retrieve_similar(self, current_context: Dict[str, Any], top_k: int = 3) -> List[Dict[str, Any]]:
        """Retrieve similar past episodes using Hopfield-style association"""
        if not self.episodes:
            return []
        
        try:
            current_vector = self._episode_to_vector(current_context)
            similarities = []
            
            for episode in self.episodes:
                try:
                    episode_vector = self._episode_to_vector(episode)
                    # Cosine similarity
                    dot_product = np.dot(current_vector, episode_vector)
                    norm_product = np.linalg.norm(current_vector) * np.linalg.norm(episode_vector)
                    similarity = dot_product / (norm_product + 1e-10)
                    
                    # Boost similarity if liked foods/videos match
                    if current_context.get("preferred_foods"):
                        liked_overlap = len(set(current_context["preferred_foods"]) & 
                                           set(episode.get("liked_foods", [])))
                        similarity += liked_overlap * 0.1
                    
                    similarities.append((similarity, episode))
                except Exception:
                    # Skip episodes that can't be processed
                    continue
            
            # Sort by similarity and return top-k
            if similarities:
                similarities.sort(key=lambda x: x[0], reverse=True)
                return [episode for _, episode in similarities[:top_k]]
            return []
        except Exception:
            # Return empty list if retrieval fails
            return []
    
    def get_preferences(self) -> Dict[str, Any]:
        """Extract user preferences from stored episodes"""
        if not self.episodes:
            return {"liked_foods": [], "liked_videos": [], "disliked_foods": []}
        
        liked_foods = []
        liked_videos = []
        disliked_foods = []
        
        for episode in self.episodes:
            liked_foods.extend(episode.get("liked_foods", []))
            liked_videos.extend(episode.get("liked_videos", []))
            disliked_foods.extend(episode.get("disliked_foods", []))
        
        # Get most common preferences
        from collections import Counter
        return {
            "liked_foods": [food for food, _ in Counter(liked_foods).most_common(5)],
            "liked_videos": [video for video, _ in Counter(liked_videos).most_common(3)],
            "disliked_foods": list(set(disliked_foods))
        }

