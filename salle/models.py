from django.db import models
from django.contrib.auth.models import User
from datetime import date
from django.utils import timezone
import uuid  # Importation pour générer des tokens uniques (UUID)

# ============================================================================
# MODÈLE SALLE
# ============================================================================
class Salle(models.Model):
    """Modèle représentant une salle physique"""
    nom = models.CharField(max_length=100, unique=True)  # Nom de la salle (ex: "IATD-SI")
    capacite = models.IntegerField(default=30)  # Nombre maximum de places
    description = models.TextField(blank=True)  # Description optionnelle
    
    def __str__(self):
        return self.nom


# ============================================================================
# MODÈLE CHAISE
# ============================================================================
class Chaise(models.Model):
    """Modèle représentant une chaise dans une salle"""
    ETAT_CHOICES = [
        ('excellent', 'Excellent'),
        ('bon', 'Bon'),
        ('usage', 'Usure normale'),
        ('bancal', 'Bancal'),
        ('casse', 'Cassée'),
        ('graffiti', 'Tag/graffiti'),
    ]
    
    code_unique = models.CharField(max_length=50, unique=True)  # Code unique (ex: CHAISE_005)
    numero = models.IntegerField(unique=True, null=True, blank=True)  # Numéro de 1 à 50
    salle = models.ForeignKey(Salle, on_delete=models.CASCADE, related_name='chaises')
    etat = models.CharField(max_length=20, choices=ETAT_CHOICES, default='bon')
    description = models.TextField(blank=True)
    photo = models.ImageField(upload_to='chaises/', blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_derniere_modification = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        """Génération automatique du code_unique basé sur le numéro"""
        if self.numero and not self.code_unique:
            self.code_unique = f"CHAISE_{self.numero:03d}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Chaise {self.code_unique}"
    
    @property
    def est_assignee(self):
        """Propriété indiquant si la chaise est assignée à un étudiant"""
        return hasattr(self, 'etudiant_assigne') and self.etudiant_assigne is not None


# ============================================================================
# MODÈLE ORDINATEUR (PC)
# ============================================================================
class Ordinateur(models.Model):
    """Modèle représentant un ordinateur/PC dans une salle"""
    ETAT_CHOICES = [
        ('excellent', 'Excellent'),
        ('bon', 'Bon'),
        ('lent', 'Lent'),
        ('ecran_casse', 'Écran cassé'),
        ('clavier_hs', 'Clavier HS'),
        ('souris_hs', 'Souris HS'),
        ('ne_demarre', 'Ne démarre pas'),
    ]
    
    code_unique = models.CharField(max_length=50, unique=True)  # Code unique (ex: PC_005)
    numero = models.IntegerField(unique=True, null=True, blank=True)  # Numéro de 1 à 50
    salle = models.ForeignKey(Salle, on_delete=models.CASCADE, related_name='ordinateurs')
    etat = models.CharField(max_length=30, choices=ETAT_CHOICES, default='bon')
    description = models.TextField(blank=True)
    photo = models.ImageField(upload_to='ordinateurs/', blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_derniere_modification = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        """Génération automatique du code_unique basé sur le numéro"""
        if self.numero and not self.code_unique:
            self.code_unique = f"PC_{self.numero:03d}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"PC {self.code_unique}"
    
    @property
    def est_assigne(self):
        """Propriété indiquant si le PC est assigné à un étudiant"""
        return hasattr(self, 'etudiant_assigne') and self.etudiant_assigne is not None


# ============================================================================
# MODÈLE ÉTUDIANT
# ============================================================================
class Etudiant(models.Model):
    """Modèle représentant un étudiant avec ses équipements assignés"""
    NIVEAU_CHOICES = [
        ('3', '3ème année'),
        ('4', '4ème année'),
        ('5', '5ème année'),
    ]
    
    # Informations personnelles
    matricule = models.CharField(max_length=50, unique=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    niveau = models.CharField(max_length=10, choices=NIVEAU_CHOICES)
    email = models.EmailField(blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    
    # Équipements assignés (OneToOne car une chaise/PC pour un seul étudiant)
    chaise_associee = models.OneToOneField(
        'Chaise', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='etudiant_assigne'
    )
    
    pc_associe = models.OneToOneField(
        'Ordinateur', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='etudiant_assigne'
    )
    
    # Dates
    date_association = models.DateTimeField(null=True, blank=True)
    date_modification = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    @property
    def filiere(self):
        """La filière est fixe pour tous les étudiants"""
        return "IATD - Système Industriel"
    
    def save(self, *args, **kwargs):
        """Définit automatiquement la date d'association si elle n'existe pas"""
        if not self.date_association:
            self.date_association = timezone.now()
        super().save(*args, **kwargs)
    
    def __str__(self):
        equipement = []
        if self.chaise_associee:
            equipement.append(f"Chaise: {self.chaise_associee.code_unique}")
        if self.pc_associe:
            equipement.append(f"PC: {self.pc_associe.code_unique}")
        
        suffixe = f" - {', '.join(equipement)}" if equipement else " - Non équipé"
        return f"{self.matricule} - {self.nom} {self.prenom} ({self.get_niveau_display()}){suffixe}"
    
    def get_niveau_display(self):
        """Retourne le libellé du niveau"""
        return dict(self.NIVEAU_CHOICES).get(self.niveau, self.niveau)


# ============================================================================
# MODÈLE SÉANCE
# ============================================================================
class Seance(models.Model):
    """Modèle représentant une séance de cours"""
    NIVEAU_CHOICES = [
        ('3', '3ème année'),
        ('4', '4ème année'),
        ('5', '5ème année'),
    ]
    
    SEMESTRE_CHOICES = [
        ('1', 'Semestre 1'),
        ('2', 'Semestre 2'),
    ]
    
    salle = models.ForeignKey(Salle, on_delete=models.CASCADE)
    professeur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seances')
    niveau = models.CharField(max_length=10, choices=NIVEAU_CHOICES)
    semestre = models.CharField(max_length=10, choices=SEMESTRE_CHOICES, default='1')
    date_seance = models.DateField(default=date.today)
    commentaire = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    @property
    def filiere(self):
        """La filière est fixe pour toutes les séances"""
        return "IATDSI - Système Industriel"
    
    def __str__(self):
        return f"{self.salle.nom} - IATDSI {self.get_niveau_display()} - {self.get_semestre_display()} - {self.date_seance}"
    
    def get_semestre_display(self):
        return dict(self.SEMESTRE_CHOICES).get(self.semestre, self.semestre)


# ============================================================================
# MODÈLE OCCUPATION SÉANCE
# ============================================================================
class OccupationSeance(models.Model):
    """Modèle liant les étudiants aux équipements utilisés pendant une séance"""
    seance = models.ForeignKey(Seance, on_delete=models.CASCADE, related_name='occupations')
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE)
    chaise = models.ForeignKey(Chaise, on_delete=models.CASCADE)
    ordinateur = models.ForeignKey(Ordinateur, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('seance', 'etudiant')  # Un étudiant ne peut être qu'une fois par séance
    
    def __str__(self):
        return f"{self.seance} - {self.etudiant.matricule}"


# ============================================================================
# MODÈLE RAPPORT SALLE
# ============================================================================
class RapportSalle(models.Model):
    """Modèle pour les rapports d'état de la salle (Gemba)"""
    ORDRE_CHOICES = [
        (1, 'Très désordonné'),
        (2, 'Désordonné'),
        (3, 'Correct'),
        (4, 'Organisé'),
        (5, 'Très organisé'),
    ]
    
    salle = models.ForeignKey(Salle, on_delete=models.CASCADE, related_name='rapports')
    responsable = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    photo = models.ImageField(upload_to='rapports_salle/%Y/%m/%d/')
    commentaire = models.TextField(help_text="État général de la salle, problèmes constatés")
    ordre_general = models.IntegerField(choices=ORDRE_CHOICES, default=3)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Rapport {self.salle.nom} - {self.date}"


# ============================================================================
# MODÈLE SIGNALEMENT
# ============================================================================
class Signalement(models.Model):
    """Modèle pour les signalements de problèmes (chaises/PC)"""
    TYPE_CHOICES = [
        ('chaise', 'Chaise'),
        ('ordinateur', 'Ordinateur'),
        ('autre', 'Autre'),
    ]
    
    type_probleme = models.CharField(max_length=20, choices=TYPE_CHOICES)
    objet_id = models.PositiveIntegerField(blank=True, null=True, help_text="ID de la chaise ou de l'ordinateur concerné")
    description = models.TextField()
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    resolu = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.get_type_probleme_display()} - {self.date}"


# ============================================================================
# ==================== NOUVEAU MODÈLE POUR LA VALIDATION EMAIL ====================
# ============================================================================
# Ce modèle a été ajouté pour permettre la vérification des emails des utilisateurs
# avant qu'ils puissent se connecter à l'application.
#
# Fonctionnalités :
# - Génère un token unique (UUID) pour chaque utilisateur
# - Stocke la date de création du token (expiration 24h)
# - Permet de vérifier si l'email a été confirmé
# - Permet de générer un nouveau token en cas d'expiration
# ============================================================================

class EmailVerificationToken(models.Model):
    """
    Modèle pour gérer la validation des emails des utilisateurs.
    
    Ce modèle est lié un-à-un avec l'utilisateur Django standard.
    Il permet de :
        1. Générer un token unique pour chaque nouvel utilisateur
        2. Vérifier si l'email a été confirmé avant de permettre la connexion
        3. Gérer l'expiration des tokens après 24 heures
        4. Renvoyer un nouveau token si nécessaire
    """
    
    # Relation OneToOne avec l'utilisateur Django standard
    # related_name='email_verification' permet d'accéder au token via user.email_verification
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='email_verification')
    
    # Token unique généré automatiquement avec UUID (Universally Unique Identifier)
    # UUID est utilisé car il est pratiquement impossible à deviner/dupliquer
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    # Date et heure de création du token (utilisée pour vérifier l'expiration)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Champ booléen indiquant si l'email a été vérifié avec succès
    email_verified = models.BooleanField(default=False)
    
    def __str__(self):
        """Représentation textuelle du modèle"""
        return f"Token de vérification pour {self.user.username}"
    
    def is_expired(self):
        """
        Vérifie si le token a expiré (délai de 24 heures).
        
        Returns:
            bool: True si le token a plus de 24h, False sinon
        """
        from django.utils import timezone
        from datetime import timedelta
        return timezone.now() > self.created_at + timedelta(hours=24)
    
    def generate_new_token(self):
        """
        Génère un nouveau token pour l'utilisateur.
        
        Utile quand :
        - Le token a expiré
        - L'utilisateur demande un nouveau lien de vérification
        
        Returns:
            UUID: Le nouveau token généré
        """
        self.token = uuid.uuid4()  # Génération d'un nouveau UUID
        self.created_at = timezone.now()  # Réinitialisation de la date
        self.save()  # Sauvegarde en base de données
        return self.token