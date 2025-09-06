# API for upload and processing images

A FastAPI backend to collect, process, and analyze epidemiological data. It exposes endpoints for disease statistics by gender and age, related diseases, daily time series, overall proportions, and basic aggregate metrics.

## Getting started
### Requirements
- Python 3.11+
- `pip`or `venv`
### Clone and Install
```
git clone https://github.com/blancafr/ova-api
cd ova-api
python -m venv .venv
source .venv/bin/activate              # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```
### Configuration
Create `.venv` file in the project root. You will need to add the following variables:

```
FIRST_SUPERUSER=admin-created-startup
FIRST_SUPERUSER_PASSWORD=admin-password
SECRET_KEY=secretkey
```

### Run locally the application

```
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
## API Endpoints
The application expose the following endpoints.
![API Endpoints](/ova-api/assets/API.png)
### Data Upload

This backend is designed to operate in **low-connectivity medical centers**, where doctors still rely on **printed tables** to record diagnoses.  

To simplify their workflow:
- Doctors use a **mobile app** (built with Expo Go) to take a photo of the paper sheet.  
- The app is specifically adapted for **unstable connections**:
  - If there is internet, the photo is uploaded immediately.  
  - If not, the photo is stored locally and automatically retried until the upload succeeds.  

📱 You can find the mobile app here: [ova-app](https://github.com/blancafr/ova-app)  


#### Expected Table Format

The system is optimized to process photos of a specific **paper table layout**:  

- Each row must contain:  
  - **Sex** (e.g., *Hombre*, *Mujer*)  
  - **Age range** (e.g., *0-5 años*, *6-17 años*, *>50 años*)  
  - **Disease name** (string, exact match required)  
- An **X mark** indicates the value selected.  

If the table design changes, you will need to update the [processing constants](https://github.com/blancafr/ova-api/blob/main/ova-api/app/processing/constants.py).  

![Table format](/ova-api/assets/table-format.jpg)




