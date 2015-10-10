#db.py
# -*- coding: utf-8 -*-

__author__ = 'Michael Liao'

'''
Database operation module.
'''

import time,uuid,functools, threading, logging

#Dict object

class Dict(dict):
	'''
	simple dict but support access as x.y style.

	>>> d1 = Dict()
	>>> d1['x'] = 100
	>>> d1.x
	'''
	def __init__(self, names = (), values = (), ** kw):
		super(Dict, self).__init__(**kw)
		for k, v in zip(names, values):
			self[k] = v

	def __getattr__(self, key):
		try:
			return self[key]
		except KeyError:
			raise AttributeError(r"'Dict' object has no attribute '%s'" % key)

	def __setattr__(self, key, value):
		self[key] = value

def next_id(t = None):
	'''
	Return next id as 50-char string.
	'''
	if t is None:
		t = time.time()
	return '%015d%s000' % (int(t * 1000), uuid.uuid4().hex)

def _profiling(start, sql= ''):
	t = time.time() - start
	if t > 0.1:
		logging.warning('[PROFILING] [DB]' % (t, sql))
	else:
		logging.info('[PROFILING] [DB]' % (t, sql))

class  DBError(Exception):
	pass

class MulticolumnsError(DBError):
	pass

class _LasyConnection(object):

	def __init__(self):
		self.connection = None

	def cursor(self):
		if self.connection is None:
			connection = engine.connect()
			logging.info('open connection <%s>...' % hex(id(connection)))
			self.connection = connection
		return self.connection.cursor()

	def commit(self):
		self.connection.commit()

	def rollback(self):
		self.connection.rollback()

	def cleanup(self):
		if self.connection:
			connection = self.connection
			self.connection = None
			logging.info('close connection <%s>...' % hex(id(connection)))
			connection.close()


#databse engine
class _Engine(object):
	def __init__(self, connect):
		self._connect = connect
	def connect(self):
		return self._connect()

engine = None

#数据库连接的上下文对象
class _DbCtx(theading.local):
	def __init__(self):
		self.connection = None
		self.transactions = 0

	def is_init(self):
		return not self.connection is None

	def init(self):
		self.connection = _LasyConnection()
		self.transaction = 0

	def cleanup(self):
		self.connection.cleanup()
		self.connection = None

	def cursor(self):
		return self.connection.cursor()

_db_ctx = _DbCtx()

class _ConnectionCtx(object):
	def __enter__(self):
		global _db_ctx
		self.should_cleanup = False
		if not _db_ctx.is_init():
			_db_ctx.init()
			self.should_cleanup = True
		return self

	def __exit__(self, exctype, excvalue,traceback):
		global _db_ctx
		if self.should_cleanup:
			_db_ctx.cleanup()

def connection():
	return _ConnectionCtx()

@with_connection
def select(sql, *args):
	pass

@with_connection
def update(sql, *args):
	pass

class _TransactionCtx(object):
	def __enter__(self):
		global _db_ctx
		self.should_close_conn = False
		if not _db_ctx.is_init():
			_db_ctx.init()
			self.should_close_conn = True
		_db_ctx.transactions = _db_ctx.transactions + 1
		return self

	def __exit__(self, exctype, exctype, traceback):
		global _db_ctx
		_db_ctx.transactions = _db_ctx.transactions - 1
		try:
			if _db_ctx.transactions == 0:
				if exctype is None:
					self.commit()
				else:
					self.rollback()
		finally:
			if self.should_close_conn:
				_db_ctx.cleanup()

	def commit(self):
		global _db_ctx
		try:
			_db_ctx.connection.commit()
		except:
			_db_ctx.connection.rollback()
			raise

	def rollback(self):
		global _db_ctx
		_db_ctx.connection.rollback()