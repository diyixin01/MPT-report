import random
import unittest
import MerklePatriciaTrie as MPT
import time
from hashlib import sha256
import string
import plyvel
import pickle
class TestingClass(unittest.TestCase):

	def __init__(self, *args, **kwargs):
		super(TestingClass, self).__init__(*args, **kwargs)
		testdb = plyvel.DB("test", create_if_missing = True)
		self.test = MPT.MerklePatriciaTrie(testdb,"")
		self.db = plyvel.DB("rootDB", create_if_missing = True)
	def test_all(self):
		
		start = time.time()
		values = ["liujinyuan", "202000460082", "cccccccc", "dddddddd", "eeeeeeee"]
		keys = ["h7766", "h7777", "hoios", "h7234", "hnvuw"]
		for j in range(5):
			#s = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(5))
			
			#val = ''.join(random.choice(string.digits) for _ in range(8))
			#key = sha256(s.encode('utf-8')).hexdigest()
			#key = s[j]
			#keys.append(key)
			#values.append(val)
			self.test.update(keys[j], values[j])
			#print("Insert {} datas with time {}".format((j+1)*250000,time.time()))
			for i in range(25):
				s = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(5))
				val = ''.join(random.choice(string.digits) for _ in range(8))
				key = sha256(s.encode('utf-8')).hexdigest()
				self.test.update(key, val)
		end = time.time()
		print("Insert time:", end-start)
		print(self.test.id)
		"""
		for i in range(10):
			start = time.time()
			self.assertEqual(self.test.search(keys[i]), values[i])
			end = time.time()
			print("Search time:", end-start)
		
	#def test_delete_all(self):


if __name__ == '__main__':
	unittest.main()
