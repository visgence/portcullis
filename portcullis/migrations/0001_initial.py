# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'PortcullisUser'
        db.create_table('portcullis_portcullisuser', (
            ('user_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('portcullis', ['PortcullisUser'])

        # Adding model 'ScalingFunction'
        db.create_table('portcullis_scalingfunction', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=32)),
            ('definition', self.gf('django.db.models.fields.CharField')(max_length=1000)),
        ))
        db.send_create_signal('portcullis', ['ScalingFunction'])

        # Adding model 'Key'
        db.create_table('portcullis_key', (
            ('key', self.gf('django.db.models.fields.CharField')(max_length=1024, primary_key=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['portcullis.PortcullisUser'])),
            ('expiration', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('num_uses', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('portcullis', ['Key'])

        # Adding model 'Device'
        db.create_table('portcullis_device', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('ip_address', self.gf('django.db.models.fields.IPAddressField')(max_length=15, blank=True)),
            ('key', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['portcullis.Key'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['portcullis.PortcullisUser'])),
        ))
        db.send_create_signal('portcullis', ['Device'])

        # Adding unique constraint on 'Device', fields ['name', 'owner']
        db.create_unique('portcullis_device', ['name', 'owner_id'])

        # Adding model 'DataStream'
        db.create_table('portcullis_datastream', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('node_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('port_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('units', self.gf('django.db.models.fields.CharField')(max_length=32, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
            ('color', self.gf('django.db.models.fields.CharField')(max_length=32, blank=True)),
            ('min_value', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=20, decimal_places=6, blank=True)),
            ('max_value', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=20, decimal_places=6, blank=True)),
            ('scaling_function', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['portcullis.ScalingFunction'])),
            ('reduction_type', self.gf('django.db.models.fields.CharField')(default='mean', max_length=32)),
            ('is_public', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['portcullis.PortcullisUser'])),
        ))
        db.send_create_signal('portcullis', ['DataStream'])

        # Adding unique constraint on 'DataStream', fields ['owner', 'name']
        db.create_unique('portcullis_datastream', ['owner_id', 'name'])

        # Adding M2M table for field can_read on 'DataStream'
        db.create_table('portcullis_datastream_can_read', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('datastream', models.ForeignKey(orm['portcullis.datastream'], null=False)),
            ('key', models.ForeignKey(orm['portcullis.key'], null=False))
        ))
        db.create_unique('portcullis_datastream_can_read', ['datastream_id', 'key_id'])

        # Adding M2M table for field can_post on 'DataStream'
        db.create_table('portcullis_datastream_can_post', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('datastream', models.ForeignKey(orm['portcullis.datastream'], null=False)),
            ('key', models.ForeignKey(orm['portcullis.key'], null=False))
        ))
        db.create_unique('portcullis_datastream_can_post', ['datastream_id', 'key_id'])

        # Adding model 'SensorReading'
        db.create_table('portcullis_sensorreading', (
            ('id', self.gf('django.db.models.fields.CharField')(max_length=32, primary_key=True)),
            ('datastream', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['portcullis.DataStream'])),
            ('value', self.gf('django.db.models.fields.DecimalField')(max_digits=20, decimal_places=6)),
            ('timestamp', self.gf('django.db.models.fields.IntegerField')(db_index=True)),
        ))
        db.send_create_signal('portcullis', ['SensorReading'])

        # Adding unique constraint on 'SensorReading', fields ['datastream', 'timestamp']
        db.create_unique('portcullis_sensorreading', ['datastream_id', 'timestamp'])

        # Adding model 'SavedWidget'
        db.create_table('portcullis_savedwidget', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('portcullis', ['SavedWidget'])

        # Adding model 'SavedView'
        db.create_table('portcullis_savedview', (
            ('key', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['portcullis.Key'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('portcullis', ['SavedView'])

        # Adding M2M table for field widget on 'SavedView'
        db.create_table('portcullis_savedview_widget', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('savedview', models.ForeignKey(orm['portcullis.savedview'], null=False)),
            ('savedwidget', models.ForeignKey(orm['portcullis.savedwidget'], null=False))
        ))
        db.create_unique('portcullis_savedview_widget', ['savedview_id', 'savedwidget_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'SensorReading', fields ['datastream', 'timestamp']
        db.delete_unique('portcullis_sensorreading', ['datastream_id', 'timestamp'])

        # Removing unique constraint on 'DataStream', fields ['owner', 'name']
        db.delete_unique('portcullis_datastream', ['owner_id', 'name'])

        # Removing unique constraint on 'Device', fields ['name', 'owner']
        db.delete_unique('portcullis_device', ['name', 'owner_id'])

        # Deleting model 'PortcullisUser'
        db.delete_table('portcullis_portcullisuser')

        # Deleting model 'ScalingFunction'
        db.delete_table('portcullis_scalingfunction')

        # Deleting model 'Key'
        db.delete_table('portcullis_key')

        # Deleting model 'Device'
        db.delete_table('portcullis_device')

        # Deleting model 'DataStream'
        db.delete_table('portcullis_datastream')

        # Removing M2M table for field can_read on 'DataStream'
        db.delete_table('portcullis_datastream_can_read')

        # Removing M2M table for field can_post on 'DataStream'
        db.delete_table('portcullis_datastream_can_post')

        # Deleting model 'SensorReading'
        db.delete_table('portcullis_sensorreading')

        # Deleting model 'SavedWidget'
        db.delete_table('portcullis_savedwidget')

        # Deleting model 'SavedView'
        db.delete_table('portcullis_savedview')

        # Removing M2M table for field widget on 'SavedView'
        db.delete_table('portcullis_savedview_widget')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'portcullis.datastream': {
            'Meta': {'ordering': "['node_id', 'port_id', 'id']", 'unique_together': "(('owner', 'name'),)", 'object_name': 'DataStream'},
            'can_post': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'can_write_set'", 'blank': 'True', 'to': "orm['portcullis.Key']"}),
            'can_read': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'can_read_set'", 'blank': 'True', 'to': "orm['portcullis.Key']"}),
            'color': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'max_value': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '20', 'decimal_places': '6', 'blank': 'True'}),
            'min_value': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '20', 'decimal_places': '6', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'node_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['portcullis.PortcullisUser']"}),
            'port_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'reduction_type': ('django.db.models.fields.CharField', [], {'default': "'mean'", 'max_length': '32'}),
            'scaling_function': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['portcullis.ScalingFunction']"}),
            'units': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'})
        },
        'portcullis.device': {
            'Meta': {'unique_together': "(('name', 'owner'),)", 'object_name': 'Device'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'blank': 'True'}),
            'key': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['portcullis.Key']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['portcullis.PortcullisUser']"})
        },
        'portcullis.key': {
            'Meta': {'object_name': 'Key'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'expiration': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'primary_key': 'True'}),
            'num_uses': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['portcullis.PortcullisUser']"})
        },
        'portcullis.portcullisuser': {
            'Meta': {'object_name': 'PortcullisUser', '_ormbases': ['auth.User']},
            'user_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'primary_key': 'True'})
        },
        'portcullis.savedview': {
            'Meta': {'object_name': 'SavedView'},
            'key': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['portcullis.Key']", 'unique': 'True', 'primary_key': 'True'}),
            'widget': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['portcullis.SavedWidget']", 'symmetrical': 'False'})
        },
        'portcullis.savedwidget': {
            'Meta': {'object_name': 'SavedWidget'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'portcullis.scalingfunction': {
            'Meta': {'object_name': 'ScalingFunction'},
            'definition': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'})
        },
        'portcullis.sensorreading': {
            'Meta': {'unique_together': "(('datastream', 'timestamp'),)", 'object_name': 'SensorReading'},
            'datastream': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['portcullis.DataStream']"}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '32', 'primary_key': 'True'}),
            'timestamp': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'value': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '6'})
        }
    }

    complete_apps = ['portcullis']