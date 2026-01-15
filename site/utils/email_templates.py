"""
Email Template Manager
Consolidates email templates and sending logic for the application
"""

from flask import url_for, current_app
from flask_mail import Mail, Message


def get_verification_email_html(username: str, verify_url: str) -> str:
    """
    Generate HTML for email verification
    
    Args:
        username: User's display name
        verify_url: Full verification URL
    
    Returns:
        HTML string for email body
    """
    return f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="background-color: #0b0d12; padding: 20px; color: white;">
                <h2 style="margin: 0;">Aerium CO₂ Monitor</h2>
            </div>
            <div style="padding: 20px;">
                <p>Bonjour {username},</p>
                <p>Merci de vous être inscrit à Aerium CO₂ Monitor. Veuillez confirmer votre adresse email en cliquant sur le lien ci-dessous:</p>
                <p><a href="{verify_url}" style="background-color: #3dd98f; color: white; padding: 10px 15px; text-decoration: none; border-radius: 5px;">Vérifier mon email</a></p>
                <p>Ce lien expirera dans 24 heures.</p>
            </div>
            <div style="background-color: #f5f7fa; padding: 15px; font-size: 0.9em; color: #666;">
                <p>Si vous n'avez pas créé de compte, ignorez cet email.</p>
            </div>
        </body>
    </html>
    """


def get_password_reset_email_html(username: str, reset_url: str) -> str:
    """
    Generate HTML for password reset email
    
    Args:
        username: User's display name
        reset_url: Full password reset URL
    
    Returns:
        HTML string for email body
    """
    return f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="background-color: #0b0d12; padding: 20px; color: white;">
                <h2 style="margin: 0;">Aerium CO₂ Monitor</h2>
            </div>
            <div style="padding: 20px;">
                <p>Bonjour {username},</p>
                <p>Vous avez demandé une réinitialisation de votre mot de passe. Cliquez sur le lien ci-dessous pour procéder:</p>
                <p><a href="{reset_url}" style="background-color: #4db8ff; color: white; padding: 10px 15px; text-decoration: none; border-radius: 5px;">Réinitialiser mon mot de passe</a></p>
                <p>Ce lien expirera dans 1 heure.</p>
            </div>
            <div style="background-color: #f5f7fa; padding: 15px; font-size: 0.9em; color: #666;">
                <p>Si vous n'avez pas demandé cette action, vous pouvez ignorer cet email.</p>
            </div>
        </body>
    </html>
    """


def send_verification_email(email: str, username: str, token: str) -> bool:
    """
    Send email verification link to user
    
    Args:
        email: User's email address
        username: User's display name
        token: Verification token
    
    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        from flask_mail import Mail, Message
        mail = Mail(current_app)
        verify_url = url_for('auth.verify_email', token=token, _external=True)
        
        subject = "Verify your Aerium CO₂ Account"
        html_body = get_verification_email_html(username, verify_url)
        
        msg = Message(subject=subject, recipients=[email], html=html_body)
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send verification email to {email}: {str(e)}")
        return False


def send_password_reset_email(email: str, username: str, token: str) -> bool:
    """
    Send password reset email to user
    
    Args:
        email: User's email address
        username: User's display name
        token: Password reset token
    
    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        from flask_mail import Mail, Message
        mail = Mail(current_app)
        reset_url = url_for('auth.reset_password_page', token=token, _external=True)
        
        subject = "Reset your Aerium CO₂ password"
        html_body = get_password_reset_email_html(username, reset_url)
        
        msg = Message(subject=subject, recipients=[email], html=html_body)
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send password reset email to {email}: {str(e)}")
        return False
