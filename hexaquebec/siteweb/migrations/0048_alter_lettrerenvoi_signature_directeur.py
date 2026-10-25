import json

from django.db import migrations, models


def convertir_signatures(apps, schema_editor):
    LettreRenvoi = apps.get_model("siteweb", "LettreRenvoi")

    database = schema_editor.connection.alias

    for lettre in LettreRenvoi.objects.using(database).all().iterator():

        ancienne_signature = lettre.signature_directeur

        if not ancienne_signature:
            # Une signature vide devient une liste JSON valide.
            nouvelle_valeur = "[]"

        else:
            try:
                valeur = json.loads(ancienne_signature)

                if isinstance(valeur, list):
                    nouvelle_valeur = ancienne_signature
                else:
                    # Préserver les données existantes.
                    nouvelle_valeur = json.dumps(
                        ancienne_signature
                    )

            except (json.JSONDecodeError, TypeError):
                # Préserver une éventuelle ancienne signature PNG.
                nouvelle_valeur = json.dumps(
                    ancienne_signature
                )

        LettreRenvoi.objects.using(database).filter(
            pk=lettre.pk
        ).update(
            signature_directeur=nouvelle_valeur
        )


class Migration(migrations.Migration):

    dependencies = [
        ("siteweb", "0047_lettrerenvoi_signature_directeur_and_more"),
    ]

    operations = [

        migrations.RunPython(
            convertir_signatures,
            migrations.RunPython.noop
        ),

        migrations.AlterField(
            model_name="lettrerenvoi",
            name="signature_directeur",
            field=models.JSONField(
                default=list,
                blank=True
            ),
        ),

    ]