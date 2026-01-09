from typing import Dict, Optional
import json

class CostCalculator:
    """
    Calculate treatment costs based on disease type, farm size, and location
    """
    
    def __init__(self):
        # Cost database with prices per acre for different treatments
        self.cost_database = {
            "tomato___early_blight": {
                "treatment": "Copper-based fungicides",
                "cost_per_acre": 1500,  # INR
                "application_frequency": "Every 7-10 days",
                "duration": "4-5 applications"
            },
            "tomato___late_blight": {
                "treatment": "Metalaxyl + Mancozeb",
                "cost_per_acre": 2000,  # INR
                "application_frequency": "Every 5 days",
                "duration": "Emergency protocol"
            },
            "potato___late_blight": {
                "treatment": "Metalaxyl + Mancozeb",
                "cost_per_acre": 1800,  # INR
                "application_frequency": "Every 5 days",
                "duration": "Emergency protocol"
            },
            "pepper___bacterial_spot": {
                "treatment": "Streptocycline + Copper Oxychloride",
                "cost_per_acre": 1700,  # INR
                "application_frequency": "Every 7 days",
                "duration": "Max 4 sprays"
            },
            "corn___common_rust": {
                "treatment": "Triazole fungicides",
                "cost_per_acre": 1200,  # INR
                "application_frequency": "2-3 applications",
                "duration": "Seasonal"
            },
            "healthy": {
                "treatment": "No treatment needed",
                "cost_per_acre": 0,  # INR
                "application_frequency": "None",
                "duration": "None"
            }
        }
        
        # Regional price variations (multiplier)
        self.regional_multipliers = {
            "maharashtra": 1.0,
            "karnataka": 1.05,
            "tamil_nadu": 0.95,
            "punjab": 1.1,
            "uttar_pradesh": 0.9,
            "andhra_pradesh": 1.02,
            "telangana": 1.0,
            "gujarat": 0.98
        }
    
    def calculate_treatment_cost(self, disease_type: str, farm_size_acres: float, 
                               location_region: str = "maharashtra", 
                               currency: str = "INR") -> Dict:
        """
        Calculate treatment cost based on disease, farm size, and location
        """
        # Normalize disease type
        disease_key = disease_type.lower().replace(" ", "_").replace("-", "_")
        
        # Get base cost info
        cost_info = self.cost_database.get(disease_key, self.cost_database.get("healthy", {}))
        
        # Get regional multiplier
        region_multiplier = self.regional_multipliers.get(location_region.lower().replace(" ", "_"), 1.0)
        
        # Calculate costs
        base_cost_per_acre = cost_info.get("cost_per_acre", 0)
        total_base_cost = base_cost_per_acre * farm_size_acres
        total_cost = total_base_cost * region_multiplier
        
        # Prepare result
        result = {
            "disease_type": disease_type,
            "farm_size_acres": farm_size_acres,
            "location_region": location_region,
            "currency": currency,
            "treatment": cost_info.get("treatment", "Unknown"),
            "cost_per_acre_base": round(base_cost_per_acre, 2),
            "cost_per_acre_adjusted": round(base_cost_per_acre * region_multiplier, 2),
            "total_cost_base": round(total_base_cost, 2),
            "total_cost_adjusted": round(total_cost, 2),
            "application_frequency": cost_info.get("application_frequency", "N/A"),
            "treatment_duration": cost_info.get("duration", "N/A"),
            "regional_multiplier": region_multiplier
        }
        
        return result
    
    def get_cost_comparison(self, diseases: list, farm_size_acres: float, 
                          location_region: str = "maharashtra") -> Dict:
        """
        Compare costs for multiple diseases
        """
        comparisons = {}
        for disease in diseases:
            comparisons[disease] = self.calculate_treatment_cost(
                disease, farm_size_acres, location_region
            )
        
        return {
            "farm_size_acres": farm_size_acres,
            "location_region": location_region,
            "comparisons": comparisons,
            "cheapest_treatment": min(comparisons.keys(), 
                                    key=lambda x: comparisons[x]["total_cost_adjusted"]),
            "most_expensive_treatment": max(comparisons.keys(), 
                                          key=lambda x: comparisons[x]["total_cost_adjusted"])
        }
    
    def get_seasonal_cost_adjustments(self, season: str) -> float:
        """
        Get seasonal cost adjustments (e.g., higher costs during peak seasons)
        """
        seasonal_multipliers = {
            "kharif": 1.1,    # Monsoon season (June-October)
            "rabi": 1.0,      # Winter season (October-March)
            "zaid": 1.05      # Summer season (March-June)
        }
        
        return seasonal_multipliers.get(season.lower(), 1.0)
    
    def add_disease_cost(self, disease_name: str, cost_info: Dict):
        """
        Add or update cost information for a disease
        """
        self.cost_database[disease_name.lower()] = cost_info
    
    def get_cost_breakdown(self, disease_type: str, farm_size_acres: float) -> Dict:
        """
        Provide detailed cost breakdown for a treatment
        """
        cost_info = self.calculate_treatment_cost(disease_type, farm_size_acres)
        
        # Calculate cost components
        base_product_cost = cost_info["total_cost_adjusted"] * 0.6  # 60% for products
        labor_cost = cost_info["total_cost_adjusted"] * 0.25       # 25% for labor
        transportation_cost = cost_info["total_cost_adjusted"] * 0.15  # 15% for transport
        
        return {
            "total_cost": cost_info["total_cost_adjusted"],
            "cost_components": {
                "products": round(base_product_cost, 2),
                "labor": round(labor_cost, 2),
                "transportation": round(transportation_cost, 2)
            },
            "cost_per_sqft": round(cost_info["total_cost_adjusted"] / (farm_size_acres * 43560), 4),  # sq ft in an acre
            "treatment": cost_info["treatment"],
            "application_details": {
                "frequency": cost_info["application_frequency"],
                "duration": cost_info["treatment_duration"]
            }
        }

# Example usage
if __name__ == "__main__":
    calculator = CostCalculator()
    
    # Example cost calculation
    result = calculator.calculate_treatment_cost(
        "tomato___early_blight", 
        farm_size_acres=2.5, 
        location_region="maharashtra"
    )
    
    print("Treatment cost calculation:", result)
    
    # Example cost comparison
    comparison = calculator.get_cost_comparison(
        ["tomato___early_blight", "tomato___late_blight", "healthy"],
        farm_size_acres=2.0
    )
    
    print("\nCost comparison:", comparison)
    
    # Example cost breakdown
    breakdown = calculator.get_cost_breakdown("tomato___early_blight", 2.0)
    print("\nCost breakdown:", breakdown)