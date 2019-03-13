from math import *
import numpy as np 


class Cache(object):
	_slots_ = ['size','line_size','set_lines','memory_address_size','cache_replace_policy','size_unit']
	
	def __init__(self,size,line_size,set_lines,memory_address_size,cache_replace_policy,size_unit):
		self.size = size
		self.line_size = line_size
		self.set_lines = set_lines
		self.memory_address_size = memory_address_size
		self.cache_replace_policy = cache_replace_policy
		self.size_unit = size_unit

class CacheLine:
	_slots_ = ['valid','tag','lastAccess','nbrAccess']
	
	def __init__(self):
		self.valid = 0
		self.tag = 0
		self.Access = 0
		self.nbrAccess = 0

def openFile(filePath):
	with open(filePath,"r") as trace:
		fileLines = trace.readlines()
	toInt = lambda list: [int(list[c],16) for c in range(0,len(list))] #mem_requests +=1
	return toInt(fileLines)	

def  lru(cacheLines):
	less = 0
	for current in range(0,len(cacheLines) - 1):
		for next in range(current,len(cacheLines)):
			if cacheLines[current].Access < cacheLines[next].Access:
				less = current
			else: 
				less = next
				break
	return less 
	
def mapeamentoDireto(cache,datas,nbr_cache_lines,tupla_bits):

	cacheLines = [CacheLine() for _ in range(nbr_cache_lines)]
	
	indexMask = 0  
	tagMask = 0
	
	for bit in range(0,tupla_bits[1]):         
		indexMask = indexMask << 1                 
		indexMask = indexMask | 0x01
	
	for bit in range(0,tupla_bits[2]):
		tagMask = tagMask << 1
		tagMask = tagMask | 0x01
	
	cache_hit = 0
	cache_miss = 0
	
	for data in datas:
		index = (data >> tupla_bits[0])  & indexMask
		tag = (data >> tupla_bits[0] + tupla_bits[1]) & tagMask
		
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
	adress_lines_int = openFile("trace")
    
	cache = Cache(2,16,4,32,0,20)
 
	print("Tamanho da cache: "+str(cache.size)+"KB\n"+
		"Tamanho do bloco: "+str(cache.line_size)+ 
		"\nLinhas por conjunto da cache: " +
		str(cache.set_lines))
		
	nbr_cache_lines = int(cache.size*2**cache.size_unit/cache.line_size)
	cache_set_size = cache.line_size/ cache.set_lines
	
	offset_bits = int(log(cache.line_size,2))
	index_bits = int(log(nbr_cache_lines))
	tag_bits = cache.memory_address_size - offset_bits - index_bits
	
	tupla_bits = (offset_bits,index_bits,tag_bits)
	
	print("Cache Formato: \nTAG: "+
			str(tag_bits)+"\nINDEX: "+
			str(index_bits)+"\nOFFSET: "+
			str(offset_bits))
	

	cache_hit,cache_miss = mapeamentoDireto(cache,adress_lines_int,nbr_cache_lines,tupla_bits)
	
	print("Mapemanto direto\n"+
			"Cache hit: " + str(cache_hit*100/len(adress_lines_int))+
			"\nCache Miss: " + str(cache_miss*100/len(adress_lines_int)))

main()