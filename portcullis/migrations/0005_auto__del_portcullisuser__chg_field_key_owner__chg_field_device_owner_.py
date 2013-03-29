# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'PortcullisUser'
        db.delete_table(u'portcullis_portcullisuser')


        # Changing field 'Key.owner'
        db.alter_column(u'portcullis_key', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['portcullis.PortcullisUser1']))

        # Changing field 'Device.owner'
        db.alter_column(u'portcullis_device', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['portcullis.PortcullisUser1']))

        # Changing field 'DataStream.owner'
        db.alter_column(u'portcullis_datastream', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['portcullis.PortcullisUser1']))

    def backwards(self, orm):
        # Adding model 'PortcullisUser'
        db.create_table(u'portcullis_portcullisuser', (
            (u'user_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True, primary_key=True)),
        ))
        db.send_create_signal(u'portcullis', ['PortcullisUser'])


        # Changing field 'Key.owner'
        db.alter_column(u'portcullis_key', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['portcullis.PortcullisUser']))

        # Changing field 'Device.owner'
        db.alter_column(u'portcullis_device', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['portcullis.PortcullisUser']))

        # Changing field 'DataStream.owner'
        db.alter_column(u'portcullis_datastream', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['portcullis.PortcullisUser']))

    models = {
        u'portcullis.datastream': {
            'Meta': {'ordering': "['id']", 'unique_together': "(('owner', 'name'),)", 'object_name': 'DataStream'},
            'can_post': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'can_write_set'", 'blank': 'True', 'to': u"orm['portcullis.Key']"}),
            'can_read': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'can_read_set'", 'blank': 'True', 'to': u"orm['portcullis.Key']"}),
            'color': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'max_value': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '20', 'decimal_places': '6', 'blank': 'True'}),
            'min_value': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '20', 'decimal_places': '6', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['portcullis.PortcullisUser1']"}),
            'reduction_type': ('django.db.models.fields.CharField', [], {'default': "'mean'", 'max_length': '32'}),
            'scaling_function': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['portcullis.ScalingFunction']"}),
            'units': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'})
        },
        u'portcullis.device': {
            'Meta': {'unique_together': "(('name', 'owner'),)", 'object_name': 'Device'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'blank': 'True'}),
            'key': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['portcullis.Key']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['portcullis.PortcullisUser1']"})
        },
        u'portcullis.key': {
            'Meta': {'object_name': 'Key'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'expiration': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'primary_key': 'True'}),
            'num_uses': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['portcullis.PortcullisUser1']"})
        },
        u'portcullis.portcullisuser1': {
            'Meta': {'object_name': 'PortcullisUser1'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 3, 28, 0, 0)'}),
            'email': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128', 'db_index': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'portcullis.savedview': {
            'Meta': {'object_name': 'SavedView'},
            'key': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['portcullis.Key']", 'unique': 'True', 'primary_key': 'True'}),
            'widget': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['portcullis.SavedWidget']", 'symmetrical': 'False'})
        },
        u'portcullis.savedwidget': {
            'Meta': {'object_name': 'SavedWidget'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'portcullis.scalingfunction': {
            'Meta': {'object_name': 'ScalingFunction'},
            'definition': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'})
        },
        u'portcullis.sensorreading': {
            'Meta': {'unique_together': "(('datastream', 'timestamp'),)", 'object_name': 'SensorReading'},
            'datastream': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['portcullis.DataStream']"}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '32', 'primary_key': 'True'}),
            'timestamp': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'value': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '6'})
        }
    }

    complete_apps = ['portcullis']