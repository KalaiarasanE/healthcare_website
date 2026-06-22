"""
Deployment Guide for Diabetes Predictor Application

This guide provides step-by-step instructions for deploying the application
on various platforms.
"""

# HEROKU DEPLOYMENT

## Prerequisites
- Heroku account (free at https://www.heroku.com)
- Heroku CLI installed

## Steps

1. Login to Heroku:
   ```bash
   heroku login
   ```

2. Create a new Heroku app:
   ```bash
   heroku create your-app-name
   ```

3. Deploy the application:
   ```bash
   git push heroku main
   ```

4. View the application:
   ```bash
   heroku open
   ```

5. View logs:
   ```bash
   heroku logs --tail
   ```

---

# DOCKER DEPLOYMENT

## Build Docker Image

1. Build the image:
   ```bash
   docker build -t diabetes-predictor .
   ```

2. Run the container:
   ```bash
   docker run -p 5000:5000 diabetes-predictor
   ```

## Docker Compose

Use docker-compose for easier management:
```bash
docker-compose up
```

---

# AWS DEPLOYMENT

## Using AWS Elastic Beanstalk

1. Install EB CLI:
   ```bash
   pip install awsebcli
   ```

2. Initialize EB:
   ```bash
   eb init -p python-3.9 diabetes-predictor
   ```

3. Create environment:
   ```bash
   eb create diabetes-env
   ```

4. Deploy:
   ```bash
   eb deploy
   ```

5. Open in browser:
   ```bash
   eb open
   ```

---

# PYTHON ANYWHERE DEPLOYMENT

1. Create account on PythonAnywhere
2. Upload project files
3. Configure virtual environment
4. Set up WSGI configuration
5. Enable the web app

---

# GOOGLE CLOUD DEPLOYMENT

1. Install Google Cloud SDK
2. Create project:
   ```bash
   gcloud projects create diabetes-predictor-app
   ```

3. Deploy with Cloud Run:
   ```bash
   gcloud run deploy diabetes-predictor --source .
   ```

---

# PRODUCTION CHECKLIST

- [ ] Set strong SECRET_KEY
- [ ] Enable HTTPS/SSL
- [ ] Configure CORS properly
- [ ] Set up proper logging
- [ ] Configure database if needed
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Update privacy policy
- [ ] Add terms of service
- [ ] Test thoroughly
- [ ] Set up CI/CD pipeline
- [ ] Configure error tracking
- [ ] Set up health monitoring

---

# ENVIRONMENT VARIABLES

Copy .env.example to .env and update:
```bash
cp .env.example .env
```

Required variables:
- FLASK_ENV=production
- SECRET_KEY=<generate-secure-key>
- DEBUG=False

---

# PERFORMANCE OPTIMIZATION

1. Use Gunicorn with multiple workers:
   ```bash
   gunicorn --workers 4 --threads 2 app:app
   ```

2. Enable caching:
   - Set appropriate cache headers
   - Use browser caching

3. Optimize database:
   - Use connection pooling
   - Create appropriate indexes

4. Monitor performance:
   - Set up APM tools
   - Monitor response times
   - Track error rates

---

# SECURITY CONSIDERATIONS

1. Always use HTTPS in production
2. Set secure cookie flags
3. Implement CSRF protection
4. Validate all user inputs
5. Use environment variables for secrets
6. Keep dependencies updated
7. Set up proper logging and monitoring
8. Use strong SECRET_KEY
9. Configure CORS properly
10. Implement rate limiting if needed

---

# TROUBLESHOOTING

## Port already in use
```bash
# Find process using port 5000
lsof -i :5000

# Kill the process
kill -9 <PID>
```

## Module not found
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

## Model file not found
Ensure diabetes-prediction-rfc-model.pkl is in the correct directory

## Permission denied
```bash
chmod +x app.py
```

---

# MONITORING AND LOGGING

1. Set up application logging
2. Configure external logging service
3. Set up uptime monitoring
4. Configure error tracking
5. Monitor resource usage
6. Track performance metrics

---

For more information, refer to the main README.md file.
