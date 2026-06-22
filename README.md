# Diabetes Predictor - End-to-End Machine Learning Application

A sophisticated AI-powered web application for early diabetes detection using machine learning. This application combines medical science with cutting-edge technology to provide instant diabetes risk assessments.

## 🎯 Features

- **AI-Powered Prediction**: Advanced Random Forest Classifier with Stratified K-Fold cross-validation
- **User-Friendly Interface**: Modern, responsive web interface built with Bootstrap 5
- **Instant Results**: Get predictions with confidence scores in seconds
- **Personalized Recommendations**: Health tips based on your specific metrics
- **Secure & Private**: Data processed securely with no persistent storage
- **RESTful API**: JSON API endpoints for programmatic access
- **Comprehensive Navigation**: Home, About, and error pages
- **Robust Error Handling**: User-friendly error messages and logging
- **Mobile Responsive**: Works seamlessly on all devices

## 📋 Health Metrics Required

1. **Pregnancies**: Number of pregnancies (0-20)
2. **Glucose**: Glucose level in mg/dL (70-200)
3. **Blood Pressure**: Blood pressure in mmHg (40-180)
4. **Skin Thickness**: Skin thickness in mm (0-100)
5. **Insulin**: Insulin level in IU/mL (0-900)
6. **BMI**: Body Mass Index in kg/m² (10-60)
7. **DPF**: Diabetes Pedigree Function (0-2.5)
8. **Age**: Age in years (20-100) 
- A user has to put details like Number of Pregnancies, Insulin Level, Age, BMI etc . 
- Once it get all the fields information , the prediction is displayed on a new page . 
### Technologies Used  
![](https://forthebadge.com/images/badges/made-with-python.svg) 

[<img target="_blank" src="https://github.com/scikit-learn/scikit-learn/blob/master/doc/logos/scikit-learn-logo-small.png">](https://github.com/scikit-learn/)
<img target="_blank" src="https://flask.palletsprojects.com/en/1.1.x/_images/flask-logo.png" width=170>
<img target="_blank" src="https://github.com/ditikrushna/End-to-End-Diabetes-Prediction-Application-Using-Machine-Learning/blob/master/Resource/heroku.png" width=170>
<img target="_blank" src="https://github.com/ditikrushna/End-to-End-Diabetes-Prediction-Application-Using-Machine-Learning/blob/master/Resource/numpy.png" width=170>
<img target="_blank" src="https://github.com/ditikrushna/End-to-End-Diabetes-Prediction-Application-Using-Machine-Learning/blob/master/Resource/pandas.jpeg" width=170>

### Bug / Feature Request
If you find a bug (the website couldn't handle the query and / or gave undesired results), kindly open an issue [here](https://github.com/ditikrushna/End-to-End-Diabetes-Prediction-Application-Using-Machine-Learning/issues) by including your search query and the expected result.

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd diabetes-predictor
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   Open your browser and navigate to `http://localhost:5000`

## 📁 Project Structure

```
diabetes-predictor/
├── app.py                                 # Main Flask application
├── Diabetes Predictor - Deployment.py     # Model training script
├── requirements.txt                       # Python dependencies
├── Procfile                              # Deployment configuration
├── README.md                             # Project documentation
├── templates/
│   ├── index.html                        # Home page
│   ├── result.html                       # Results page
│   ├── about.html                        # About page
│   └── error.html                        # Error page
├── static/
│   ├── css/
│   │   └── style.css                     # Custom CSS styles
│   └── (images and other static assets)
└── Resource/                             # Additional resources
```

## 🔧 Application Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Home page with prediction form |
| `/predict` | POST | Submit prediction form |
| `/about` | GET | About page with project details |
| `/api/predict` | POST | JSON API for predictions |
| `/health` | GET | Health check endpoint |

## 🤖 Machine Learning Model

- **Algorithm**: Random Forest Classifier
- **Dataset**: Pima Indians Diabetes Database
- **Training Method**: Stratified K-Fold Cross-Validation (5 folds)
- **Input Features**: 8 health metrics
- **Output**: Binary classification (Diabetes/No Diabetes)

### Model Training

The model is trained using Stratified K-Fold cross-validation for robust evaluation:

```python
from sklearn.model_selection import StratifiedKFold
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)
```

## 💻 API Documentation

### Prediction Endpoint

**POST** `/api/predict`

Request body:
```json
{
    "pregnancies": 2,
    "glucose": 120,
    "bloodpressure": 80,
    "skinthickness": 25,
    "insulin": 100,
    "bmi": 25.5,
    "dpf": 0.52,
    "age": 35
}
```

Response:
```json
{
    "prediction": 1,
    "has_diabetes": true,
    "confidence": 75.45,
    "timestamp": "2024-02-09T12:34:56.789Z"
}
```

## 🎨 UI/UX Features

- **Responsive Design**: Works seamlessly on mobile, tablet, and desktop
- **Modern Styling**: Clean, professional interface with gradients and animations
- **Form Validation**: Client-side and server-side validation
- **User Feedback**: Clear error messages and success confirmations
- **Print Support**: Results can be printed for record keeping

## 🔒 Security Features

- **Input Validation**: Strict validation of all user inputs
- **Error Handling**: Comprehensive error handling with logging
- **Session Management**: Secure session handling
- **No Data Storage**: Personal health data is never persisted

## ⚠️ Important Disclaimer

**This tool is for educational and informational purposes only.** It is NOT a substitute for professional medical advice, diagnosis, or treatment. Always consult with a qualified healthcare provider for proper diagnosis and treatment.

## 📚 Technologies Used

- **Backend**: Flask 2.3.2
- **Machine Learning**: Scikit-learn 1.2.0
- **Data Processing**: NumPy, Pandas
- **Visualization**: Matplotlib
- **Frontend**: Bootstrap 5.3.0, Font Awesome 6.4.0
- **Server**: Gunicorn 20.1.0

## 📞 Support

For issues or questions, please feel free to reach out.

## 📈 Future Enhancements

- User authentication and history tracking
- Advanced visualization of health metrics
- Multi-language support
- Mobile app version
- Integration with health devices

## 📝 License

This project is provided for educational purposes.

---

**Last Updated**: February 2024
**Version**: 2.0 (Website Edition with Enhanced Features)

