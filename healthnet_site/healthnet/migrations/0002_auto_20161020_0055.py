# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-10-20 00:55
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('healthnet', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('timestamp', models.DateTimeField()),
                ('unread', models.BooleanField()),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipient', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sender', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='administrator',
            name='hospital',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='healthnet.Hospital'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='appointment',
            name='location',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='healthnet.Hospital'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='doctor',
            name='hospital',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='healthnet.Hospital'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='hospital',
            name='location',
            field=models.CharField(default='', max_length=30),
        ),
        migrations.AddField(
            model_name='hospital',
            name='name',
            field=models.CharField(default='', max_length=30),
        ),
        migrations.AddField(
            model_name='logitem',
            name='user_type1',
            field=models.CharField(default='', max_length=20),
        ),
        migrations.AddField(
            model_name='logitem',
            name='user_type2',
            field=models.CharField(default='', max_length=20),
        ),
        migrations.AddField(
            model_name='nurse',
            name='hospital',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='healthnet.Hospital'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='patient',
            name='address',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='patient',
            name='age',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='patient',
            name='height',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='patient',
            name='hospital',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='healthnet.Hospital'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='patient',
            name='insurance_company',
            field=models.CharField(default='', max_length=30),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='patient',
            name='insurance_id',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='patient',
            name='weight',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='prescription',
            name='doctor',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='doctor', to='healthnet.Doctor'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='prescription',
            name='dosage',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='prescription',
            name='medication',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='prescription',
            name='patient',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='patient', to='healthnet.Patient'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='testresult',
            name='comments',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='testresult',
            name='name',
            field=models.CharField(default=None, max_length=30),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='testresult',
            name='patient',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='healthnet.Patient'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='testresult',
            name='released',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='testresult',
            name='results',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]