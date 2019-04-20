#!/usr/bin/python3

import unittest
import time
import api
import socket
import select
import struct
from pss import decodehex

privkey = "2ea3f401733d3ecc1e18b305245adc98f3ffc4c6e46bf42f37001fb18b5a70ac"
pubkey = "04b72985aa2104e41c1a2d40340c2b71a8d641bb6ac0f9fd7dc2dbbd48c0eaf172baa41456d252532db97704ea4949e1f42f66fd57de00f8f1f4514a2889f42df6"

class TestServer(unittest.TestCase):


	def setUp(self):
		self.obj = api.ApiServer("foo")
		self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
		self.fileno = self.sock.fileno()
		time.sleep(1.0)


	def tearDown(self):
		self.sock.close()
		self.obj.stop()


	def test_contact_single(self):
		self.obj.connect(self.sock)
		print("sending on addr:{} sock:{}\n".format(self.obj.sockaddr, self.sock))

		# basic check for echo
		select.select([], [self.fileno], [])
		datasend = b"\x00\x08\x01"
		bytedata = decodehex(pubkey)
		bytedata += b'\x04\x01\x02\x03\x04inky'
		(datalengthserialized) = struct.pack(">I", len(bytedata))
		datasend += datalengthserialized
		datasend += bytedata
		dataexpect = b"\x20\x08\x01\x00\x00\x00\x00"
		self.sock.send(datasend)
		select.select([self.fileno], [], [])
		datarecv = self.sock.recv(1024)
		self.assertEqual(dataexpect, datarecv)
		self.assertEqual(0x20, datarecv[0] & 0xe0)

		# check that the error (erroneously) sent does not come back
		select.select([], [self.fileno], [])
		datasend = b"\x00\x01\x00\x00\x00\x00\x20"
		datasend += decodehex(privkey)
		dataexpect = b"\x20\x01\x00\x00\x00\x00\x00"
		self.sock.send(datasend)
		select.select([self.fileno], [], [])
		datarecv = self.sock.recv(1024)
		self.assertEqual(dataexpect, datarecv)

#		# check correct treatment of high order byte in id
#		select.select([], [self.fileno], [])
#		datasend = b"\x10\x01\x88\x00\x00\x00\x05\x78\x79\x7a\x7a\x79"
#		self.sock.send(datasend)
#		select.select([self.fileno], [], [])
#		datarecv = self.sock.recv(1024)
#		self.assertEqual(datasend[1:], datarecv[1:])
#		self.assertEqual(datasend[0], datarecv[0] & 0x1f)
#		self.assertEqual(0x20, datarecv[0] & 0xe0)

		time.sleep(1.0)


if __name__ == "__main__":
	unittest.main()
