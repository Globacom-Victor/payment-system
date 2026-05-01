# Email Notifications Setup Guide

## 🚀 Quick Setup (5 Minutes)

### Step 1: Get Your Email Credentials

#### **Option A: Using Gmail (Recommended)**

1. Go to https://myaccount.google.com/apppasswords
2. Sign in to your Google account
3. Select "Mail" and "Windows Computer" (or your device)
4. Google will generate a 16-character password
5. Copy this password (you'll need it)

#### **Option B: Using Other Email Providers**

**Microsoft Outlook/Hotmail:**
- SMTP Server: `smtp.outlook.com`
- Port: `587`
- App Password: Get from account settings

**Yahoo Mail:**
- SMTP Server: `smtp.mail.yahoo.com`
- Port: `587`
- App Password: Generate from account security settings

**SendGrid (Recommended for Production):**
- SMTP Server: `smtp.sendgrid.net`
- Port: `587`
- Username: `apikey`
- Password: Your SendGrid API key

### Step 2: Configure Environment Variables

```bash
# Copy environment template
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Email Configuration (Gmail Example)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=your_16_char_app_password
SMTP_USE_TLS=True
SMTP_NAME=Crypto Payment System

# Notification Settings
NOTIFICATIONS_ENABLED=True
ADMIN_EMAIL=admin@example.com
NOTIFY_CUSTOMER=True      # Send emails to customers
NOTIFY_ADMIN=True          # Send emails to admin

# Database & API (existing config)
DATABASE_URL=postgresql://user:password@localhost:5432/crypto_payment
ETHERSCAN_API_KEY=your_key
```

### Step 3: Install Email Dependencies

```bash
pip install -r requirements-dashboard.txt
```

### Step 4: Test Email Configuration

```python
# test_email.py
from email_service import EmailService

email_service = EmailService()
test_data = {
    'transaction_id': 'test-123',
    'crypto_symbol': 'BTC',
    'crypto_amount': '0.025',
    'fiat_symbol': 'USD',
    'fiat_amount': '1000',
    'exchange_rate': '40000',
    'wallet_address': 'bc1q09nu70j26mgln6x9tha6eerlv80d6uzn588u0v',
    'created_at': '2026-05-01 12:00:00 UTC'
}

# Send test email
email_service.send_payment_created_email('your_email@example.com', test_data)
print("✅ Email sent!")
```

---

## 📧 Email Notifications Included

### 1. **Payment Created** 🎉
- Sent when customer initiates a payment
- Includes transaction ID, amount, wallet address
- Status: **PENDING**

### 2. **Payment Confirmed** ✅
- Sent when payment is confirmed on blockchain
- Includes confirmation time
- Status: **CONFIRMED**

### 3. **Payment Completed** 🎊
- Sent when payment is fully processed
- Includes completion summary
- Status: **COMPLETED**

### 4. **Payment Failed** ❌
- Sent if payment fails
- Includes failure reason
- Status: **FAILED**

---

## 🔧 Usage Examples

### Creating Payment with Email Notification

```bash
python cli_v2.py purchase \
  --crypto BTC \
  --fiat USD \
  --amount 100 \
  --wallet bc1q09nu70j26mgln6x9tha6eerlv80d6uzn588u0v \
  --email customer@example.com
```

### Programmatic Usage

```python
from payment_service_v2 import PaymentServiceV2
from database import get_session

session = get_session()
service = PaymentServiceV2(session)

# Create payment with email notification
transaction = service.create_purchase(
    crypto_symbol='BTC',
    fiat_symbol='USD',
    fiat_amount=100,
    wallet_address='bc1q09nu70j26mgln6x9tha6eerlv80d6uzn588u0v',
    customer_email='customer@example.com'  # Email will be sent!
)

# Update status with notification
service.update_transaction_status(
    transaction_id=transaction.id,
    status='confirmed',
    customer_email='customer@example.com'  # Email will be sent!
)
```

---

## 🎨 Email Templates

All emails are professionally designed with:
- ✅ HTML formatting
- ✅ Color-coded status badges
- ✅ Clear transaction details
- ✅ Company branding
- ✅ Responsive design

---

## 📊 Email Notification Flow

```
┌─────────────────────┐
│  Payment Created    │
│  (CLI/API)          │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Email Sent:        │
│  🎉 Payment Created │
│  (Customer + Admin) │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Status: PENDING    │
│  (Awaiting Confirm) │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Admin Updates      │
│  Status to          │
│  CONFIRMED          │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Email Sent:        │
│  ✅ Payment Confirm │
│  (Customer + Admin) │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Admin Updates      │
│  Status to          │
│  COMPLETED          │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Email Sent:        │
│  🎊 Payment Done    │
│  (Customer + Admin) │
└─────────────────────┘
```

---

## 🔐 Security Best Practices

✅ Never commit `.env` file to Git  
✅ Use app-specific passwords (not main password)  
✅ Enable 2FA on email account  
✅ Rotate API keys regularly  
✅ Use environment variables for all secrets  
✅ Consider using SendGrid for production  

---

## 🚨 Troubleshooting

### Email Not Sending?

1. **Check SMTP credentials:**
   ```python
   from email_service import EmailService
   service = EmailService()
   # If no error, credentials are correct
   ```

2. **Check logs:**
   ```bash
   # Enable debug logging
   LOG_LEVEL=DEBUG python cli_v2.py purchase ...
   ```

3. **Gmail-specific issues:**
   - Use app password (not Gmail password)
   - Enable "Less secure app access" if not using app password
   - Check if 2FA is enabled

4. **Test SMTP connection:**
   ```python
   import smtplib
   server = smtplib.SMTP('smtp.gmail.com', 587)
   server.starttls()
   server.login('your_email@gmail.com', 'your_app_password')
   print("✅ Connection successful!")
   ```

---

## 📈 Production Recommendations

1. **Use SendGrid or AWS SES** for reliability and scalability
2. **Add email templates database** for custom branding
3. **Implement retry logic** for failed sends
4. **Add email logging** to track sends
5. **Use scheduled tasks** (Celery) for async sending
6. **Monitor email delivery** rates

---

## 🎯 Customization

To customize email templates, edit the HTML in `email_service.py`:

```python
# Change template HTML
template = """
<!DOCTYPE html>
<html>
<!-- Your custom HTML here -->
</html>
"""
```

---

Your email notification system is ready! 🚀
