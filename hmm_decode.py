from __future__ import division
import os
import xml.etree.ElementTree as ET
import math
import operator
import itertools
import binascii

def get_all_state(fsa_file):
	tree = ET.parse(fsa_file)
	root = tree.getroot()
	# Get all states and transitions
	state = []
	for child in root:
		for gdchild in child:
			if gdchild.tag == 'e-state':
				state.append(gdchild.attrib['id'])
	return state

def count_one_branch(start, fsa_file):
	tree = ET.parse(fsa_file)
	root = tree.getroot()
	# Get all states and transitions
	state = []
	for child in root:
		for gdchild in child:
			if gdchild.tag == 'e-state':
				state.append(gdchild.attrib['id'])
	# Given a start state
	choice = []
	prob = []
	end = []
	for child in root:
		for gdchild in child:
			if gdchild.tag == 'event' and gdchild.attrib['state1ID'] == start:
				choice.append(gdchild.attrib['name'])
				prob.append(gdchild.attrib['value'])
				end.append(gdchild.attrib['state2ID'])
	return choice, prob, end

# Convert the list of parameters into probability
# For example, para for [1, 1/2, 1/4] is [0,1,2]
# The result will be [1/2, 1/4, 1/4]
def convert_list_to_prob(list1):
    sumsum = sum(list1)
    index = round_up(sumsum)
    output = []
    for i in range(index+2):
        if list1[i] != 0:
            tmp = [1/2**(i)] * list1[i]
            output += tmp
    return output

# For list1: [x1,x2] and list2: [x3,x4], calculate result = (x1-x3)^2 + (x2-x4)^2
def diff_two_list(list1, list2):
	diff = 0
	for i in range(len(list1)):
		diff += (list1[i] - list2[i]) * (list1[i] - list2[i])
	return diff

# It will round a number up to the closest 2^n
def round_up(num):
	i = 0
	while 2**i < num:
		i += 1
	return i

# When len(output) >= 2, we have to decide which is the best
def find_best_match(prob, output):
	diff = []
	for i in range(len(output)):
		prob_output = convert_list_to_prob(output[i])
		one_diff = diff_two_list(prob, prob_output)
		diff.append(one_diff)
	min_diff = min(diff)
	index = diff.index(min_diff)
	return output[index]

# Convert each element of a list from string to float number
def convert_string_list_to_float(list1):
	output = [0.0] * len(list1)
	for i in range(len(list1)):
		output[i] = float(list1[i])
	return output

# How to map elements of two lists that have the same number of elements
# Assume list2 is sorted already (from largest)
def map_two_lists(list1, list2, bit_list):
	ind = list(reversed(sorted(range(len(list1)), key=lambda k: list1[k])))
	ordered_list2 = []
	ordered_bit = []
	for i in range(len(ind)):
		ordered_list2.append(list2[ind.index(i)])
		ordered_bit.append(bit_list[ind.index(i)])
	return ordered_list2, ind, ordered_bit

# It gives a length of (size) division of a number (n)
def sum_to_n(n, size):
    # http://stackoverflow.com/questions/2065553/get-all-numbers-that-add-up-to-a-number
    if size == 1:
        yield [n]
        return
    for i in range(0, n+1):
        for tail in sum_to_n(n - i, size - 1):
            yield [i] + tail


# Generate all parameters that will sum up to 1
# It generates [a_i] for sum(a_i * 2^i) == 0 
def gen_all_combo(num):
    index = round_up(num)
    output = []
    for partition in sum_to_n(num, index+2):
        sumsum = 0
        if partition[0] <= 1:
            j = 0
            while j < len(partition):
                sumsum += (1/2**(j))*partition[j]
                j += 1
            if sumsum == 1.0:
                output.append(partition)
    return output

def map_list_to_bit_fake(list2):
	if list2 == [1/2,1/4,1/8,1/8]:
		output = ['0','10','110','111']
	if list2 == [1/2,1/2]:
		output = ['0','1']	
	if list2 == [1/2,1/4,1/4]:
		output = ['0','10','11']	
	return output

# Assgin 0/1 to probabilities
def map_list_to_bit(my_list):
	# Initialize the list
	result = ['a'] * len(my_list)
	limit = 1
	# Map the list for the largest value
	max_value, index = find_max_value_index(my_list, limit)
	integer = int(math.log(1/max_value,2))
	all_combos = gen_all_combos(integer)
	result, leftover = assign_value(my_list, all_combos, index, result, limit)
	# Continue to assign to the next largest value until all values are assigned
	while leftover != []:
		limit = max_value
		max_value2, index = find_max_value_index(my_list, limit)
		diff = int(math.log(1/max_value2,2)) - int(math.log(1/max_value,2))
		all_combos = adjust_value(leftover, diff)
		result, leftover = assign_value(my_list, all_combos, index, result, limit)
		max_value = max_value2
	return result


# Go to the next level from the leftover of the last assignment
# For example, if the leftover = ['1110','1111'], diff = 1
# output = ['11100','11101','11110','11111']
def adjust_value(leftover, diff):
	output = []
	stuff = ['0','1']
	for i in range(len(leftover)):
		for combination in itertools.product(xrange(2), repeat=diff):
			if not leftover[i] + ''.join(map(str, combination)) in output:
				output.append(leftover[i] + ''.join(map(str, combination)))	
	return output

# Actually assign the value given some limits
def assign_value(my_list, all_combos, index, result, limit):
	used_combos = []
	for i in range(len(index)):
		result[index[i]] = all_combos[i]
		used_combos.append(all_combos[i])
	leftover = delete_list1_from_list2(used_combos, all_combos)
	return result, leftover

# Delete list1 from list2 
def delete_list1_from_list2(list1, list2):
	output = []
	for i in range(len(list2)):
		if not list2[i] in list1:
			output.append(list2[i])
	return output

# Find the maximum value of a list (less than a limit)
def find_max_value_index(my_list, limit):
	max_value = 0
	index = []
	for i in range(len(my_list)):
		if my_list[i] >= max_value and my_list[i] < limit:
			max_value = my_list[i]
			index.append(i)
	return max_value,index
	
# Generate all combonations of 01s given the length
def gen_all_combos(num):
	output = []
	stuff = ['0','1']
	for combination in itertools.product(xrange(2), repeat=num):
		output.append(''.join(map(str, combination)))
	return output

# One step through the HMM
def read_hmm(filename, start, all_prob, all_state):
	#random.seed(one_seed)
	tree = ET.parse(filename)
	root = tree.getroot()
	# Get all states and transitions
	state = []
	for child in root:
		for gdchild in child:
			if gdchild.tag == 'e-state':
				state.append(gdchild.attrib['id'])
	# Given a start state
	choice = []
	prob = []
	end = []
	for child in root:
		for gdchild in child:
			if gdchild.tag == 'event' and gdchild.attrib['state1ID'] == start:
				choice.append(gdchild.attrib['name'])
				prob.append(gdchild.attrib['value'])
				end.append(gdchild.attrib['state2ID'])
	prob_new = all_prob[all_state.index(start)]
	bit_list = map_list_to_bit(prob_new)
	(prob, all_index, ordered_bit) = map_two_lists(prob, prob_new, bit_list)
	return choice, end, ordered_bit

def hmm_decode(message, last_num, start):
	output = ''
	while message != '':
		choice, end, bit_list = read_hmm(filename, start, all_prob, all_state)
		ind = choice.index(message[:1])		
		start = end[ind]
		message = message[1:]
		output += bit_list[ind]
	if last_num != 0:
		output = output[:last_num * (-1)]
	plain = binascii.unhexlify('%x' % int(output,2))
	return plain

# Main function
if __name__ == '__main__':
	filename = '500KL3.fsa'
	# Read the prob file
	prob_file = 'hmm-stat-prob-new'
	f = open(prob_file)
	line = f.readlines()
	f.close()
	all_prob = [[] for i in range(len(line))]
	for i in range(len(line)):
		value = line[i].split(' ')
		value = value[2:]
		tmp = ''.join(value)
		tmp2 = (tmp.strip()).split(',')
		all_prob[i] = [float(it) for it in tmp2]
	all_state = get_all_state(filename)

	# Choose a random start state
	start = '1440'

	# Read into the encoded_result
	f = open('dm_output')
	line = f.readlines()
	f.close()
	text = [line[i].strip() for i in range(len(line))]
	num = [0] * len(text)
	mess = [''] * len(text)
	output = [''] * len(text)
	for i in range(len(line)):
		try:
			num[i] = int(text[i][-2:])
			mess[i] = text[i][:-2]
			output[i] = hmm_decode(mess[i], num[i], start)
		except:
			num[i] = 0	
			mess[i] = text[i]
			output[i] = hmm_decode(mess[i], num[i], start)
	print output

























