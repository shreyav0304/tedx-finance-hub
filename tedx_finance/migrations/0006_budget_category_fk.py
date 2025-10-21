from django.db import migrations, models
import django.db.models.deletion


def forwards(apps, schema_editor):
    Budget = apps.get_model('tedx_finance', 'Budget')
    Category = apps.get_model('tedx_finance', 'Category')
    db_alias = schema_editor.connection.alias
    # Populate the new FK field by matching/creating Category by name from old char field
    for budget in Budget.objects.using(db_alias).all():
        # Old field was 'category' (char); during migration it's accessible via _category_old if we rename, but we used add field
        # So read from the historical field value stored on the model before removal via a temporary attribute
        # We'll assume a temporary field 'category_old' exists per operations below
        old_name = getattr(budget, 'category_old', None) or getattr(budget, 'category', None)
        if old_name:
            cat, _ = Category.objects.using(db_alias).get_or_create(name=old_name)
            setattr(budget, 'category_new', cat)
            budget.save()


def reverse(apps, schema_editor):
    Budget = apps.get_model('tedx_finance', 'Budget')
    db_alias = schema_editor.connection.alias
    # If reversing, copy FK name back to char field if present
    for budget in Budget.objects.using(db_alias).all():
        if getattr(budget, 'category_new_id', None):
            if budget.category_new:
                budget.category_old = budget.category_new.name
                budget.save()


class Migration(migrations.Migration):

    dependencies = [
        ('tedx_finance', '0005_category'),
    ]

    operations = [
        # 1) Add a temporary char field copy to hold old values (if not already exists)
        migrations.AddField(
            model_name='budget',
            name='category_old',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        # 2) Copy data from old 'category' into 'category_old'
        migrations.RunSQL(
            sql=("UPDATE tedx_finance_budget SET category_old = category"),
            reverse_sql=("UPDATE tedx_finance_budget SET category_old = NULL"),
        ),
        # 3) Add the new FK field nullable for backfill
        migrations.AddField(
            model_name='budget',
            name='category_new',
            field=models.ForeignKey(null=True, blank=True, to='tedx_finance.category', on_delete=django.db.models.deletion.CASCADE, unique=True),
        ),
        # 4) Backfill category_new from category_old, creating Category rows as needed
        migrations.RunPython(forwards, reverse),
        # 5) Drop the original 'category' field
        migrations.RemoveField(
            model_name='budget',
            name='category',
        ),
        # 6) Rename fields: category_new -> category
        migrations.RenameField(
            model_name='budget',
            old_name='category_new',
            new_name='category',
        ),
        # 7) Drop the temporary category_old field
        migrations.RemoveField(
            model_name='budget',
            name='category_old',
        ),
    ]
