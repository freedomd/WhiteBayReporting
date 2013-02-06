# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Trade.tradeDate'
        db.add_column('trades_trade', 'tradeDate',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 2, 5, 0, 0)),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Trade.tradeDate'
        db.delete_column('trades_trade', 'tradeDate')


    models = {
        'trades.trade': {
            'Meta': {'object_name': 'Trade'},
            'account': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'broker': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'exchange': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'executionId': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'price': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'quantity': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'side': ('django.db.models.fields.CharField', [], {'default': "'SEL'", 'max_length': '5'}),
            'symbol': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'tradeDate': ('django.db.models.fields.DateTimeField', [], {})
        }
    }

    complete_apps = ['trades']