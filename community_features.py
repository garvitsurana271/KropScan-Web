"""
Community Features for KropScan
Features for farmer community engagement
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class CommunityFeatures:
    """Manages community features like farmer reviews, tips sharing, etc."""
    
    def __init__(self, reviews_file="community_reviews.json", tips_file="community_tips.json"):
        self.reviews_file = reviews_file
        self.tips_file = tips_file
        self.reviews = self.load_reviews()
        self.tips = self.load_tips()
    
    def load_reviews(self) -> List[Dict]:
        """Load community reviews from file"""
        if os.path.exists(self.reviews_file):
            try:
                with open(self.reviews_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_reviews(self):
        """Save community reviews to file"""
        try:
            with open(self.reviews_file, 'w') as f:
                json.dump(self.reviews, f, indent=2)
        except Exception as e:
            print(f"Error saving reviews: {e}")
    
    def load_tips(self) -> List[Dict]:
        """Load community tips from file"""
        if os.path.exists(self.tips_file):
            try:
                with open(self.tips_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_tips(self):
        """Save community tips to file"""
        try:
            with open(self.tips_file, 'w') as f:
                json.dump(self.tips, f, indent=2)
        except Exception as e:
            print(f"Error saving tips: {e}")
    
    def add_review(self, user_name: str, crop_type: str, treatment: str, 
                   effectiveness: int, review_text: str) -> bool:
        """
        Add a community review
        effectiveness: 1-5 star rating
        """
        review = {
            "id": len(self.reviews) + 1,
            "user_name": user_name,
            "crop_type": crop_type,
            "treatment": treatment,
            "effectiveness": effectiveness,  # 1-5 rating
            "review_text": review_text,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "likes": 0
        }
        self.reviews.append(review)
        self.save_reviews()
        return True
    
    def add_tip(self, user_name: str, crop_type: str, tip_category: str, 
                tip_content: str, location: str = "") -> bool:
        """
        Add a community tip
        tip_category: 'pest_control', 'fertilizer', 'irrigation', 'disease_prevention', 'harvesting', etc.
        """
        tip = {
            "id": len(self.tips) + 1,
            "user_name": user_name,
            "crop_type": crop_type,
            "tip_category": tip_category,
            "tip_content": tip_content,
            "location": location,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "upvotes": 0
        }
        self.tips.append(tip)
        self.save_tips()
        return True
    
    def get_top_reviews(self, limit: int = 5) -> List[Dict]:
        """Get top community reviews"""
        # Sort by effectiveness and likes
        sorted_reviews = sorted(self.reviews, 
                              key=lambda x: (x['effectiveness'], x.get('likes', 0)), 
                              reverse=True)
        return sorted_reviews[:limit]
    
    def get_tips_by_category(self, category: str) -> List[Dict]:
        """Get tips by category"""
        return [tip for tip in self.tips if tip['tip_category'] == category]
    
    def get_tips_by_crop(self, crop_type: str) -> List[Dict]:
        """Get tips for a specific crop"""
        return [tip for tip in self.tips if tip['crop_type'].lower() == crop_type.lower()]
    
    def get_recent_reviews(self, limit: int = 5) -> List[Dict]:
        """Get most recent reviews"""
        sorted_reviews = sorted(self.reviews, 
                              key=lambda x: x['date'], 
                              reverse=True)
        return sorted_reviews[:limit]
    
    def get_top_tips(self, limit: int = 5) -> List[Dict]:
        """Get top community tips by upvotes"""
        sorted_tips = sorted(self.tips, 
                            key=lambda x: x.get('upvotes', 0), 
                            reverse=True)
        return sorted_tips[:limit]
    
    def like_review(self, review_id: int) -> bool:
        """Like a review"""
        for review in self.reviews:
            if review['id'] == review_id:
                review['likes'] = review.get('likes', 0) + 1
                self.save_reviews()
                return True
        return False
    
    def upvote_tip(self, tip_id: int) -> bool:
        """Upvote a tip"""
        for tip in self.tips:
            if tip['id'] == tip_id:
                tip['upvotes'] = tip.get('upvotes', 0) + 1
                self.save_tips()
                return True
        return False

# Example usage
if __name__ == "__main__":
    community = CommunityFeatures()
    
    # Add some example reviews
    community.add_review(
        user_name="Ramesh Kumar",
        crop_type="Tomato",
        treatment="Copper Fungicide",
        effectiveness=5,
        review_text="This treatment worked excellently for early blight. Applied twice and saw significant improvement within a week."
    )
    
    community.add_tip(
        user_name="Sunita Devi",
        crop_type="Rice",
        tip_category="irrigation",
        tip_content="For better yield, use alternate wetting and drying method. Save 15-30% water while maintaining productivity.",
        location="Bihar"
    )
    
    print("Community features initialized!")
    print(f"Total reviews: {len(community.reviews)}")
    print(f"Total tips: {len(community.tips)}")