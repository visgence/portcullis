# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models, DatabaseError


class Migration(SchemaMigration):

    def forwards(self, orm):
        try:
            # Delete auth User Table, but might not have ever existed.
            db.delete_table(u'auth_user_groups')
            db.delete_table(u'auth_user_user_permissions')
            db.delete_table(u'auth_user')
        except DatabaseError:
            pass

    def backwards(self, orm):
        #  Create auth User table
        print "Adding auth_user tables"
        db.create_table(u'auth_user', (
                (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
                ('username', self.gf('django.db.models.fields.CharField')(max_length=30, unique=True)),
                ('password', self.gf('django.db.models.fields.CharField')(max_length=128)),
                ('last_login', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now())),
                ('email', self.gf('django.db.models.fields.CharField')(max_length=75, blank=True)),
                ('first_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
                ('last_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
                ('is_superuser', self.gf('django.db.models.fields.BooleanField')(default=False)),
                ('is_staff', self.gf('django.db.models.fields.BooleanField')(default=False)),
                ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
                ('date_joined', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now()))
                ))
        print "Sending create signal"
        db.send_create_signal(u'auth', ['User'])
        print "Remvoing user_groups"
        print orm[u'auth.group']
        print orm[u'auth.user']
        db.create_table(u'auth_user_groups', (
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
                ('user', models.ForeignKey(orm[u'auth.user'], null=False)),
                ('group', models.ForeignKey(orm[u'auth.group'], null=False)),
                ))
        print 'Before unique'
        db.create_unique(u'auth_user_groups', ['user_id', 'group_id'])
        print "removing user_user_permisssions"
        db.create_table(u'auth_user_user_permissions', (
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
                ('user', models.ForeignKey(orm[u'auth.user'], null=False)),
                ('permission', models.ForeignKey(orm[u'auth.permission'], null=False))
                ))
        db.create_unique(u'auth_user_user_permissions', ['user_id', 'permission_id'])

    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
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
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['portcullis.PortcullisUser']"}),
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
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['portcullis.PortcullisUser']"})
        },
        u'portcullis.key': {
            'Meta': {'object_name': 'Key'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'expiration': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'primary_key': 'True'}),
            'num_uses': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['portcullis.PortcullisUser']"})
        },
        u'portcullis.portcullisuser': {
            'Meta': {'object_name': 'PortcullisUser'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 4, 2, 0, 0)'}),
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

    complete_apps = ['auth', 'portcullis']
