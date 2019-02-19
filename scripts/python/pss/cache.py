import os
import sys

from tools import clean_pubkey, clean_overlay
from user import PssContact

CACHE_CONTACT_STOREFILE = ".pss-contacts"

class Cache:
	
	def __init__(self, path=".", queuelength=10):
		self.bzzs = {}
		self.psses = {}
		self.selfs = {}	

		self.contacts = []
		self.idx_pubkey_nick = {}
		self.idx_nick_pubkey = {}

		self.feeds = {}

		# index nicks to chat rooms
		self.rooms = {}
		self.idx_room_nicks = {}
		self.idx_nick_rooms = {}

		# verify path and handle trailing slash
		self.path = path
		self.file = None

	
	def add_node(self, pssobj, name):
		if name in self.psses.keys():
			raise AttributeError("pss key " + str(name) + " already in use")

		self.psses[name] = pssobj
		return True


	def add_bzz(self, bzzobj, name):
		if name in self.bzzs.keys():
			raise AttributeError("bzz key " + str(name) + " already in use")

		self.bzzs[name] = bzzobj
		return True


	
	def add_contact(self, name, contact):

		if name in self.idx_nick_pubkey.keys():
			raise KeyError("contact name '" + str(name) + "' already in use")

		if contact.get_public_key() == "":
			raise AttributeError("public key missing from contact")

		# take over the reference of contact, caller can drop var
		self.contacts.append(contact)
		self.idx_pubkey_nick[contact.get_public_key()] = name
		self.idx_nick_pubkey[name] = contact.get_public_key()
		return True


	def remove_contact(self):
		pass



	def get_active_bzz(self):
		if (len(self.bzzs) == 0):
			return None

		return self.bzzs[0]



	def have_node_name(self, name):
		return name in self.psses

	

	def get_node_by_name(self, name):
		return (self.psses[name], self.get_active_bzz())

	
	
	def get_contact_by_nick(self, name):
		contact = self.ids_nick_pubkey[name]
		if contact == None:
			raise AttributeError("no cached contact with name '" + str(name) + "'")
		return publickey



	def get_contact_by_public_key(self, publickey):
		contact = self.ids_pubkey_nick[publickey]
		if contact == None:
			raise AttributeError("no cached contact with public key'" + str(name) + "'")
		return contact



	def get_store_path(self):
		return self.path + "/" + CACHE_CONTACT_STOREFILE



	def load_store(self):

		entrycount = 0
		okcount = 0

		f = open(self.get_store_path(), "r", 0600)

		while 1:
			# if there is a record
			# split fields on tab and chop newline
			record = f.readline()
			if len(record) == 0:
				break	


			# add it to the map and report
			entrycount += 1
			try: 
				(nick, pubkeyhx, overlayhx, srckeyhx) = record.split("\t")
				if ord(srckeyhx[len(srckeyhx)-1]) == 0x0a:
					srckeyhx = srckeyhx[:len(srckeyhx)-1]
				pubkey = clean_pubkey(pubkeyhx)
				contact = PssContact(nick, srckeyhx)
				contact.set_public_key(pubkeyhx.decode("hex"))
				contact.set_overlay(clean_overlay(overlayhx).decode("hex"))

			# \todo delete the record from the contact store
			except Exception as e:
				pass

			try:
				self.add_contact(nick, contact)
				okcount += 1
			except Exception as e:
				sys.stderr.write("fail on " + str(nick) + ": " + repr(e) + "\n")

		f.close()

		# \todo dump valid entries to new file and copy over old
		self.file = open(self.get_store_path(), "a", 0600)
		return (entrycount, okcount)


	def close_node(self, name):
		self.psses[name].close()
		if (self.bzzs[name] != self.get_active_bzz()):
			self.bzzs[name].close()


	def close(self):

		for p in self.psses.values():
			p.close()

		for b in self.bzzs.values():
			b.close()

		self.file.close()
