# Generated by Django 2.2.7 on 2019-12-02 15:04

import django.contrib.postgres.fields
import django.contrib.postgres.operations
from django.db import migrations, models
import django.db.models.deletion
import sorl.thumbnail.fields


class Migration(migrations.Migration):

    replaces = []

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Arc',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mid', models.PositiveIntegerField(unique=True, verbose_name='Metron ID')),
                ('name', models.CharField(blank=True, max_length=200)),
                ('slug', models.SlugField(blank=True, max_length=255)),
                ('desc', models.TextField(blank=True, verbose_name='Description')),
                ('image', sorl.thumbnail.fields.ImageField(blank=True, upload_to='arc/%Y/%m/%d/')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Creator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mid', models.PositiveIntegerField(unique=True, verbose_name='Metron ID')),
                ('name', models.CharField(blank=True, max_length=200)),
                ('slug', models.SlugField(blank=True, max_length=255)),
                ('desc', models.TextField(blank=True, verbose_name='Description')),
                ('wikipedia', models.CharField(blank=True, max_length=255, verbose_name='Wikipedia Slug')),
                ('birth', models.DateField(blank=True, null=True, verbose_name='Date of Birth')),
                ('death', models.DateField(blank=True, null=True, verbose_name='Date of Death')),
                ('image', sorl.thumbnail.fields.ImageField(blank=True, upload_to='creator/%Y/%m/%d/')),
                ('alias', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), blank=True, null=True, size=None)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Credits',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='comics.Creator')),
            ],
            options={
                'verbose_name_plural': 'Credits',
                'ordering': ['creator__name'],
            },
        ),
        migrations.CreateModel(
            name='Publisher',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mid', models.PositiveIntegerField(unique=True, verbose_name='Metron ID')),
                ('name', models.CharField(blank=True, max_length=255)),
                ('slug', models.SlugField(blank=True, max_length=255)),
                ('founded', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Year Founded')),
                ('desc', models.TextField(blank=True, verbose_name='Description')),
                ('wikipedia', models.CharField(blank=True, max_length=255, verbose_name='Wikipedia Slug')),
                ('image', sorl.thumbnail.fields.ImageField(blank=True, upload_to='publisher/%Y/%m/%d/', verbose_name='Logo')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mid', models.PositiveIntegerField(unique=True, verbose_name='Metron ID')),
                ('name', models.CharField(max_length=25)),
                ('notes', models.TextField(blank=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='SeriesType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mid', models.PositiveIntegerField(unique=True, verbose_name='Metron ID')),
                ('name', models.CharField(max_length=255)),
                ('notes', models.TextField(blank=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Series',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mid', models.PositiveIntegerField(unique=True, verbose_name='Metron ID')),
                ('name', models.CharField(blank=True, max_length=255)),
                ('sort_name', models.CharField(blank=True, max_length=255)),
                ('slug', models.SlugField(blank=True, max_length=255)),
                ('volume', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Volume Number')),
                ('year_began', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Year Began')),
                ('year_end', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Year Ended')),
                ('desc', models.TextField(blank=True, verbose_name='Description')),
                ('publisher', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='comics.Publisher')),
                ('series_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='comics.SeriesType')),
            ],
            options={
                'verbose_name_plural': 'Series',
                'ordering': ['sort_name', 'year_began'],
            },
        ),
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mid', models.PositiveIntegerField(unique=True, verbose_name='Metron ID')),
                ('name', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=150, verbose_name='Story Title'), blank=True, null=True, size=None)),
                ('number', models.CharField(max_length=25, verbose_name='Issue Number')),
                ('slug', models.SlugField(max_length=255, unique=True)),
                ('cover_date', models.DateField(verbose_name='Cover Date')),
                ('store_date', models.DateField(blank=True, null=True, verbose_name='In Store Date')),
                ('desc', models.TextField(blank=True, verbose_name='Description')),
                ('image', sorl.thumbnail.fields.ImageField(blank=True, upload_to='issue/%Y/%m/%d/', verbose_name='Cover')),
                ('file', models.CharField(max_length=300, verbose_name='File Path')),
                ('status', models.PositiveSmallIntegerField(blank=True, choices=[(0, 'Unread'), (1, 'Partially Read'), (2, 'Read')], default=0, verbose_name='Status')),
                ('leaf', models.PositiveSmallIntegerField(blank=True, default=0, editable=False)),
                ('page_count', models.PositiveSmallIntegerField(blank=True, default=1, editable=False)),
                ('mod_ts', models.DateTimeField()),
                ('import_date', models.DateTimeField(auto_now_add=True, verbose_name='Date Imported')),
                ('arcs', models.ManyToManyField(blank=True, to='comics.Arc')),
                ('creators', models.ManyToManyField(blank=True, through='comics.Credits', to='comics.Creator')),
                ('series', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='comics.Series')),
            ],
            options={
                'ordering': ['series__sort_name', 'cover_date', 'store_date', 'number'],
                'unique_together': {('series', 'number')},
            },
        ),
        migrations.AddField(
            model_name='credits',
            name='issue',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='comics.Issue'),
        ),
        migrations.AddField(
            model_name='credits',
            name='role',
            field=models.ManyToManyField(to='comics.Role'),
        ),
        migrations.AlterUniqueTogether(
            name='credits',
            unique_together={('issue', 'creator')},
        ),
        django.contrib.postgres.operations.UnaccentExtension(
        ),
        migrations.RemoveField(
            model_name='issue',
            name='import_date',
        ),
        migrations.RemoveField(
            model_name='seriestype',
            name='modified',
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mid', models.PositiveIntegerField(unique=True, verbose_name='Metron ID')),
                ('name', models.CharField(max_length=200)),
                ('slug', models.SlugField(max_length=255, unique=True)),
                ('desc', models.TextField(blank=True, verbose_name='Description')),
                ('wikipedia', models.CharField(blank=True, max_length=255, verbose_name='Wikipedia Slug')),
                ('image', sorl.thumbnail.fields.ImageField(blank=True, upload_to='team/%Y/%m/%d/')),
                ('creators', models.ManyToManyField(blank=True, to='comics.Creator')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Character',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mid', models.PositiveIntegerField(unique=True, verbose_name='Metron ID')),
                ('name', models.CharField(max_length=200)),
                ('slug', models.SlugField(max_length=255, unique=True)),
                ('desc', models.TextField(blank=True, verbose_name='Description')),
                ('wikipedia', models.CharField(blank=True, max_length=255, verbose_name='Wikipedia Slug')),
                ('image', sorl.thumbnail.fields.ImageField(blank=True, upload_to='character/%Y/%m/%d/')),
                ('alias', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), blank=True, null=True, size=None)),
                ('creators', models.ManyToManyField(blank=True, to='comics.Creator')),
                ('teams', models.ManyToManyField(blank=True, to='comics.Team')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
    ]