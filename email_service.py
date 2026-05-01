import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging
from config import SMTP_CONFIG
from jinja2 import Template

logger = logging.getLogger(__name__)

class EmailService:
    """Service for sending transaction notification emails"""
    
    def __init__(self):
        """Initialize email service with SMTP configuration"""
        self.smtp_server = SMTP_CONFIG['server']
        self.smtp_port = SMTP_CONFIG['port']
        self.sender_email = SMTP_CONFIG['email']
        self.sender_password = SMTP_CONFIG['password']
        self.sender_name = SMTP_CONFIG.get('name', 'Crypto Payment System')
    
    def send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """Send email
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: Email body (HTML)
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = f"{self.sender_name} <{self.sender_email}>"
            message['To'] = to_email
            
            # Attach HTML content
            html_part = MIMEText(html_content, 'html')
            message.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if SMTP_CONFIG['use_tls']:
                    server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except smtplib.SMTPAuthenticationError:
            logger.error(f"SMTP authentication failed for {self.sender_email}")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error occurred: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False
    
    def send_payment_created_email(self, to_email: str, transaction_data: dict) -> bool:
        """Send payment created notification
        
        Args:
            to_email: Recipient email
            transaction_data: Transaction details dict
            
        Returns:
            bool: Success status
        """
        template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body { font-family: Arial, sans-serif; background-color: #f5f5f5; }
                .container { max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; }
                .header { background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); color: white; padding: 20px; border-radius: 8px 8px 0 0; text-align: center; }
                .content { padding: 20px; }
                .info-row { margin: 15px 0; border-bottom: 1px solid #e5e5e5; padding-bottom: 10px; }
                .label { font-weight: bold; color: #666; font-size: 12px; text-transform: uppercase; }
                .value { font-size: 16px; color: #333; margin-top: 5px; }
                .status-badge { display: inline-block; padding: 8px 16px; background-color: #fbbf24; color: #854d0e; border-radius: 20px; font-weight: bold; }
                .button { display: inline-block; margin-top: 20px; padding: 12px 30px; background-color: #3b82f6; color: white; text-decoration: none; border-radius: 6px; }
                .footer { text-align: center; color: #999; font-size: 12px; margin-top: 20px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Payment Created!</h1>
                </div>
                <div class="content">
                    <p>Hi there,</p>
                    <p>A new cryptocurrency payment has been created. Here are the details:</p>
                    
                    <div class="info-row">
                        <div class="label">Transaction ID</div>
                        <div class="value">{{ transaction_id }}</div>
                    </div>
                    
                    <div class="info-row">
                        <div class="label">Type</div>
                        <div class="value">{{ crypto_amount }} {{ crypto_symbol }} ← {{ fiat_amount }} {{ fiat_symbol }}</div>
                    </div>
                    
                    <div class="info-row">
                        <div class="label">Exchange Rate</div>
                        <div class="value">1 {{ crypto_symbol }} = {{ exchange_rate }} {{ fiat_symbol }}</div>
                    </div>
                    
                    <div class="info-row">
                        <div class="label">Wallet Address</div>
                        <div class="value" style="word-break: break-all; font-family: monospace;">{{ wallet_address }}</div>
                    </div>
                    
                    <div class="info-row">
                        <div class="label">Status</div>
                        <div class="value">
                            <span class="status-badge">⏳ PENDING</span>
                        </div>
                    </div>
                    
                    <div class="info-row">
                        <div class="label">Created At</div>
                        <div class="value">{{ created_at }}</div>
                    </div>
                    
                    <p style="margin-top: 30px; color: #666;">
                        Please keep this transaction ID safe for future reference.
                    </p>
                </div>
                <div class="footer">
                    <p>© 2026 Crypto Payment System. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        subject = f"🎉 Payment Created - {transaction_data['transaction_id'][:8]}..."
        html_content = Template(template).render(**transaction_data)
        
        return self.send_email(to_email, subject, html_content)
    
    def send_payment_confirmed_email(self, to_email: str, transaction_data: dict) -> bool:
        """Send payment confirmed notification
        
        Args:
            to_email: Recipient email
            transaction_data: Transaction details dict
            
        Returns:
            bool: Success status
        """
        template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body { font-family: Arial, sans-serif; background-color: #f5f5f5; }
                .container { max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; }
                .header { background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 20px; border-radius: 8px 8px 0 0; text-align: center; }
                .content { padding: 20px; }
                .info-row { margin: 15px 0; border-bottom: 1px solid #e5e5e5; padding-bottom: 10px; }
                .label { font-weight: bold; color: #666; font-size: 12px; text-transform: uppercase; }
                .value { font-size: 16px; color: #333; margin-top: 5px; }
                .status-badge { display: inline-block; padding: 8px 16px; background-color: #dcfce7; color: #15803d; border-radius: 20px; font-weight: bold; }
                .button { display: inline-block; margin-top: 20px; padding: 12px 30px; background-color: #10b981; color: white; text-decoration: none; border-radius: 6px; }
                .footer { text-align: center; color: #999; font-size: 12px; margin-top: 20px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✅ Payment Confirmed!</h1>
                </div>
                <div class="content">
                    <p>Great news!</p>
                    <p>Your cryptocurrency payment has been confirmed on the blockchain.</p>
                    
                    <div class="info-row">
                        <div class="label">Transaction ID</div>
                        <div class="value">{{ transaction_id }}</div>
                    </div>
                    
                    <div class="info-row">
                        <div class="label">Payment</div>
                        <div class="value">{{ crypto_amount }} {{ crypto_symbol }}</div>
                    </div>
                    
                    <div class="info-row">
                        <div class="label">Received At</div>
                        <div class="value">{{ wallet_address }}</div>
                    </div>
                    
                    <div class="info-row">
                        <div class="label">Status</div>
                        <div class="value">
                            <span class="status-badge">✅ CONFIRMED</span>
                        </div>
                    </div>
                    
                    <div class="info-row">
                        <div class="label">Confirmed At</div>
                        <div class="value">{{ confirmed_at }}</div>
                    </div>
                    
                    <p style="margin-top: 30px; color: #666;">
                        Thank you for using our payment service!
                    </p>
                </div>
                <div class="footer">
                    <p>© 2026 Crypto Payment System. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        subject = f"✅ Payment Confirmed - {transaction_data['transaction_id'][:8]}..."
        html_content = Template(template).render(**transaction_data)
        
        return self.send_email(to_email, subject, html_content)
    
    def send_payment_failed_email(self, to_email: str, transaction_data: dict) -> bool:
        """Send payment failed notification
        
        Args:
            to_email: Recipient email
            transaction_data: Transaction details dict
            
        Returns:
            bool: Success status
        """
        template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body { font-family: Arial, sans-serif; background-color: #f5f5f5; }
                .container { max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; }
                .header { background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; padding: 20px; border-radius: 8px 8px 0 0; text-align: center; }
                .content { padding: 20px; }
                .info-row { margin: 15px 0; border-bottom: 1px solid #e5e5e5; padding-bottom: 10px; }
                .label { font-weight: bold; color: #666; font-size: 12px; text-transform: uppercase; }
                .value { font-size: 16px; color: #333; margin-top: 5px; }
                .status-badge { display: inline-block; padding: 8px 16px; background-color: #fee2e2; color: #7c2d12; border-radius: 20px; font-weight: bold; }
                .warning { background-color: #fef2f2; padding: 15px; border-radius: 6px; border-left: 4px solid #ef4444; margin-top: 20px; }
                .button { display: inline-block; margin-top: 20px; padding: 12px 30px; background-color: #ef4444; color: white; text-decoration: none; border-radius: 6px; }
                .footer { text-align: center; color: #999; font-size: 12px; margin-top: 20px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>❌ Payment Failed</h1>
                </div>
                <div class="content">
                    <p>We're sorry,</p>
                    <p>Your cryptocurrency payment could not be processed. Please see details below:</p>
                    
                    <div class="info-row">
                        <div class="label">Transaction ID</div>
                        <div class="value">{{ transaction_id }}</div>
                    </div>
                    
                    <div class="info-row">
                        <div class="label">Payment Amount</div>
                        <div class="value">{{ crypto_amount }} {{ crypto_symbol }} ({{ fiat_amount }} {{ fiat_symbol }})</div>
                    </div>
                    
                    <div class="info-row">
                        <div class="label">Status</div>
                        <div class="value">
                            <span class="status-badge">❌ FAILED</span>
                        </div>
                    </div>
                    
                    <div class="warning">
                        <strong>Reason:</strong> {{ failure_reason }}
                    </div>
                    
                    <p style="margin-top: 30px; color: #666;">
                        Please contact our support team if you need assistance.
                    </p>
                </div>
                <div class="footer">
                    <p>© 2026 Crypto Payment System. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        subject = f"❌ Payment Failed - {transaction_data['transaction_id'][:8]}..."
        html_content = Template(template).render(**transaction_data)
        
        return self.send_email(to_email, subject, html_content)
    
    def send_payment_completed_email(self, to_email: str, transaction_data: dict) -> bool:
        """Send payment completed notification
        
        Args:
            to_email: Recipient email
            transaction_data: Transaction details dict
            
        Returns:
            bool: Success status
        """
        template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body { font-family: Arial, sans-serif; background-color: #f5f5f5; }
                .container { max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; }
                .header { background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); color: white; padding: 20px; border-radius: 8px 8px 0 0; text-align: center; }
                .content { padding: 20px; }
                .info-row { margin: 15px 0; border-bottom: 1px solid #e5e5e5; padding-bottom: 10px; }
                .label { font-weight: bold; color: #666; font-size: 12px; text-transform: uppercase; }
                .value { font-size: 16px; color: #333; margin-top: 5px; }
                .status-badge { display: inline-block; padding: 8px 16px; background-color: #ddd6fe; color: #5b21b6; border-radius: 20px; font-weight: bold; }
                .summary { background-color: #f3f4f6; padding: 15px; border-radius: 6px; margin-top: 20px; }
                .button { display: inline-block; margin-top: 20px; padding: 12px 30px; background-color: #8b5cf6; color: white; text-decoration: none; border-radius: 6px; }
                .footer { text-align: center; color: #999; font-size: 12px; margin-top: 20px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎊 Payment Completed!</h1>
                </div>
                <div class="content">
                    <p>Excellent!</p>
                    <p>Your cryptocurrency payment has been fully processed and completed.</p>
                    
                    <div class="info-row">
                        <div class="label">Transaction ID</div>
                        <div class="value">{{ transaction_id }}</div>
                    </div>
                    
                    <div class="info-row">
                        <div class="label">Payment Amount</div>
                        <div class="value">{{ crypto_amount }} {{ crypto_symbol }}</div>
                    </div>
                    
                    <div class="info-row">
                        <div class="label">Value</div>
                        <div class="value">{{ fiat_amount }} {{ fiat_symbol }}</div>
                    </div>
                    
                    <div class="info-row">
                        <div class="label">Status</div>
                        <div class="value">
                            <span class="status-badge">✨ COMPLETED</span>
                        </div>
                    </div>
                    
                    <div class="info-row">
                        <div class="label">Completed At</div>
                        <div class="value">{{ completed_at }}</div>
                    </div>
                    
                    <div class="summary">
                        <strong>Summary:</strong>
                        <p style="margin-top: 10px;">This transaction is now complete and funds have been processed. You can view your transaction history anytime in your dashboard.</p>
                    </div>
                    
                    <p style="margin-top: 30px; color: #666;">
                        Thank you for using our payment service!
                    </p>
                </div>
                <div class="footer">
                    <p>© 2026 Crypto Payment System. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        subject = f"🎊 Payment Completed - {transaction_data['transaction_id'][:8]}..."
        html_content = Template(template).render(**transaction_data)
        
        return self.send_email(to_email, subject, html_content)
