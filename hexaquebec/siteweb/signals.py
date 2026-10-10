from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import (
    Stagiaires,
    Messages,
    Reunion,
    Notification,
)


@receiver(
    post_save,
    sender=Messages,
    dispatch_uid="hq_espace_notification_message",
)
def notification_message(
    sender,
    instance,
    created,
    **kwargs,
):
    if not created:
        return

    if instance.auteur_id == instance.stagiaire.utilisateur_id:
        destinataires = list(
            get_user_model()
            .objects.filter(
                is_active=True,
                is_staff=True,
            )
            .values_list("pk", flat=True)
        )

        texte = (
            "Nouveau message du stagiaire "
            f"{instance.stagiaire.code}."
        )

    else:
        destinataires = [
            instance.stagiaire.utilisateur_id,
        ]

        texte = (
            "Vous avez reçu un message "
            "de l’administration HexaQuébec."
        )

    transaction.on_commit(
        lambda: Notification.objects.bulk_create([
            Notification(
                utilisateur_id=identifiant,
                texte=texte,
            )
            for identifiant in destinataires
        ])
    )


@receiver(
    post_save,
    sender=Reunion,
    dispatch_uid="hq_espace_notification_reunion",
)
def notification_reunion(
    sender,
    instance,
    created,
    **kwargs,
):
    profils = Stagiaires.objects.filter(
        actif=True,
        utilisateur__is_active=True,
    )

    if instance.domaine:
        profils = profils.filter(
            domaine=instance.domaine,
        )

    destinataires = list(
        profils.values_list(
            "utilisateur_id",
            flat=True,
        )
    )

    if instance.annulee:
        action = "annulé"
    elif created:
        action = "créé"
    else:
        action = "modifié"

    texte = (
        f"Événement {action} : {instance.titre}"
    )[:250]

    transaction.on_commit(
        lambda: Notification.objects.bulk_create([
            Notification(
                utilisateur_id=identifiant,
                texte=texte,
            )
            for identifiant in destinataires
        ])
    )