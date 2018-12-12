class Stream:
	buf = ""
	depth = 0

	def process(self, data):
		"""  process stream of json and connect/disconnect indicators, keeping state between calls
		returns a dict, where the members mean:
		* processing: if the data stopped in the middle of a json object
		* results: all json objects completed in this call
		* status: if false, connection status is down
		"""

		n = 0
		r = {
			"processing": False,
			"results": [],
			"status": True
		}

		try:
			n = len(data)
		except:
			return 			

		last = 0
		for i in range(0, n):
			if ord(data[i]) == 0x03:
				r['status'] = False
				self.buf = ""
				self.depth = 0
				continue
			elif ord(data[i]) == 0x02:
				r['status'] = True
				continue
			self.buf += data[i]

			if ord(data[i]) == 0x7b:
				self.depth += 1
			elif ord(data[i]) == 0x7d:
				self.depth -= 1
				if self.depth == 0:
					r['results'].append(self.buf)
					self.buf = ""
					last = i
			
		if self.depth > 0:
			r['processing'] = True

		return r
