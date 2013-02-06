# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Trade'
        db.create_table('trades_trade', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('account', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('symbol', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('quantity', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('price', self.gf('django.db.models.fields.FloatField')(default=0.0)),
            ('broker', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('tradeDate', self.gf('django.db.models.fields.DateTimeField')()),
            ('exchange', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
        ))
        db.send_create_signal('trades', ['Trade'])


    def backwards(self, orm):
        # Deleting model 'Trade'
        db.delete_table('trades_trade')


    models = {
        'trades.trade': {
            'Meta': {'object_name': 'Trade'},
            'account': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'broker': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'exchange': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'price': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'quantity': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'symbol': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'tradeDate': ('django.db.models.fields.DateTimeField', [], {})
        }
    }

    complete_apps = ['trades']