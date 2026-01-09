from PIL import Image, ImageStat
import numpy as np
from typing import Dict, Tuple
import cv2

class ImageQualityAssessment:
    """
    Assess image quality for agricultural disease detection
    """
    
    def __init__(self):
        pass
    
    def assess_image_quality(self, image_path_or_bytes) -> Dict:
        """
        Assess image quality based on multiple factors
        """
        # Load image
        if isinstance(image_path_or_bytes, str):
            image = Image.open(image_path_or_bytes)
        else:
            # Assume it's bytes
            image = Image.open(image_path_or_bytes)
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert to numpy array for advanced analysis
        img_array = np.array(image)
        
        # Calculate various quality metrics
        brightness = self._calculate_brightness(image)
        contrast = self._calculate_contrast(image)
        sharpness = self._calculate_sharpness(img_array)
        noise_level = self._calculate_noise(img_array)
        color_balance = self._calculate_color_balance(img_array)
        resolution = self._calculate_resolution(image)
        
        # Overall quality score
        quality_score = self._calculate_overall_quality(
            brightness, contrast, sharpness, noise_level, color_balance, resolution
        )
        
        # Quality description
        quality_description = self._get_quality_description(quality_score)
        
        return {
            "brightness": brightness,
            "contrast": contrast,
            "sharpness": sharpness,
            "noise_level": noise_level,
            "color_balance": color_balance,
            "resolution": resolution,
            "quality_score": quality_score,
            "quality_description": quality_description,
            "recommendations": self._get_recommendations(
                brightness, contrast, sharpness, noise_level, color_balance
            )
        }
    
    def _calculate_brightness(self, image) -> float:
        """
        Calculate brightness of the image (0-255)
        """
        gray_image = image.convert('L')
        stat = ImageStat.Stat(gray_image)
        return stat.mean[0]
    
    def _calculate_contrast(self, image) -> float:
        """
        Calculate contrast of the image (standard deviation of pixel values)
        """
        gray_image = image.convert('L')
        pixels = np.array(gray_image)
        return float(np.std(pixels))
    
    def _calculate_sharpness(self, img_array) -> float:
        """
        Calculate sharpness using Laplacian variance
        Higher values indicate sharper images
        """
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        return float(laplacian_var)
    
    def _calculate_noise(self, img_array) -> float:
        """
        Estimate noise level in the image
        Lower values indicate less noise
        """
        # Calculate noise using wavelet-based method (simplified)
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        # Simple noise estimation using standard deviation of Laplacian
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        noise = 1 / (1 + laplacian.std())  # Inverse relationship
        return float(noise)
    
    def _calculate_color_balance(self, img_array) -> float:
        """
        Calculate color balance (0-100), where 100 is perfectly balanced
        """
        # Calculate mean and std for each channel
        r_mean, g_mean, b_mean = np.mean(img_array, axis=(0,1))
        r_std, g_std, b_std = np.std(img_array, axis=(0,1))
        
        # Calculate color balance as inverse of the difference between channels
        color_diff = abs(r_mean - g_mean) + abs(g_mean - b_mean) + abs(r_mean - b_mean)
        # Normalize to 0-100 scale (lower difference = better balance)
        balance = max(0, 100 - color_diff)
        return min(balance, 100)  # Cap at 100
    
    def _calculate_resolution(self, image) -> Tuple[int, int]:
        """
        Get image resolution (width, height)
        """
        return image.size
    
    def _calculate_overall_quality(self, brightness, contrast, sharpness, noise_level, 
                                 color_balance, resolution) -> float:
        """
        Calculate overall quality score (0-100)
        """
        # Normalize individual scores to 0-100 scale
        brightness_norm = min(100, max(0, (brightness - 50) * 100 / 155))  # Adjusted for good brightness range
        contrast_norm = min(100, contrast * 100 / 100)  # Assuming max contrast of 100 is good
        sharpness_norm = min(100, sharpness * 100 / 1000)  # Adjusted based on typical sharpness values
        noise_norm = max(0, 100 - noise_level * 100)  # Inverse relationship
        color_balance_norm = color_balance
        resolution_norm = min(100, (resolution[0] * resolution[1]) / 1000000 * 100)  # Based on 1MP
        
        # Weighted average (adjust weights based on importance)
        weights = {
            'brightness': 0.15,
            'contrast': 0.15,
            'sharpness': 0.25,
            'noise': 0.15,
            'color_balance': 0.15,
            'resolution': 0.15
        }
        
        quality_score = (
            brightness_norm * weights['brightness'] +
            contrast_norm * weights['contrast'] +
            sharpness_norm * weights['sharpness'] +
            noise_norm * weights['noise'] +
            color_balance_norm * weights['color_balance'] +
            resolution_norm * weights['resolution']
        )
        
        return round(quality_score, 2)
    
    def _get_quality_description(self, quality_score: float) -> str:
        """
        Get quality description based on score
        """
        if quality_score >= 80:
            return "Excellent"
        elif quality_score >= 60:
            return "Good"
        elif quality_score >= 40:
            return "Fair"
        elif quality_score >= 20:
            return "Poor"
        else:
            return "Very Poor"
    
    def _get_recommendations(self, brightness, contrast, sharpness, noise_level, color_balance) -> list:
        """
        Get recommendations based on quality metrics
        """
        recommendations = []
        
        # Brightness recommendations
        if brightness < 50:
            recommendations.append("Image is too dark. Increase lighting or use flash.")
        elif brightness > 200:
            recommendations.append("Image is too bright. Reduce lighting or avoid direct sunlight.")
        
        # Contrast recommendations
        if contrast < 20:
            recommendations.append("Low contrast detected. Image may appear flat.")
        
        # Sharpness recommendations
        if sharpness < 100:  # Threshold may need adjustment
            recommendations.append("Image appears blurry. Hold camera steady or use tripod.")
        
        # Noise recommendations
        if noise_level > 0.8:  # Threshold may need adjustment
            recommendations.append("High noise detected. Use better lighting to avoid high ISO settings.")
        
        # Color balance recommendations
        if color_balance < 60:
            recommendations.append("Color balance could be improved. Avoid mixed lighting conditions.")
        
        if not recommendations:
            recommendations.append("Image quality is good for disease detection.")
        
        return recommendations
    
    def is_suitable_for_analysis(self, quality_score: float) -> bool:
        """
        Determine if image quality is suitable for disease analysis
        """
        return quality_score >= 50  # Threshold for acceptable quality

# Example usage
if __name__ == "__main__":
    # Note: This example would require an actual image file
    # For now, we'll just show the class structure
    print("ImageQualityAssessment class ready for use.")
    print("To use: image_qa = ImageQualityAssessment()")
    print("       result = image_qa.assess_image_quality('path_to_image.jpg')")
    print("       print(result)")