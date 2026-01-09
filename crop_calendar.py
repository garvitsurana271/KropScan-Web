from datetime import datetime, date
from typing import Dict, List, Optional
import json

class CropCalendar:
    """
    Crop calendar for seasonal farming recommendations
    """
    
    def __init__(self):
        self.crop_data = self._initialize_crop_data()
    
    def _initialize_crop_data(self) -> Dict:
        """
        Initialize crop calendar data
        """
        return {
            "tomato": {
                "kharif": {
                    "planting_months": ["june", "july"],
                    "harvesting_months": ["september", "october", "november"],
                    "care_tips": {
                        "june_july": "Prepare nursery beds, select disease-resistant seeds",
                        "august": "Transplant seedlings, start preventive fungicide spray",
                        "september": "Monitor for early blight, support plants with stakes",
                        "october": "Continue monitoring, harvest mature fruits",
                        "november": "Final harvest, prepare for next season"
                    },
                    "disease_risk": {
                        "july": ["early blight", "fusarium wilt"],
                        "august": ["early blight", "late blight"],
                        "september": ["late blight", "septoria leaf spot"],
                        "october": ["bacterial spot", "anthracnose"]
                    }
                },
                "rabi": {
                    "planting_months": ["october", "november"],
                    "harvesting_months": ["january", "february", "march"],
                    "care_tips": {
                        "october_november": "Prepare field, apply organic manure, select seeds",
                        "december": "Transplant, ensure proper spacing, irrigation",
                        "january": "Monitor for diseases in cool weather",
                        "february": "Flowering stage, support with proper nutrition",
                        "march": "Ripe harvest, disease monitoring"
                    },
                    "disease_risk": {
                        "january": ["early blight", "septoria leaf spot"],
                        "february": ["late blight", "fusarium wilt"],
                        "march": ["bacterial spot", "viral infections"]
                    }
                }
            },
            "potato": {
                "rabi": {
                    "planting_months": ["october", "november"],
                    "harvesting_months": ["january", "february", "march"],
                    "care_tips": {
                        "october": "Prepare field, treat seed tubers with fungicides",
                        "november": "Planting, ensure proper spacing",
                        "december": "Irrigation, weeding, monitor for pests",
                        "january": "Monitor for late blight, hilling",
                        "february": "Final growth stage, reduce irrigation",
                        "march": "Harvesting, proper storage preparation"
                    },
                    "disease_risk": {
                        "january": ["late blight", "early blight"],
                        "february": ["late blight", "blackleg"],
                        "march": ["soft rot", "silver scurf"]
                    }
                },
                "kharif": {
                    "planting_months": ["may", "june"],
                    "harvesting_months": ["august", "september"],
                    "care_tips": {
                        "may": "Early planting in cool weather, seed treatment",
                        "june": "Planting during pre-monsoon, bed preparation",
                        "july": "Monsoon care, drainage management",
                        "august": "Monitor blight diseases during monsoon",
                        "september": "Harvesting before heavy rains"
                    },
                    "disease_risk": {
                        "july": ["late blight", "early blight"],
                        "august": ["late blight", "black scurf"],
                        "september": ["soft rot", "early blight"]
                    }
                }
            },
            "corn": {
                "kharif": {
                    "planting_months": ["may", "june"],
                    "harvesting_months": ["september", "october"],
                    "care_tips": {
                        "may": "Soil preparation, seed treatment",
                        "june": "Planting during early monsoon",
                        "july": "Monsoon growth phase, nutrient management",
                        "august": "Tasseling stage, irrigation management",
                        "september": "Silking and grain filling, pest control",
                        "october": "Harvesting, drying and storage"
                    },
                    "disease_risk": {
                        "july": ["rust", "blight"],
                        "august": ["rust", "smut"],
                        "september": ["ear rot", "stalk rot"]
                    }
                }
            },
            "rice": {
                "kharif": {
                    "planting_months": ["june", "july"],
                    "harvesting_months": ["october", "november"],
                    "care_tips": {
                        "june": "Nursery preparation, seed sowing",
                        "july": "Transplanting during monsoon",
                        "august": "Monsoon care, water management",
                        "september": "Grain formation, nutrient supply",
                        "october": "Grain maturation, water reduction",
                        "november": "Harvesting, drying"
                    },
                    "disease_risk": {
                        "july": ["blast", "bacterial blight"],
                        "august": ["blast", "sheath blight"],
                        "september": ["brown spot", "rice tungro"],
                        "october": ["brown spot", "grain discoloration"]
                    }
                }
            }
        }
    
    def get_current_season(self, month: Optional[str] = None) -> str:
        """
        Determine the current agricultural season
        """
        if month is None:
            month = date.today().strftime("%B").lower()
        
        # In India, seasons are typically:
        # Kharif: June-October (monsoon season)
        # Rabi: October-March (winter season)
        # Zaid: March-June (summer season) - less common
        
        kharif_months = ["june", "july", "august", "september", "october"]
        rabi_months = ["october", "november", "december", "january", "february", "march"]
        
        if month in kharif_months:
            return "kharif"
        elif month in rabi_months:
            return "rabi"
        else:
            return "zaid"  # Default to zaid for April-May
    
    def get_suitable_crops(self, season: Optional[str] = None, 
                          month: Optional[str] = None) -> List[str]:
        """
        Get crops suitable for the current season
        """
        if season is None:
            season = self.get_current_season(month)
        
        suitable_crops = []
        for crop, data in self.crop_data.items():
            if season in data:
                suitable_crops.append(crop)
        
        return suitable_crops
    
    def get_planting_schedule(self, crop: str, season: Optional[str] = None) -> Dict:
        """
        Get planting schedule for a specific crop and season
        """
        crop = crop.lower()
        if season is None:
            season = self.get_current_season()
        
        if crop in self.crop_data and season in self.crop_data[crop]:
            crop_info = self.crop_data[crop][season]
            return {
                "crop": crop,
                "season": season,
                "planting_months": crop_info["planting_months"],
                "harvesting_months": crop_info["harvesting_months"],
                "care_tips": crop_info["care_tips"],
                "disease_risk": crop_info["disease_risk"]
            }
        else:
            return {
                "crop": crop,
                "season": season,
                "planting_months": [],
                "harvesting_months": [],
                "care_tips": {},
                "disease_risk": {},
                "message": f"Calendar information not available for {crop} in {season} season"
            }
    
    def get_monthly_care_tips(self, crop: str, month: str, season: Optional[str] = None) -> str:
        """
        Get specific care tips for a crop in a particular month
        """
        if season is None:
            season = self.get_current_season(month)
        
        schedule = self.get_planting_schedule(crop, season)
        
        # Format month for lookup (e.g., "june_july" for months in care tips)
        month_key = month.lower()
        
        # Check for combined month keys first (like "june_july")
        for key in schedule["care_tips"]:
            if month_key in key:
                return schedule["care_tips"][key]
        
        # If not found, return the general tip for the month
        return schedule["care_tips"].get(month_key, 
                                       f"No specific care tips available for {crop} in {month}")
    
    def get_disease_risk_for_month(self, crop: str, month: str, season: Optional[str] = None) -> List[str]:
        """
        Get disease risk for a crop in a specific month
        """
        if season is None:
            season = self.get_current_season(month)
        
        schedule = self.get_planting_schedule(crop, season)
        
        # Format month for lookup
        month_key = month.lower()
        
        # Check for combined month keys first
        for key in schedule["disease_risk"]:
            if month_key in key:
                return schedule["disease_risk"][key]
        
        # If not found, return the general risk for the month
        return schedule["disease_risk"].get(month_key, [])
    
    def get_seasonal_recommendations(self, location: str = "India") -> Dict:
        """
        Get seasonal recommendations based on location
        """
        current_month = date.today().strftime("%B").lower()
        current_season = self.get_current_season(current_month)
        
        suitable_crops = self.get_suitable_crops(current_season, current_month)
        
        recommendations = {
            "current_month": current_month.title(),
            "current_season": current_season,
            "location": location,
            "suitable_crops": suitable_crops,
            "crop_details": {}
        }
        
        for crop in suitable_crops:
            schedule = self.get_planting_schedule(crop, current_season)
            recommendations["crop_details"][crop] = {
                "planting_months": schedule["planting_months"],
                "harvesting_months": schedule["harvesting_months"]
            }
        
        return recommendations
    
    def add_crop_data(self, crop_name: str, crop_info: Dict):
        """
        Add new crop data to the calendar
        """
        self.crop_data[crop_name.lower()] = crop_info
    
    def get_preventive_measures(self, crop: str, month: str, season: Optional[str] = None) -> List[str]:
        """
        Get preventive measures based on disease risk
        """
        if season is None:
            season = self.get_current_season(month)
        
        disease_risks = self.get_disease_risk_for_month(crop, month, season)
        
        preventive_measures = []
        
        for disease in disease_risks:
            measures = self._get_preventive_measures_for_disease(disease)
            preventive_measures.extend(measures)
        
        # Remove duplicates while preserving order
        unique_measures = []
        for measure in preventive_measures:
            if measure not in unique_measures:
                unique_measures.append(measure)
        
        return unique_measures
    
    def _get_preventive_measures_for_disease(self, disease: str) -> List[str]:
        """
        Get preventive measures for specific disease
        """
        measures_map = {
            "late blight": [
                "Apply preventive fungicides before disease appears",
                "Ensure good air circulation around plants",
                "Avoid overhead watering",
                "Remove infected plant parts immediately"
            ],
            "early blight": [
                "Apply copper-based fungicides preventively",
                "Rotate crops annually",
                "Use disease-free seeds",
                "Maintain proper plant spacing"
            ],
            "bacterial blight": [
                "Use disease-free seeds",
                "Avoid working in wet fields",
                "Apply copper-based bactericides",
                "Ensure proper drainage"
            ],
            "blast": [
                "Use resistant varieties",
                "Apply silicate fertilizers",
                "Avoid excessive nitrogen",
                "Drain water before applying fungicides"
            ],
            "rust": [
                "Apply preventive fungicides",
                "Remove crop residue",
                "Plant resistant varieties",
                "Monitor fields regularly"
            ]
        }
        
        return measures_map.get(disease.lower(), [
            f"General preventive measures for {disease}:",
            "Use disease-resistant varieties",
            "Maintain field hygiene",
            "Monitor crops regularly",
            "Apply preventive treatments as needed"
        ])

# Example usage
if __name__ == "__main__":
    calendar = CropCalendar()
    
    # Get seasonal recommendations
    recommendations = calendar.get_seasonal_recommendations()
    print("Seasonal recommendations:", recommendations)
    
    # Get planting schedule for tomato
    tomato_schedule = calendar.get_planting_schedule("tomato")
    print("\nTomato schedule:", tomato_schedule)
    
    # Get care tips for tomato in July
    july_tips = calendar.get_monthly_care_tips("tomato", "july")
    print(f"\nTomato care tips for July: {july_tips}")
    
    # Get disease risk for tomato in August
    aug_risks = calendar.get_disease_risk_for_month("tomato", "august")
    print(f"\nTomato disease risks for August: {aug_risks}")
    
    # Get preventive measures for tomato in August
    aug_measures = calendar.get_preventive_measures("tomato", "august")
    print(f"\nPreventive measures for August: {aug_measures}")