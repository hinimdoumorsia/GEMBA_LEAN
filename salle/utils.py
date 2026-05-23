# salle/utils.py
"""
Utils pour l'envoi d'emails - GEMBA LEAN
Gestion des emails de vérification, bienvenue et réinitialisation de mot de passe
"""

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# EMAIL DE VÉRIFICATION (Envoyé à l'inscription)
# ============================================================================

def send_verification_email(request, user, token):
    """
    Envoie l'email de vérification avec token.
    L'utilisateur doit cliquer sur le lien pour activer son compte.
    """
    try:
        # Construire le lien de vérification
        current_site = get_current_site(request)
        verification_link = f"http://{current_site.domain}/verify-email/{token}/"
        
        subject = '🔐 Confirmez votre inscription - GEMBA LEAN'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [user.email]
        
        # Générer le contenu HTML depuis le template
        html_content = render_to_string('emails/verification_email.html', {
            'user': user,
            'verification_link': verification_link,
            'site_name': 'GEMBA LEAN',
            'expiry_hours': 24
        })
        
        # Version texte brut (pour les clients email qui ne supportent pas HTML)
        text_content = strip_tags(html_content)
        
        # Créer l'email avec EmailMultiAlternatives
        email = EmailMultiAlternatives(
            subject,
            text_content,
            from_email,
            to_email,
        )
        # Attacher la version HTML (c'est ce qui rend les liens cliquables)
        email.attach_alternative(html_content, "text/html")
        
        # Envoyer l'email
        email.send(fail_silently=False)
        
        logger.info(f"✅ Email de vérification envoyé à {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur envoi email vérification: {str(e)}")
        return False


# ============================================================================
# EMAIL DE BIENVENUE (Envoyé après validation du compte)
# ============================================================================

def send_welcome_email(user, request=None):
    """
    Envoie l'email de bienvenue après validation du compte.
    Félicite l'utilisateur et l'invite à se connecter.
    """
    try:
        subject = '🎉 Bienvenue sur GEMBA LEAN - ENSAM Meknès'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [user.email]
        
        # Déterminer l'URL du site
        if request:
            current_site = get_current_site(request)
            site_url = f"http://{current_site.domain}"
        else:
            site_url = settings.SITE_URL
        
        # Générer le contenu HTML depuis le template
        html_content = render_to_string('emails/welcome_email.html', {
            'user': user,
            'site_name': 'GEMBA LEAN',
            'site_url': site_url,
            'ensam_location': 'ENSAM Meknès - IA & Technologies de Données'
        })
        
        # Version texte brut
        text_content = strip_tags(html_content)
        
        # Créer l'email avec EmailMultiAlternatives
        email = EmailMultiAlternatives(
            subject,
            text_content,
            from_email,
            to_email,
        )
        # Attacher la version HTML
        email.attach_alternative(html_content, "text/html")
        
        # Envoyer l'email
        email.send(fail_silently=False)
        
        logger.info(f"✅ Email de bienvenue envoyé à {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur envoi email bienvenue: {str(e)}")
        return False


# ============================================================================
# EMAIL DE RÉINITIALISATION MOT DE PASSE (Optionnel)
# ============================================================================

def send_password_reset_email(request, user, token):
    """
    Envoie l'email de réinitialisation de mot de passe.
    L'utilisateur peut créer un nouveau mot de passe via le lien.
    """
    try:
        current_site = get_current_site(request)
        reset_link = f"http://{current_site.domain}/reset-password/{token}/"
        
        subject = '🔑 Réinitialisation de votre mot de passe - GEMBA LEAN'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [user.email]
        
        # Générer le contenu HTML
        html_content = render_to_string('emails/password_reset_email.html', {
            'user': user,
            'reset_link': reset_link,
            'site_name': 'GEMBA LEAN'
        })
        
        # Version texte brut
        text_content = strip_tags(html_content)
        
        # Créer l'email avec EmailMultiAlternatives
        email = EmailMultiAlternatives(
            subject,
            text_content,
            from_email,
            to_email,
        )
        # Attacher la version HTML
        email.attach_alternative(html_content, "text/html")
        
        # Envoyer l'email
        email.send(fail_silently=False)
        
        logger.info(f"✅ Email réinitialisation envoyé à {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur envoi reset password: {str(e)}")
        return False