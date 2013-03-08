# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SavedDSGraph'
        db.create_table('graphs_saveddsgraph', (
            ('savedwidget_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['portcullis.SavedWidget'], unique=True, primary_key=True)),
            ('datastream', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['portcullis.DataStream'])),
            ('start', self.gf('django.db.models.fields.IntegerField')()),
            ('end', self.gf('django.db.models.fields.IntegerField')()),
            ('reduction_type', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('granularity', self.gf('django.db.models.fields.IntegerField')()),
            ('zoom_start', self.gf('django.db.models.fields.IntegerField')()),
            ('zoom_end', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('graphs', ['SavedDSGraph'])


    def backwards(self, orm):
        # Deleting model 'SavedDSGraph'
        db.delete_table('graphs_saveddsgraph')


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
        'graphs.saveddsgraph': {
            'Meta': {'object_name': 'SavedDSGraph', '_ormbases': ['portcullis.SavedWidget']},
            'datastream': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['portcullis.DataStream']"}),
            'end': ('django.db.models.fields.IntegerField', [], {}),
            'granularity': ('django.db.models.fields.IntegerField', [], {}),
            'reduction_type': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'savedwidget_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['portcullis.SavedWidget']", 'unique': 'True', 'primary_key': 'True'}),
            'start': ('django.db.models.fields.IntegerField', [], {}),
            'zoom_end': ('django.db.models.fields.IntegerField', [], {}),
            'zoom_start': ('django.db.models.fields.IntegerField', [], {})
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
        'portcullis.savedwidget': {
            'Meta': {'object_name': 'SavedWidget'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'portcullis.scalingfunction': {
            'Meta': {'object_name': 'ScalingFunction'},
            'definition': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'})
        }
    }

    complete_apps = ['graphs']