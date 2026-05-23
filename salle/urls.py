"""
URL Configuration pour l'application GEMBA LEAN
Gestion des URLs pour l'authentification, les dashboards, et la gestion des équipements
"""

from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

# ============================================================================
# IMPORTS SPÉCIFIQUES POUR LA VALIDATION EMAIL
# ============================================================================
# Ces vues sont importées directement car elles ne sont pas accessibles via views.
# (Elles sont définies dans views.py mais pas dans le namespace views par défaut)
from .views import verify_email, resend_verification_email

# ============================================================================
# DÉFINITION DES URLs
# ============================================================================

urlpatterns = [
    # ------------------------------------------------------------------------
    # AUTHENTIFICATION
    # ------------------------------------------------------------------------
    path('', views.dashboard, name='dashboard'),                      # Page d'accueil
    path('login/', views.login_view, name='login'),                   # Connexion
    path('register/', views.register_view, name='register'),          # Inscription
    
    # ------------------------------------------------------------------------
    # VALIDATION EMAIL (NOUVEAUTÉS)
    # ------------------------------------------------------------------------
    # URL pour confirmer l'email via un token UUID (ex: /verify-email/abc123.../)
    path('verify-email/<uuid:token>/', verify_email, name='verify_email'),
    
    # URL pour renvoyer un nouveau lien de vérification
    path('resend-verification/', resend_verification_email, name='resend_verification'),
    
    # ------------------------------------------------------------------------
    # ADMIN - SÉLECTION PAR NIVEAU
    # ------------------------------------------------------------------------
    path('admin/selection/', views.selection_niveau, name='selection_niveau'),
    path('admin/selection/traitement/', views.selection_traitement, name='selection_traitement'),
    path('admin/dashboard/<str:niveau>/<str:semestre>/', views.admin_dashboard_niveau, name='dashboard_admin_niveau'),
    
    # ------------------------------------------------------------------------
    # DASHBOARDS (Tableaux de bord)
    # ------------------------------------------------------------------------
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),           # Admin standard
    path('responsable-dashboard/', views.responsable_dashboard, name='responsable_dashboard'), # Responsable
    path('user-dashboard/', views.user_dashboard, name='user_dashboard'),             # Utilisateur normal
    
    # ------------------------------------------------------------------------
    # GESTION DES CHAISES (CRUD)
    # ------------------------------------------------------------------------
    path('chaises/', views.gestion_chaises, name='gestion_chaises'),                   # Liste + CRUD
    path('chaise/<int:id>/modifier/', views.modifier_chaise, name='modifier_chaise'), # Modification
    
    # ------------------------------------------------------------------------
    # GESTION DES ORDINATEURS (CRUD)
    # ------------------------------------------------------------------------
    path('ordinateurs/', views.gestion_ordinateurs, name='gestion_ordinateurs'),       # Liste + CRUD
    path('ordinateur/<int:id>/modifier/', views.modifier_ordinateur, name='modifier_ordinateur'), # Modification
    
    # ------------------------------------------------------------------------
    # RAPPORTS ET SIGNALEMENTS
    # ------------------------------------------------------------------------
    path('ajouter-rapport/', views.ajouter_rapport, name='ajouter_rapport'),           # Ajouter un rapport
    path('signaler/', views.signaler_probleme, name='signaler_probleme'),              # Signaler un problème
    
    # ------------------------------------------------------------------------
    # VISUALISATION GEMBA (Aller voir sur le terrain)
    # ------------------------------------------------------------------------
    path('visualiser/chaise/<int:id_objet>/', views.visualiser_objet, {'type_objet': 'chaise'}, name='visualiser_chaise'),
    path('visualiser/ordinateur/<int:id_objet>/', views.visualiser_objet, {'type_objet': 'ordinateur'}, name='visualiser_ordinateur'),
    
    # ------------------------------------------------------------------------
    # API POUR AJAX (Appels asynchrones)
    # ------------------------------------------------------------------------
    # Récupérer les chaises et PC disponibles selon la salle
    path('api/chaises-pc-disponibles/', views.get_chaises_pc_disponibles, name='get_chaises_pc_disponibles'),
    
    # Récupérer les informations d'un équipement (chaise ou PC)
    path('api/equipement-info/', views.get_equipement_info, name='get_equipement_info'),
    
    # ------------------------------------------------------------------------
    # GESTION DES ÉTUDIANTS
    # ------------------------------------------------------------------------
    path('gerer-etudiants/', views.gestion_etudiants, name='gestion_etudiants'),
]

# ============================================================================
# SERVIRE LES FICHIERS MÉDIAS EN MODE DÉVELOPPEMENT
# ============================================================================
# Permet d'afficher les photos des chaises, PC, rapports, etc.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)