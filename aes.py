from __future__ import division
import random, string
from Crypto.Cipher import AES
import base64
import os
import math

# Generate random string for testing
def randomword(length):
	return ''.join(random.choice(string.lowercase+string.digits) for i in range(length))

# AES encrytion (The input string size is always 63, so there is only one padding)
def aes_encrypt(string, key, padding, block_size):
	# one-liner to sufficiently pad the text to be encrypted
	pad = lambda s: s + (block_size - len(s) % block_size) * padding
	# one-liners to encrypt/encode and decrypt/decode a string
	# encrypt with AES, encode with base64
	EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
	# create a cipher object using the random secret
	cipher = AES.new(key)
	# encode a string
	encoded = EncodeAES(cipher, string)
	return encoded

# AES decryption
def aes_decrypt(string, key, padding, block_size):
	DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(padding)
	#DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e))[:-1]
	# create a cipher object using the random secret
	cipher = AES.new(key)
	decoded = DecodeAES(cipher, string)
	return decoded

# AES generate shared key and store it in a file
def aes_gen_key(block_size, key_file):
	key = os.urandom(block_size)
	f = open(key_file, 'w')
	f.write(key)
	f.close()
	return key

# AES read shared key from file
def aes_read_key(block_size, key_file):
	f = open(key_file)
	key = f.readlines()[0]
	f.close()
	return key

# Parse the data stream in the format data_size + data
def parse_output(input_str):
	output = []
	left = input_str
	size = 0
	while size < len(left):
		size = int(left[:5])
		if size + 5 <= len(left):
			left = left[5:]
			output.append(left[:size])
			left = left[size:]
		else:
			break
	return output,left

if __name__ == '__main__':
	# AES Parameters
	block_size =  16
	padding = '{'
	#input_str = randomword(63)
	input_str = '00058bate4vmyuvq2lkx8q2qficjif3sc13872c5cpxlsyo7x7k4k4x2hzn6a9j'
	print len(input_str)
	# Generate key
	key_file = 'aes_key'
	key1 = aes_read_key(block_size, key_file)
	aes_encoded = aes_encrypt(input_str, key1, padding, block_size)
	print aes_encoded
	aes_decoded = aes_decrypt(aes_encoded, key1, padding, block_size)
	if aes_decoded == input_str:
		print 'yes'


















