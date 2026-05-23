from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import *
from .forms import *
from .utils import send_verification_email, send_welcome_email
import json
from datetime import date
import uuid

def is_admin(user):
    return user.is_superuser

def is_responsable(user):
    return user.groups.filter(name='Responsable').exists() or user.is_superuser

@login_required
def dashboard(request):
    user = request.user
    if user.is_superuser:
        return redirect('selection_niveau')
    elif user.groups.filter(name='Responsable').exists():
        return redirect('responsable_dashboard')
    else:
        return redirect('user_dashboard')

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    chaises = Chaise.objects.all()
    ordinateurs = Ordinateur.objects.all()
    signalements = Signalement.objects.filter(resolu=False)
    return render(request, 'dashboard/admin_dashboard.html', {
        'chaises': chaises,
        'ordinateurs': ordinateurs,
        'signalements': signalements,
    })

@login_required
@user_passes_test(is_responsable)
def responsable_dashboard(request):
    rapports = RapportSalle.objects.all().order_by('-date')
    return render(request, 'dashboard/responsable_dashboard.html', {'rapports': rapports})

@login_required
def user_dashboard(request):
    signalements = Signalement.objects.filter(utilisateur=request.user)
    return render(request, 'dashboard/user_dashboard.html', {'signalements': signalements})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            # Vérifier si l'email est validé
            try:
                token_obj = EmailVerificationToken.objects.get(user=user)
                if not token_obj.email_verified:
                    messages.error(request, 'Veuillez vérifier votre email avant de vous connecter. Un nouveau lien de validation vous a été envoyé.')
                    new_token = token_obj.generate_new_token()
                    send_verification_email(request, user, new_token)
                    return redirect('login')
            except EmailVerificationToken.DoesNotExist:
                pass
            
            login(request, user)
            return redirect('dashboard')
        messages.error(request, 'Identifiants invalides')
    return render(request, 'registration/login.html')

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.save()
            
            token_obj = EmailVerificationToken.objects.create(
                user=user,
                token=uuid.uuid4(),
                email_verified=False
            )
            
            if send_verification_email(request, user, token_obj.token):
                messages.success(request, 'Un email de vérification a été envoyé à votre adresse. Veuillez vérifier votre boîte de réception pour activer votre compte.')
            else:
                messages.warning(request, "Votre compte a été créé mais l'envoi de l'email de vérification a échoué. Veuillez contacter l'administrateur.")
            
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

def verify_email(request, token):
    """Vue pour vérifier l'email de l'utilisateur"""
    try:
        token_obj = EmailVerificationToken.objects.get(token=token)
        
        if token_obj.is_expired():
            new_token = token_obj.generate_new_token()
            send_verification_email(request, token_obj.user, new_token)
            messages.warning(request, 'Votre lien de validation a expiré. Un nouveau lien vous a été envoyé par email.')
            return redirect('login')
        
        token_obj.email_verified = True
        token_obj.save()
        
        send_welcome_email(token_obj.user, request)
        
        messages.success(request, 'Votre email a été vérifié avec succès ! Vous pouvez maintenant vous connecter.')
        return redirect('login')
        
    except EmailVerificationToken.DoesNotExist:
        messages.error(request, 'Lien de vérification invalide.')
        return redirect('login')

def resend_verification_email(request):
    """Renvoie un email de vérification"""
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            token_obj, created = EmailVerificationToken.objects.get_or_create(
                user=user,
                defaults={'token': uuid.uuid4(), 'email_verified': False}
            )
            
            if token_obj.email_verified:
                messages.info(request, 'Cet email est déjà vérifié. Vous pouvez vous connecter.')
            else:
                if token_obj.is_expired():
                    token_obj.generate_new_token()
                send_verification_email(request, user, token_obj.token)
                messages.success(request, 'Un nouveau lien de vérification a été envoyé à votre adresse email.')
        except User.DoesNotExist:
            messages.error(request, 'Aucun compte associé à cet email.')
        
        return redirect('login')
    
    return render(request, 'registration/resend_verification.html')

@login_required
@user_passes_test(is_admin)
def gestion_chaises(request):
    salles = Salle.objects.all()
    chaises = Chaise.objects.all()
    
    niveau_actuel = request.session.get('niveau_actuel', '3')
    semestre_actuel = request.session.get('semestre_actuel', '1')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'ajouter':
            try:
                numero = request.POST.get('numero')
                
                if not numero:
                    messages.error(request, 'Veuillez sélectionner un numéro pour la chaise')
                    return redirect('gestion_chaises')
                
                salle_id = request.POST.get('salle')
                etat = request.POST.get('etat')
                description = request.POST.get('description', '')
                photo = request.FILES.get('photo')
                
                numero_int = int(numero)
                
                if Chaise.objects.filter(numero=numero_int).exists():
                    messages.error(request, f'Une chaise avec le numéro {numero_int} existe déjà')
                    return redirect('gestion_chaises')
                
                salle = get_object_or_404(Salle, id=salle_id)
                
                chaise = Chaise.objects.create(
                    numero=numero_int,
                    code_unique=f"CHAISE_{numero_int:03d}",
                    salle=salle,
                    etat=etat,
                    description=description,
                    photo=photo
                )
                
                messages.success(request, f'Chaise N°{numero_int} ajoutée avec succès')
                
            except ValueError as e:
                messages.error(request, f'Numéro invalide: {str(e)}')
            except Exception as e:
                messages.error(request, f'Erreur lors de l\'ajout: {str(e)}')
            
            return redirect('gestion_chaises')
        
        elif action == 'supprimer':
            try:
                chaise_id = request.POST.get('chaise_id')
                chaise = get_object_or_404(Chaise, id=chaise_id)
                numero = chaise.numero
                
                if hasattr(chaise, 'etudiant_assigne') and chaise.etudiant_assigne:
                    etudiant = chaise.etudiant_assigne
                    etudiant.chaise_associee = None
                    etudiant.save()
                    messages.warning(request, f'La chaise N°{numero} était assignée à {etudiant.nom} {etudiant.prenom}. Elle a été libérée.')
                
                chaise.delete()
                messages.success(request, f'Chaise N°{numero} supprimée avec succès')
                
            except Exception as e:
                messages.error(request, f'Erreur lors de la suppression: {str(e)}')
            
            return redirect('gestion_chaises')
    
    numeros_existants = list(chaises.filter(numero__isnull=False).values_list('numero', flat=True))
    
    context = {
        'chaises': chaises,
        'salles': salles,
        'numeros_existants': numeros_existants,
        'niveau_actuel': niveau_actuel,
        'semestre_actuel': semestre_actuel,
    }
    return render(request, 'salle/liste_chaises.html', context)

@login_required
@user_passes_test(is_admin)
def modifier_chaise(request, id):
    chaise = get_object_or_404(Chaise, id=id)
    if request.method == 'POST':
        form = ChaiseForm(request.POST, request.FILES, instance=chaise)
        if form.is_valid():
            form.save()
            messages.success(request, 'Chaise modifiée avec succès')
            return redirect('gestion_chaises')
    else:
        form = ChaiseForm(instance=chaise)
    return render(request, 'salle/modifier_chaise.html', {'form': form, 'chaise': chaise})

@login_required
@user_passes_test(is_admin)
def gestion_ordinateurs(request):
    salles = Salle.objects.all()
    ordinateurs = Ordinateur.objects.all()
    
    niveau_actuel = request.session.get('niveau_actuel', '3')
    semestre_actuel = request.session.get('semestre_actuel', '1')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'ajouter':
            try:
                numero = request.POST.get('numero')
                
                if not numero:
                    messages.error(request, 'Veuillez sélectionner un numéro pour le PC')
                    return redirect('gestion_ordinateurs')
                
                salle_id = request.POST.get('salle')
                etat = request.POST.get('etat')
                description = request.POST.get('description', '')
                photo = request.FILES.get('photo')
                
                numero_int = int(numero)
                
                if Ordinateur.objects.filter(numero=numero_int).exists():
                    messages.error(request, f'Un PC avec le numéro {numero_int} existe déjà')
                    return redirect('gestion_ordinateurs')
                
                salle = get_object_or_404(Salle, id=salle_id)
                
                ordinateur = Ordinateur.objects.create(
                    numero=numero_int,
                    code_unique=f"PC_{numero_int:03d}",
                    salle=salle,
                    etat=etat,
                    description=description,
                    photo=photo
                )
                
                messages.success(request, f'PC N°{numero_int} ajouté avec succès')
                
            except ValueError as e:
                messages.error(request, f'Numéro invalide: {str(e)}')
            except Exception as e:
                messages.error(request, f'Erreur lors de l\'ajout: {str(e)}')
            
            return redirect('gestion_ordinateurs')
        
        elif action == 'supprimer':
            try:
                ordinateur_id = request.POST.get('ordinateur_id')
                ordinateur = get_object_or_404(Ordinateur, id=ordinateur_id)
                numero = ordinateur.numero
                
                # CORRECTION: Vérification sécurisée
                if hasattr(ordinateur, 'etudiant_assigne') and ordinateur.etudiant_assigne is not None:
                    etudiant = ordinateur.etudiant_assigne
                    etudiant.pc_associe = None
                    etudiant.save()
                    messages.warning(request, f'Le PC N°{numero} était assigné à {etudiant.nom} {etudiant.prenom}. Il a été libéré.')
                
                ordinateur.delete()
                messages.success(request, f'PC N°{numero} supprimé avec succès')
                
            except Exception as e:
                messages.error(request, f'Erreur lors de la suppression: {str(e)}')
            
            return redirect('gestion_ordinateurs')
    
    numeros_existants = list(ordinateurs.filter(numero__isnull=False).values_list('numero', flat=True))
    
    context = {
        'ordinateurs': ordinateurs,
        'salles': salles,
        'numeros_existants': numeros_existants,
        'niveau_actuel': niveau_actuel,
        'semestre_actuel': semestre_actuel,
    }
    return render(request, 'salle/liste_ordinateurs.html', context)

@login_required
@user_passes_test(is_admin)
def modifier_ordinateur(request, id):
    ordi = get_object_or_404(Ordinateur, id=id)
    if request.method == 'POST':
        form = OrdinateurForm(request.POST, request.FILES, instance=ordi)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ordinateur modifié avec succès')
            return redirect('gestion_ordinateurs')
    else:
        form = OrdinateurForm(instance=ordi)
    return render(request, 'salle/modifier_ordinateur.html', {'form': form, 'ordinateur': ordi})

@login_required
@user_passes_test(is_responsable)
def ajouter_rapport(request):
    if request.method == 'POST':
        form = RapportForm(request.POST, request.FILES)
        if form.is_valid():
            rapport = form.save(commit=False)
            rapport.responsable = request.user
            rapport.save()
            messages.success(request, 'Rapport ajouté avec succès')
            return redirect('responsable_dashboard')
    else:
        form = RapportForm()
    return render(request, 'responsable/ajouter_rapport.html', {'form': form})

@login_required
def signaler_probleme(request):
    if request.method == 'POST':
        form = SignalementForm(request.POST)
        if form.is_valid():
            signalement = form.save(commit=False)
            signalement.utilisateur = request.user
            signalement.save()
            messages.success(request, 'Problème signalé avec succès')
            return redirect('user_dashboard')
    else:
        form = SignalementForm()
    return render(request, 'signalement/signaler_probleme.html', {'form': form})

@login_required
def visualiser_objet(request, type_objet, id_objet):
    if type_objet == 'chaise':
        objet = get_object_or_404(Chaise, id=id_objet)
        template = 'salle/visualiser_chaise.html'
    elif type_objet == 'ordinateur':
        objet = get_object_or_404(Ordinateur, id=id_objet)
        template = 'salle/visualiser_ordinateur.html'
    else:
        messages.error(request, 'Type d\'objet invalide')
        return redirect('dashboard')
    
    etudiant_associe = None
    if type_objet == 'chaise':
        if hasattr(objet, 'etudiant_assigne') and objet.etudiant_assigne:
            etudiant_associe = objet.etudiant_assigne
    elif type_objet == 'ordinateur':
        if hasattr(objet, 'etudiant_assigne') and objet.etudiant_assigne:
            etudiant_associe = objet.etudiant_assigne
    
    return render(request, template, {
        'objet': objet,
        'etudiant_associe': etudiant_associe,
    })

@login_required
@user_passes_test(is_admin)
def get_chaises_pc_disponibles(request):
    salle_id = request.GET.get('salle_id')
    if salle_id:
        chaises = Chaise.objects.filter(salle_id=salle_id).values('id', 'code_unique', 'etat', 'numero')
        ordinateurs = Ordinateur.objects.filter(salle_id=salle_id).values('id', 'code_unique', 'etat', 'numero')
        return JsonResponse({
            'chaises': list(chaises),
            'ordinateurs': list(ordinateurs)
        })
    return JsonResponse({'chaises': [], 'ordinateurs': []})

# ========== VUES POUR LA SÉLECTION PAR NIVEAU ==========

@login_required
@user_passes_test(is_admin)
def selection_niveau(request):
    if request.method == 'POST':
        niveau = request.POST.get('niveau')
        semestre = request.POST.get('semestre')
        request.session['niveau_actuel'] = niveau
        request.session['semestre_actuel'] = semestre
        return redirect('dashboard_admin_niveau', niveau=niveau, semestre=semestre)
    return render(request, 'dashboard/selection_admin.html')

@login_required
@user_passes_test(is_admin)
def selection_traitement(request):
    if request.method == 'POST':
        niveau = request.POST.get('niveau')
        semestre = request.POST.get('semestre')
        request.session['niveau_actuel'] = niveau
        request.session['semestre_actuel'] = semestre
        return redirect('dashboard_admin_niveau', niveau=niveau, semestre=semestre)
    return redirect('selection_niveau')

@login_required
@user_passes_test(is_admin)
def admin_dashboard_niveau(request, niveau, semestre):
    request.session['niveau_actuel'] = niveau
    request.session['semestre_actuel'] = semestre
    
    salle, created = Salle.objects.get_or_create(
        nom='IATD-SI',
        defaults={'capacite': 30, 'description': 'Salle principale IATD - Système Industriel'}
    )
    
    chaises = Chaise.objects.filter(salle=salle)
    ordinateurs = Ordinateur.objects.filter(salle=salle)
    signalements = Signalement.objects.filter(resolu=False)
    total_etudiants = Etudiant.objects.filter(niveau=niveau).count()
    
    niveau_texte = get_niveau_texte(niveau)
    semestre_texte = "Semestre Unique" if niveau == '5' else f"Semestre {semestre}"
    
    return render(request, 'dashboard/admin_dashboard.html', {
        'chaises': chaises,
        'ordinateurs': ordinateurs,
        'signalements': signalements,
        'niveau_selectionne': niveau_texte,
        'semestre_selectionne': semestre_texte,
        'niveau_actuel': niveau,
        'semestre_actuel': semestre,
        'total_etudiants': total_etudiants,
        'admin_name': request.user.get_full_name() or request.user.username,
    })

def get_niveau_texte(niveau):
    niveaux = {
        '3': '3ème Année',
        '4': '4ème Année',
        '5': '5ème Année'
    }
    return niveaux.get(niveau, 'Inconnu')

# ========== VUE POUR LA GESTION DES ÉTUDIANTS ==========

@login_required
@user_passes_test(is_admin)
def gestion_etudiants(request):
    niveau_actuel = request.GET.get('niveau') or request.session.get('niveau_actuel')
    semestre_actuel = request.GET.get('semestre') or request.session.get('semestre_actuel')
    
    if niveau_actuel:
        etudiants = Etudiant.objects.filter(niveau=niveau_actuel).select_related('chaise_associee', 'pc_associe').order_by('nom')
    else:
        etudiants = Etudiant.objects.all().select_related('chaise_associee', 'pc_associe').order_by('niveau', 'nom')
    
    # Générer la liste des numéros 1 à 50 avec leurs statuts
    numeros_disponibles = []
    for i in range(1, 51):
        chaise_occupee = Chaise.objects.filter(numero=i, etudiant_assigne__isnull=False).exists()
        pc_occupe = Ordinateur.objects.filter(numero=i, etudiant_assigne__isnull=False).exists()
        numeros_disponibles.append({
            'numero': i,
            'chaise_occupee': chaise_occupee,
            'pc_occupe': pc_occupe
        })
    
    chaises_disponibles_select = Chaise.objects.filter(etudiant_assigne__isnull=True).order_by('numero')
    pc_disponibles_select = Ordinateur.objects.filter(etudiant_assigne__isnull=True).order_by('numero')
    toutes_chaises_select = Chaise.objects.all().order_by('numero')
    tous_pc_select = Ordinateur.objects.all().order_by('numero')
    
    chaises_assignees_count = Chaise.objects.filter(etudiant_assigne__isnull=False).count()
    pc_assigne_count = Ordinateur.objects.filter(etudiant_assigne__isnull=False).count()
    
    chaises_disponibles = chaises_disponibles_select
    pc_disponibles = pc_disponibles_select
    toutes_chaises = Chaise.objects.all()
    tous_pc = Ordinateur.objects.all()
    chaises_numeros_utilises = list(Chaise.objects.filter(etudiant_assigne__isnull=False).values_list('numero', flat=True))
    pc_numeros_utilises = list(Ordinateur.objects.filter(etudiant_assigne__isnull=False).values_list('numero', flat=True))
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'ajouter':
            try:
                matricule = request.POST.get('matricule')
                nom = request.POST.get('nom')
                prenom = request.POST.get('prenom')
                niveau = request.POST.get('niveau')
                email = request.POST.get('email', '')
                telephone = request.POST.get('telephone', '')
                
                if Etudiant.objects.filter(matricule=matricule).exists():
                    messages.error(request, f'Un étudiant avec le matricule {matricule} existe déjà')
                    return redirect(f'/gerer-etudiants/?niveau={niveau_actuel}&semestre={semestre_actuel}' if niveau_actuel else 'gestion_etudiants')
                
                chaise = None
                pc = None
                
                assignation_group = request.POST.get('assignation_group')
                if assignation_group:
                    numero_assign = int(assignation_group)
                    chaise = Chaise.objects.filter(numero=numero_assign, etudiant_assigne__isnull=True).first()
                    pc = Ordinateur.objects.filter(numero=numero_assign, etudiant_assigne__isnull=True).first()
                    
                    if not chaise:
                        messages.error(request, f'La chaise N°{numero_assign} n\'existe pas ou est déjà assignée')
                        return redirect(f'/gerer-etudiants/?niveau={niveau_actuel}&semestre={semestre_actuel}' if niveau_actuel else 'gestion_etudiants')
                    
                    if not pc:
                        messages.error(request, f'Le PC N°{numero_assign} n\'existe pas ou est déjà assigné')
                        return redirect(f'/gerer-etudiants/?niveau={niveau_actuel}&semestre={semestre_actuel}' if niveau_actuel else 'gestion_etudiants')
                else:
                    chaise_value = request.POST.get('chaise')
                    pc_value = request.POST.get('pc')
                    
                    if chaise_value:
                        chaise_numero = chaise_value.split('_')[1]
                        chaise = Chaise.objects.filter(numero=chaise_numero, etudiant_assigne__isnull=True).first()
                        if not chaise:
                            messages.error(request, f'La chaise N°{chaise_numero} n\'est pas disponible')
                            return redirect(f'/gerer-etudiants/?niveau={niveau_actuel}&semestre={semestre_actuel}' if niveau_actuel else 'gestion_etudiants')
                    
                    if pc_value:
                        pc_numero = pc_value.split('_')[1]
                        pc = Ordinateur.objects.filter(numero=pc_numero, etudiant_assigne__isnull=True).first()
                        if not pc:
                            messages.error(request, f'Le PC N°{pc_numero} n\'est pas disponible')
                            return redirect(f'/gerer-etudiants/?niveau={niveau_actuel}&semestre={semestre_actuel}' if niveau_actuel else 'gestion_etudiants')
                
                if not chaise and not pc:
                    messages.error(request, 'Un étudiant doit avoir au moins une chaise OU un PC assigné')
                    return redirect(f'/gerer-etudiants/?niveau={niveau_actuel}&semestre={semestre_actuel}' if niveau_actuel else 'gestion_etudiants')
                
                etudiant = Etudiant.objects.create(
                    matricule=matricule,
                    nom=nom,
                    prenom=prenom,
                    niveau=niveau,
                    email=email,
                    telephone=telephone,
                    chaise_associee=chaise,
                    pc_associe=pc
                )
                
                messages.success(request, f'Étudiant {nom} {prenom} ajouté avec succès')
                
            except Exception as e:
                messages.error(request, f'Erreur lors de l\'ajout: {str(e)}')
            
            if niveau_actuel:
                return redirect(f'/gerer-etudiants/?niveau={niveau_actuel}&semestre={semestre_actuel}')
            return redirect('gestion_etudiants')
        
        elif action == 'modifier':
            try:
                etudiant_id = request.POST.get('etudiant_id')
                etudiant = get_object_or_404(Etudiant, id=etudiant_id)
                
                nouvelle_chaise_value = request.POST.get('chaise')
                nouveau_pc_value = request.POST.get('pc')
                nouveau_niveau = request.POST.get('niveau')
                
                # Traitement de la chaise
                if nouvelle_chaise_value and nouvelle_chaise_value != '':
                    chaise_numero = nouvelle_chaise_value.split('_')[1]
                    nouvelle_chaise = Chaise.objects.filter(numero=chaise_numero).first()
                    if nouvelle_chaise:
                        # Vérifier si la chaise est déjà assignée à un autre étudiant
                        if nouvelle_chaise.etudiant_assigne and nouvelle_chaise.etudiant_assigne.id != etudiant.id:
                            messages.error(request, f'La chaise N°{chaise_numero} est déjà assignée à un autre étudiant')
                            return redirect(f'/gerer-etudiants/?niveau={niveau_actuel}&semestre={semestre_actuel}' if niveau_actuel else 'gestion_etudiants')
                        etudiant.chaise_associee = nouvelle_chaise
                    else:
                        messages.error(request, f'La chaise N°{chaise_numero} n\'existe pas')
                        return redirect(f'/gerer-etudiants/?niveau={niveau_actuel}&semestre={semestre_actuel}' if niveau_actuel else 'gestion_etudiants')
                else:
                    etudiant.chaise_associee = None
                
                # Traitement du PC - CORRECTION IMPORTANTE
                if nouveau_pc_value and nouveau_pc_value != '':
                    pc_numero = nouveau_pc_value.split('_')[1]
                    nouveau_pc = Ordinateur.objects.filter(numero=pc_numero).first()
                    if nouveau_pc:
                        # Vérification sécurisée avec hasattr
                        if hasattr(nouveau_pc, 'etudiant_assigne') and nouveau_pc.etudiant_assigne and nouveau_pc.etudiant_assigne.id != etudiant.id:
                            messages.error(request, f'Le PC N°{pc_numero} est déjà assigné à un autre étudiant')
                            return redirect(f'/gerer-etudiants/?niveau={niveau_actuel}&semestre={semestre_actuel}' if niveau_actuel else 'gestion_etudiants')
                        etudiant.pc_associe = nouveau_pc
                    else:
                        messages.error(request, f'Le PC N°{pc_numero} n\'existe pas')
                        return redirect(f'/gerer-etudiants/?niveau={niveau_actuel}&semestre={semestre_actuel}' if niveau_actuel else 'gestion_etudiants')
                else:
                    etudiant.pc_associe = None
                
                if not etudiant.chaise_associee and not etudiant.pc_associe:
                    messages.error(request, 'Un étudiant doit avoir au moins une chaise OU un PC assigné')
                    return redirect(f'/gerer-etudiants/?niveau={niveau_actuel}&semestre={semestre_actuel}' if niveau_actuel else 'gestion_etudiants')
                
                etudiant.matricule = request.POST.get('matricule')
                etudiant.nom = request.POST.get('nom')
                etudiant.prenom = request.POST.get('prenom')
                etudiant.niveau = nouveau_niveau
                etudiant.email = request.POST.get('email', '')
                etudiant.telephone = request.POST.get('telephone', '')
                etudiant.save()
                
                messages.success(request, 'Étudiant modifié avec succès')
                
                if niveau_actuel and nouveau_niveau != niveau_actuel:
                    messages.info(request, f"L'étudiant a été déplacé vers {get_niveau_texte(nouveau_niveau)}")
                    
            except Exception as e:
                messages.error(request, f'Erreur lors de la modification: {str(e)}')
            
            if niveau_actuel:
                return redirect(f'/gerer-etudiants/?niveau={niveau_actuel}&semestre={semestre_actuel}')
            return redirect('gestion_etudiants')
        
        elif action == 'supprimer':
            try:
                etudiant_id = request.POST.get('etudiant_id')
                etudiant = get_object_or_404(Etudiant, id=etudiant_id)
                nom_etudiant = f"{etudiant.nom} {etudiant.prenom}"
                etudiant.delete()
                messages.success(request, f'Étudiant {nom_etudiant} supprimé avec succès')
            except Exception as e:
                messages.error(request, f'Erreur lors de la suppression: {str(e)}')
            
            if niveau_actuel:
                return redirect(f'/gerer-etudiants/?niveau={niveau_actuel}&semestre={semestre_actuel}')
            return redirect('gestion_etudiants')
    
    context = {
        'etudiants': etudiants,
        'total_etudiants': etudiants.count(),
        'chaises_disponibles': chaises_disponibles,
        'pc_disponibles': pc_disponibles,
        'toutes_chaises': toutes_chaises,
        'tous_pc': tous_pc,
        'niveaux': Etudiant.NIVEAU_CHOICES,
        'niveau_actuel': niveau_actuel,
        'semestre_actuel': semestre_actuel,
        'niveau_actuel_texte': get_niveau_texte(niveau_actuel) if niveau_actuel else 'Tous',
        'chaises_numeros_utilises': chaises_numeros_utilises,
        'pc_numeros_utilises': pc_numeros_utilises,
        'numeros_disponibles': numeros_disponibles,
        'chaises_disponibles_select': chaises_disponibles_select,
        'pc_disponibles_select': pc_disponibles_select,
        'toutes_chaises_select': toutes_chaises_select,
        'tous_pc_select': tous_pc_select,
        'chaises_assignees_count': chaises_assignees_count,
        'pc_assigne_count': pc_assigne_count,
    }
    
    return render(request, 'gestion/gestion_etudiants.html', context)

# ========== AJAX ==========

@login_required
@user_passes_test(is_admin)
def get_equipement_info(request):
    equip_type = request.GET.get('type')
    equip_id = request.GET.get('id')
    
    if equip_type == 'chaise':
        try:
            chaise = Chaise.objects.get(id=equip_id)
            data = {
                'code_unique': chaise.code_unique,
                'numero': chaise.numero,
                'etat': chaise.get_etat_display(),
                'description': chaise.description,
                'salle': chaise.salle.nom if chaise.salle else None,
                'photo_url': chaise.photo.url if chaise.photo else None,
                'est_assigne': hasattr(chaise, 'etudiant_assigne') and chaise.etudiant_assigne is not None
            }
            return JsonResponse({'success': True, 'data': data})
        except Chaise.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Chaise non trouvée'})
    
    elif equip_type == 'pc':
        try:
            pc = Ordinateur.objects.get(id=equip_id)
            data = {
                'code_unique': pc.code_unique,
                'numero': pc.numero,
                'etat': pc.get_etat_display(),
                'description': pc.description,
                'salle': pc.salle.nom if pc.salle else None,
                'photo_url': pc.photo.url if pc.photo else None,
                'est_assigne': hasattr(pc, 'etudiant_assigne') and pc.etudiant_assigne is not None
            }
            return JsonResponse({'success': True, 'data': data})
        except Ordinateur.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'PC non trouvé'})
    
    return JsonResponse({'success': False, 'error': 'Type invalide'})