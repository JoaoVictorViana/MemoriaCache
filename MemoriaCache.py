from math import *
import numpy as np 


class Cache(object):
	_slots_ = ['size','line_size','set_lines','memory_address_size','replace_policy','size_unit']
	
	def __init__(self,size,line_size,set_lines,memory_address_size,replace_policy,size_unit):
		self.size = size
		self.line_size = line_size
		self.set_lines = set_lines
		self.memory_address_size = memory_address_size
		self.replace_policy = replace_policy
		self.size_unit = size_unit

class CacheLine:
	_slots_ = ['valid','tag','time','nbrAccess']
	
	def __init__(self):
		self.valid = 0
		self.tag = 0
		self.time = 0
		self.nbrAccess = 0

def openFile(filePath):
	with open(filePath,"r") as trace:
		fileLines = trace.readlines()
	toInt = lambda list: [int(list[c],16) for c in range(0,len(list))]
	return toInt(fileLines)	


def lfu(set_lines,cacheSetLines,index):
	less = 0
	for lineCurrent in range(0,set_lines-1):
		for nextLine in range(lineCurrent,set_lines):
			if cacheSetLines[index][lineCurrent].nbrAccess < cacheSetLines[index][nextLine].nbrAccess:
				less = lineCurrent
			else: 
				less = nextLine
				break
				
	new_list = list(cacheSetLines[index][:less]) + list(cacheSetLines[index][less+1:])
	cacheSetLines[index] = np.array(new_list + [CacheLine()])
	return cacheSetLines 

def lru(set_lines,cacheSetLines,index):
	less = 0
	for lineCurrent in range(0,set_lines-1):
		for nextLine in range(lineCurrent,set_lines):
			if cacheSetLines[index][lineCurrent].time < cacheSetLines[index][nextLine].time:
				less = lineCurrent
			else: 
				less = nextLine
				break
				
	new_list = list(cacheSetLines[index][:less]) + list(cacheSetLines[index][less+1:])
	cacheSetLines[index] = np.array(new_list + [CacheLine()])
	return cacheSetLines 
	
def fifo(cacheSetLines,index):
	cacheSetLines[index] = np.array(list(cacheSetLines[index][1:]) + [CacheLine()])
	return cacheSetLines
 

def mapeamentoAssociativo(cache,datas):
	set_size = cache.set_lines*cache.line_size
	nbr_set = int(cache.size*2**cache.size_unit/set_size)
	
	offset_bits = int(log(cache.line_size,2))
	index_bits = int(log(nbr_set,2))
	tag_bits = cache.memory_address_size - offset_bits - index_bits
	
	print("Cache Formato: \nTAG: "+
			str(tag_bits)+"\nINDEX: "+
			str(index_bits)+"\nOFFSET: "+
			str(offset_bits))
			
	cacheSetLines = np.array([ [ CacheLine()  for _ in range(0,cache.set_lines)]   for _ in range(0,nbr_set)])
	
	indexMask = 0  
	tagMask = 0
	
	for bit in range(0,index_bits):         
		indexMask = indexMask << 1                 
		indexMask = indexMask | 0x01
	
	for bit in range(0,tag_bits):
		tagMask = tagMask << 1
		tagMask = tagMask | 0x01
		
	cache_hit = 0
	cache_miss = 0
	timestamp = 0
	
	for data in datas:
		timestamp += 1
		index = (data >> offset_bits)  & indexMask
		tag = (data >> offset_bits + index_bits) & tagMask
		full = False
		for line in range(0,cache.set_lines):
			
			if cacheSetLines[index][line].valid == 0:
				cacheSetLines[index][line].tag = tag
				cacheSetLines[index][line].valid = 1
				cacheSetLines[index][line].time = timestamp
				cacheSetLines[index][line].nbrAccess += 1
				cache_miss += 1
				full = False 
				break
			else:
				if cacheSetLines[index][line].tag == tag:
					cacheSetLines[index][line].time = timestamp
					cacheSetLines[index][line].nbrAccess += 1
					cache_hit += 1
					full = False
					break
				else:
					full = True 

		
		if(full == True):
			if cache.replace_policy == 0 :
				cacheSetLines = lru(cache.set_lines,cacheSetLines,index)
			elif cache.replace_policy == 1:
				cacheSetLines = lfu(cache.set_lines,cacheSetLines,index)
			else:
				cacheSetLines = fifo(cacheSetLines,index)
			cacheSetLines[index][-1].valid = 1
			cacheSetLines[index][-1].tag = tag
			cacheSetLines[index][line].nbrAccess = 1
			cacheSetLines[index][line].time = timestamp
			full = False
			cache_miss += 1 	
			
	return (cache_hit,cache_miss)
	
def mapeamentoDireto(cache,datas):

	nbr_cache_lines = int(cache.size*2**cache.size_unit/cache.line_size)
	
	offset_bits = int(log(cache.line_size,2))
	index_bits = int(log(nbr_cache_lines,2))
	tag_bits = cache.memory_address_size - offset_bits - index_bits

	print("Cache Formato: \nTAG: "+
			str(tag_bits)+"\nINDEX: "+
			str(index_bits)+"\nOFFSET: "+
			str(offset_bits))
	
	cacheLines = [CacheLine() for _ in range(nbr_cache_lines)]
	
	indexMask = 0  
	tagMask = 0
	
	for bit in range(0,index_bits):         
		indexMask = indexMask << 1                 
		indexMask = indexMask | 0x01
	
	for bit in range(0,tag_bits):
		tagMask = tagMask << 1
		tagMask = tagMask | 0x01
	
	cache_hit = 0
	cache_miss = 0
	
	for data in datas:
		index = (data >> offset_bits)  & indexMask
		tag = (data >> offset_bits + index_bits) & tagMask
		
		if cacheLines[index].valid == 0:
			cacheLines[index].tag = tag
			cacheLines[index].valid = 1
			cache_miss += 1 
		else:
			if cacheLines[index].tag == tag:
				cache_hit += 1
			else:
				cacheLines[index].tag = tag
				cache_miss += 1
				
				
	return (cache_hit,cache_miss)
	
def main():
	address_lines_int = openFile("trace")
    
	cache = Cache(1,16,8,64,2,16)
 
	print("Tamanho da cache: "+str(cache.size)+"KB\n"+
		"Tamanho do bloco: "+str(cache.line_size)+ 
		"\nLinhas por conjunto da cache: " +
		str(cache.set_lines))

	#cache_hit,cache_miss = mapeamentoDireto(cache,address_lines_int)
	cache_hit, cache_miss = mapeamentoAssociativo(cache,address_lines_int)
	
	print("Mapemanto direto\n"+
			"Cache hit: " + str(cache_hit*100.0/len(address_lines_int))+
			"\nCache Miss: " + str(cache_miss*100.0/len(address_lines_int)))
	
main()
