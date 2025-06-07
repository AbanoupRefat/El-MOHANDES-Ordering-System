# EL-MOHANDES WhatsApp Ordering System

This is a Streamlit application designed for EL-MOHANDES Auto Parts company to facilitate WhatsApp-based ordering. Customers can browse products, add items to their cart, and generate a WhatsApp message with their order details.

## Features

- Product listing with search and pagination.
- Quantity selection for each product.
- Order summary with total items and cost.
- Generate pre-filled WhatsApp message for easy ordering.
- Integration with Google Sheets for product data (requires setup).

## Setup and Deployment

To run this application locally or deploy it to Streamlit Cloud, follow these steps:

### 1. Clone the Repository (if not already cloned)

```bash
git clone <your-repository-url>
cd "EL-MOHANDES Whatsapp Ordering System"
```

### 2. Install Dependencies

Install the required Python packages using `pip`:

```bash
pip install -r requirements.txt
```

### 3. Google Sheets Integration (for real data)

This application is configured to fetch product data from a Google Sheet. To enable this, you need to set up a Google Cloud Platform (GCP) service account and share your sheet with it.

#### a. Create a GCP Service Account

1.  Go to the [Google Cloud Console](https://console.cloud.google.com/).
2.  Navigate to "IAM & Admin" > "Service Accounts".
3.  Create a new service account.
4.  Grant the service account `Google Sheets API Viewer` or `Google Sheets API Editor` role.
5.  Generate a new JSON key for this service account and download it. Keep this file secure!

#### b. Share Your Google Sheet

1.  Open your Google Sheet (e.g., `https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit#gid=0`).
2.  Click the "Share" button.
3.  Add the `client_email` from your downloaded service account JSON key (e.g., `your-service-account-email@your-project-id.iam.gserviceaccount.com`) as a user with at least "Viewer" access.

### 4. Configure Secrets

Sensitive information like your Google Sheet URL, WhatsApp number, and GCP service account credentials should be stored as secrets. 

#### For Local Development (Optional)

Create a `.streamlit/secrets.toml` file in your project's root directory (next to `app.py`). **Do NOT commit this file to your public GitHub repository!** (It's already added to `.gitignore`).

```toml
[google]
sheet_url = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit#gid=0"

[whatsapp]
number = "201234567890"

[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n" # Replace newlines with \n
client_email = "your-service-account-email@your-project-id.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account-email.iam.gserviceaccount.com"
universe_domain = "googleapis.com"
```

#### For Streamlit Cloud Deployment

When deploying to Streamlit Cloud, you'll set these secrets directly in the app's settings:

1.  Go to your app's dashboard on Streamlit Cloud.
2.  Click the "Settings" button (gear icon).
3.  Select "Secrets".
4.  Add each secret in the format `[section]key = value` as shown in the `secrets.toml` example above. Ensure the `private_key` value is on a single line with `\n` representing newlines.

### 5. Run the Application

To run the app locally:

```bash
streamlit run app.py
```

### 6. Deploy to Streamlit Cloud

1.  Ensure your code is pushed to a public GitHub repository.
2.  Go to [share.streamlit.io](https://share.streamlit.io/).
3.  Click "New app" and connect to your GitHub repository.
4.  Select the repository, branch, and `app.py` as the main file.
5.  Ensure your secrets are configured in the Streamlit Cloud dashboard as described in step 4b.
6.  Click "Deploy!".

## Contact

For questions or support, please contact [Your Name/Company Name] at [Your Contact Info]. 