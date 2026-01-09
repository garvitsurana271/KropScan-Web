import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import uuid

class TreatmentEffectivenessTracker:
    """
    Track treatment effectiveness over time
    """
    
    def __init__(self, tracking_file="treatment_effectiveness.json"):
        self.tracking_file = tracking_file
        self.effectiveness_data = self.load_tracking_data()
    
    def load_tracking_data(self) -> Dict:
        """
        Load existing tracking data from file
        """
        if os.path.exists(self.tracking_file):
            try:
                with open(self.tracking_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_tracking_data(self):
        """
        Save tracking data to file
        """
        try:
            with open(self.tracking_file, 'w') as f:
                json.dump(self.effectiveness_data, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving tracking data: {e}")
    
    def create_treatment_record(self, disease: str, treatment: str, confidence: float, 
                              farm_size: float = None, location: str = None) -> str:
        """
        Create a new treatment record
        Returns a unique case ID for tracking
        """
        case_id = str(uuid.uuid4())
        
        record = {
            "case_id": case_id,
            "disease": disease,
            "treatment": treatment,
            "confidence": confidence,
            "farm_size": farm_size,
            "location": location,
            "created_at": datetime.now().isoformat(),
            "followups": [],
            "effectiveness_score": None,
            "final_outcome": None
        }
        
        self.effectiveness_data[case_id] = record
        self.save_tracking_data()
        
        return case_id
    
    def add_followup(self, case_id: str, days_after_treatment: int, 
                     improvement_level: str, notes: str = "") -> bool:
        """
        Add a followup record for a treatment
        improvement_level: "much_better", "better", "same", "worse", "unknown"
        """
        if case_id not in self.effectiveness_data:
            return False
        
        followup = {
            "followup_id": str(uuid.uuid4()),
            "days_after_treatment": days_after_treatment,
            "improvement_level": improvement_level,
            "notes": notes,
            "timestamp": datetime.now().isoformat()
        }
        
        self.effectiveness_data[case_id]["followups"].append(followup)
        
        # Update effectiveness score based on followups
        self._calculate_effectiveness_score(case_id)
        
        self.save_tracking_data()
        return True
    
    def _calculate_effectiveness_score(self, case_id: str):
        """
        Calculate effectiveness score based on followups
        """
        record = self.effectiveness_data[case_id]
        followups = record["followups"]
        
        if not followups:
            record["effectiveness_score"] = None
            return
        
        # Sort followups by days after treatment
        followups.sort(key=lambda x: x["days_after_treatment"])
        
        # Calculate weighted effectiveness
        total_weight = 0
        weighted_score = 0
        
        for followup in followups:
            # Weight more recent followups more heavily
            weight = 1.0 + (followup["days_after_treatment"] / 30.0)  # More recent = higher weight
            improvement_score = self._improvement_to_score(followup["improvement_level"])
            
            total_weight += weight
            weighted_score += improvement_score * weight
        
        if total_weight > 0:
            effectiveness = weighted_score / total_weight
            record["effectiveness_score"] = round(effectiveness, 2)
            
            # Determine final outcome based on latest followup
            latest_followup = followups[-1]
            record["final_outcome"] = latest_followup["improvement_level"]
    
    def _improvement_to_score(self, improvement_level: str) -> float:
        """
        Convert improvement level to numerical score
        """
        score_map = {
            "much_better": 100,
            "better": 75,
            "same": 25,
            "worse": 0,
            "unknown": 50
        }
        return score_map.get(improvement_level, 50)
    
    def get_effectiveness_report(self, case_id: str) -> Dict:
        """
        Get effectiveness report for a specific case
        """
        if case_id not in self.effectiveness_data:
            return {}
        
        record = self.effectiveness_data[case_id]
        
        return {
            "case_id": record["case_id"],
            "disease": record["disease"],
            "treatment": record["treatment"],
            "confidence": record["confidence"],
            "created_at": record["created_at"],
            "followups": record["followups"],
            "effectiveness_score": record["effectiveness_score"],
            "final_outcome": record["final_outcome"],
            "treatment_duration_days": self._get_treatment_duration(record)
        }
    
    def _get_treatment_duration(self, record: Dict) -> int:
        """
        Get the duration of treatment tracking in days
        """
        if not record["followups"]:
            return 0
        
        followup_days = [f["days_after_treatment"] for f in record["followups"]]
        return max(followup_days) if followup_days else 0
    
    def get_disease_effectiveness_stats(self, disease: str) -> Dict:
        """
        Get effectiveness statistics for a specific disease
        """
        relevant_records = [
            record for record in self.effectiveness_data.values()
            if record["disease"] == disease and record["effectiveness_score"] is not None
        ]
        
        if not relevant_records:
            return {
                "disease": disease,
                "total_treatments": 0,
                "average_effectiveness": 0,
                "success_rate": 0
            }
        
        total_effectiveness = sum(r["effectiveness_score"] for r in relevant_records)
        avg_effectiveness = total_effectiveness / len(relevant_records)
        
        # Success is defined as effectiveness score > 60
        successful_treatments = sum(1 for r in relevant_records if r["effectiveness_score"] > 60)
        success_rate = (successful_treatments / len(relevant_records)) * 100
        
        return {
            "disease": disease,
            "total_treatments": len(relevant_records),
            "average_effectiveness": round(avg_effectiveness, 2),
            "success_rate": round(success_rate, 2),
            "treatments": [
                {
                    "case_id": r["case_id"],
                    "effectiveness_score": r["effectiveness_score"],
                    "confidence": r["confidence"]
                }
                for r in relevant_records
            ]
        }
    
    def get_treatment_comparison(self, treatment1: str, treatment2: str) -> Dict:
        """
        Compare effectiveness of two treatments
        """
        records1 = [r for r in self.effectiveness_data.values() 
                   if r["treatment"] == treatment1 and r["effectiveness_score"] is not None]
        records2 = [r for r in self.effectiveness_data.values() 
                   if r["treatment"] == treatment2 and r["effectiveness_score"] is not None]
        
        avg1 = sum(r["effectiveness_score"] for r in records1) / len(records1) if records1 else 0
        avg2 = sum(r["effectiveness_score"] for r in records2) / len(records2) if records2 else 0
        
        return {
            "treatment1": {
                "name": treatment1,
                "average_effectiveness": round(avg1, 2),
                "sample_size": len(records1)
            },
            "treatment2": {
                "name": treatment2,
                "average_effectiveness": round(avg2, 2),
                "sample_size": len(records2)
            },
            "comparison": "treatment1_better" if avg1 > avg2 else "treatment2_better" if avg2 > avg1 else "equal"
        }
    
    def get_recent_followups(self, days: int = 7) -> List[Dict]:
        """
        Get recent followups within specified number of days
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_followups = []
        
        for case_id, record in self.effectiveness_data.items():
            for followup in record["followups"]:
                followup_date = datetime.fromisoformat(followup["timestamp"].replace("Z", "+00:00"))
                if followup_date >= cutoff_date:
                    recent_followups.append({
                        "case_id": case_id,
                        "disease": record["disease"],
                        "treatment": record["treatment"],
                        "followup": followup
                    })
        
        return recent_followups

# Example usage
if __name__ == "__main__":
    tracker = TreatmentEffectivenessTracker()
    
    # Create a treatment record
    case_id = tracker.create_treatment_record(
        disease="Tomato Early Blight",
        treatment="Copper-based fungicides",
        confidence=0.85,
        farm_size=2.5,
        location="Maharashtra"
    )
    
    print(f"Created treatment record with ID: {case_id}")
    
    # Add followups
    tracker.add_followup(case_id, days_after_treatment=7, improvement_level="better", 
                        notes="Significant improvement in leaf health")
    tracker.add_followup(case_id, days_after_treatment=14, improvement_level="much_better", 
                        notes="Almost complete recovery")
    
    # Get effectiveness report
    report = tracker.get_effectiveness_report(case_id)
    print(f"Effectiveness report: {report}")
    
    # Get disease stats
    stats = tracker.get_disease_effectiveness_stats("Tomato Early Blight")
    print(f"Disease stats: {stats}")