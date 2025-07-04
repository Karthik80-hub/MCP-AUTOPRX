#!/usr/bin/env python3
"""
Gmail notification tool for MCP server.
Sends emails via Gmail SMTP.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

def send_gmail_notification(subject: str, message: str, recipient: str = None) -> str:
    """
    Send a Gmail notification.
    
    Args:
        subject: Email subject
        message: Email message content
        recipient: Email recipient (optional, uses DEFAULT_EMAIL_RECIPIENT if not provided)
    
    Returns:
        Status message indicating success or failure
    """
    gmail_user = os.getenv("GMAIL_USER")
    gmail_password = os.getenv("GMAIL_APP_PASSWORD")
    default_recipient = os.getenv("DEFAULT_EMAIL_RECIPIENT")
    
    if not gmail_user or not gmail_password:
        return "Error: GMAIL_USER and GMAIL_APP_PASSWORD environment variables not set"
    
    recipient = recipient or default_recipient
    if not recipient:
        return "Error: No recipient email specified and DEFAULT_EMAIL_RECIPIENT not set"
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = gmail_user
        msg['To'] = recipient
        msg['Subject'] = subject
        
        # Create HTML body
        html_body = f"""
        <html>
        <body>
            <h2>{subject}</h2>
            <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                {message.replace(chr(10), '<br>')}
            </div>
            <hr style="margin: 20px 0; border: none; border-top: 1px solid #eee;">
            <p style="color: #666; font-size: 12px; margin-top: 20px;">
                Sent by MCP-AutoPRX Server
            </p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_body, 'html'))
        
        # Send email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(gmail_user, gmail_password)
        text = msg.as_string()
        server.sendmail(gmail_user, recipient, text)
        server.quit()
        
        return f"Gmail notification sent successfully to {recipient}"
        
    except smtplib.SMTPAuthenticationError:
        return "Error: Gmail authentication failed. Check GMAIL_USER and GMAIL_APP_PASSWORD"
    except smtplib.SMTPRecipientsRefused:
        return f"Error: Recipient email {recipient} was refused"
    except smtplib.SMTPServerDisconnected:
        return "Error: Gmail server disconnected. Please try again"
    except Exception as e:
        return f"Error sending Gmail notification: {str(e)}"

def send_gmail_alert(subject: str, message: str, recipient: str = None) -> str:
    """
    Alias for send_gmail_notification for consistency with Slack notifier.
    """
    return send_gmail_notification(subject, message, recipient) 