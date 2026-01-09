# KropScan - AI-Powered Crop Disease Detection

KropScan is an advanced AI-powered platform that enables farmers to instantly diagnose plant diseases using just their smartphone camera, with comprehensive treatment recommendations and agricultural support features.

## 🌟 Features

- **AI Disease Detection**: 98% accuracy in identifying crop diseases
- **Multi-Language Support**: English, Hindi, Marathi (expandable)
- **Camera Capture**: Direct photo capture functionality
- **Treatment Recommendations**: Detailed, localized treatment plans
- **Cost Calculator**: Estimate treatment costs based on farm size
- **Weather Integration**: Disease risk prediction based on weather
- **Crop Calendar**: Seasonal farming recommendations
- **Image Quality Assessment**: Ensures accurate diagnosis
- **Admin Dashboard**: Expert review and model management
- **Model Retraining**: Automatic improvement with feedback
- **Offline Mode**: Functionality without internet (coming soon)

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd kropscan
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the setup script:
```bash
python setup.py
```

### Running the Application

1. Start the backend server:
```bash
python backend.py
```

2. In a new terminal, start the frontend:
```bash
streamlit run frontend.py
```

3. Access the application at `http://localhost:8501`

## 🔐 Admin Access

- Default admin password: `admin123`
- Access admin features through the sidebar
- Admin dashboard available in "Expert Admin" section

## 🏗️ Project Structure

```
kropscan/
├── frontend.py          # Streamlit frontend
├── backend.py           # FastAPI backend
├── ai_engine.py         # AI model and prediction logic
├── setup.py             # Setup and dependency installation
├── run_app.py           # Application runner
├── requirements.txt     # Python dependencies
├── user_management.py   # User registration and profiles
├── notification_system.py # Notification system
├── weather_service.py   # Weather integration
├── language_service.py  # Multi-language support
├── cost_calculator.py   # Treatment cost estimation
├── retrain_model.py     # Model retraining pipeline
├── model_info.json      # Model configuration
├── kropscan_production_model.pth  # AI model weights
├── database/            # User data and feedback storage
└── README.md           # This file
```

## 🛠️ Development

### Adding New Features
1. Create new modules in the appropriate directory
2. Import and integrate into frontend.py
3. Update requirements.txt if needed
4. Test thoroughly
5. Update documentation

### Model Training
- Training scripts in `train_advanced.py` and `train_enhanced.py`
- Use `merge_datasets.py` to combine training data
- Validate model performance before deployment

### API Endpoints
- `/analyze` - Disease analysis endpoint
- `/chat` - Chatbot endpoint
- More endpoints in `backend.py`

## 📊 Data Flow

1. User uploads image via frontend
2. Frontend sends image to backend
3. Backend processes image with AI model
4. Results returned to frontend
5. User sees diagnosis and recommendations
6. Feedback stored for model improvement

## 🚨 Troubleshooting

### Common Issues
- **Model not loading**: Check `kropscan_production_model.pth` exists
- **Backend not connecting**: Verify backend is running on port 8000
- **Dependencies missing**: Run `pip install -r requirements.txt`
- **Admin access denied**: Check password is correct

### Performance Issues
- Ensure sufficient RAM for model loading
- Check internet connection for weather services
- Verify GPU availability if using CUDA

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

- **Issues**: Use GitHub Issues
- **Email**: support@kropscan.com
- **Documentation**: See FEATURES_GUIDE.md

---

*"Empowering farmers with AI, one crop at a time."*