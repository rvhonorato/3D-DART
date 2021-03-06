#!/usr/bin/env python2.7

USAGE = """
==========================================================================================

Author:				Marc van Dijk, Department of NMR spectroscopy, Bijvoet Center
					for Biomolecular Research, Utrecht university, The Netherlands
Copyright (C):		2006 (DART project)
DART version:		1.2 (25-11-2008)
DART module: 		Xpath.py
Module function:	Independent Xpath-like implementation for quering XML documents.
					Load XML document as file, string or URL. XML documents can be
					queried using the Evalaute function of Xpath. The syntax allows
					to search for elements and attributes in the XML tree using a
					dictionary notation. The tree is traversed in a hierarchical
					manner. The syntax looks as follows:
			
					{1:{'element':'chain','attr':{'ID':'A'}},2:{'element':'residue',
					 'attr':{'ID':'CYT','ID':'GUA'}}}
			
					Xpath searches the XML for the first instance of the element
					'chain' which is than adressed as level 1. All following elements
					must match the query. The first element has to match the attribute
					with name ID and value A. Multiple attribute names can be queried
					or non at all (all will be accepted).The instances of the XML
					document that match the query will be stored in a dictionary with
					the level as key. Relevant information can be extracted from the
					nodes in this dictionary using the functions: getElem, getAttr and
					getData. Results are stored in self.result
					- getElem will return the element name associated with the node
					- getAttr will return the attribute name and value associated with
					  the node (if any).
					- getData will return the data associated with the node (if any).
			
					These functions accept selections and can return the data as one
					continues list of values (export='string') or as a list of lists
					(export='list', default). All returned data will be checked on the
					data type (string, float or boolean).
					The dictionary of stored nodes can be queried again by suppling
					Evaluate with the optione source=<node adress>. The function
					ClearResult will empty the lists of stored results ready for
					excepting a new query on stored nodes
Module depenencies:	Standard python2.4 modules

==========================================================================================
"""

"""Import modules"""
from xml.dom import EMPTY_NAMESPACE, minidom, Node
import sys,string

class Xpath:
	
	"""Independent Xpath-like implementation for quering XML documents.
           Load XML document as file, string or URL. XML documents can be
           queried using the Evalaute function of Xpath. The syntax allows
           to search for elements and attributes in the XML tree using a
           dictionary notation. The tree is traversed in a hierarchical
           manner. The syntax looks as follows:
           
           {1:{'element':'chain','attr':{'ID':'A'}},2:{'element':'residue',
            'attr':{'ID':['CYT','GUA']}}}
           
           Xpath searches the XML for the first instance of the element
           'chain' which is than adressed as level 1. All following elements
           must match the query. The first element has to match the attribute
           with name ID and value A. Multiple attribute names can be queried
           or non at all (all will be accepted).The instances of the XML
           document that match the query will be stored in a dictionary with
           the level as key. Relevant information can be extracted from the
           nodes in this dictionary using the functions: getElem, getAttr and
           getData. Results are stored in self.result
           - getElem will return the element name associated with the node
           - getAttr will return the attribute name and value associated with
             the node (if any).
           - getData will return the data associated with the node (if any).
           
           These functions accept selections and can return the data as one
           continues list of values (export='string') or as a list of lists
           (export='list', default). All returned data will be checked on the
           data type (string, float or boolean).
           The dictionary of stored nodes can be queried again by suppling
           Evaluate with the optione source=<node adress>. The function
           ClearResult will empty the lists of stored results ready for
           excepting a new query on stored nodes"""
	
	def __init__(self, inputfile):
		
		self.query = {}
		self.level = 1
		self.result = []
		self.nodeselection = {}
		
		self.XMLdata = self._OpenXMLdoc(inputfile)
	
	def _OpenXMLdoc(self, inputfile):
		source = self._OpenAnything(inputfile)
		xmldoc = minidom.parse(source)
		source.close
		return xmldoc
	
	def _OpenAnything(self, inputfile):
		
		if hasattr(inputfile, "read"):
			return inputfile
		
		if inputfile == '-':
			return sys.stdin
		
		import urllib
		try:
			return urllib.urlopen(inputfile)
		except Exception:
			pass
		
		try:
			return open(inputfile)
		except Exception:
			pass
		
		import StringIO
		return StringIO.StringIO(str(inputfile))
	
	def _EvaluateNodeAttribute(self,node,NodeQuery):
		
		"""Get all attribute nodes of the given element node and match against query,
		   Return True if query matches and False if not"""
		
		if NodeQuery == None:
			return True
		else:
			attributes = []
			attrNodes = node.attributes.values()
			for Node in attrNodes:
				attributes.append(Node.localName)
			
			result = []
			for attribute in attributes:
				if attribute in NodeQuery.keys():
					if type(NodeQuery[attribute]) == type([]):
						if (node.getAttribute(attribute)).strip() in NodeQuery[attribute]:
							result.append(True)
					else:
						if (node.getAttribute(attribute)).strip() == NodeQuery[attribute]:
							result.append(True)
			if True in result:
				return True
			else:
				return False
	
	
	def _WalkTree(self,parent=None,level=None):
		
		"""Iterate over all nodes of the tree passing each node to self._EvaluateNodeElement for
		   evaluation against the query. The loop searches for the first occurence of the first
		   element of the query. As long as this element has not been found result = 0 and
		   level will not be increased. When it has been found result = 1 and level will be
		   increased with 1 (next element in query)"""
		
		NodeQuery = self.query[level]
		if NodeQuery['element'] == None:
			Nodes = []
			for node in parent.childNodes:
				if node.nodeType == Node.TEXT_NODE:
					pass
				else:
					Nodes.append(node)
		else:
			Nodes = parent.getElementsByTagName(NodeQuery['element'])
		
		if len(Nodes) > 0:
			for node in Nodes:
				result = self._EvaluateNodeAttribute(node,NodeQuery['attr'])
				if result == True:
					self.nodeselection[level].append(node)
	
	def _TypeCheck(self,inputstring):
		
		"""Check the type of input string and return appropriate type, either float, boolean or string"""
		
		if inputstring == 'False':
			return False
		elif inputstring == 'True':
			return True
		else:
		        try:
		        	value = float(inputstring)
		        	return value
		        except:
		        	return (str(inputstring)).strip()
	
	def ClearResult(self):
		
		"""Clear content of result for additional queries"""
		
		self.result = []
	
	def getAttr(self,node=None,selection=None,export='list'):
		
		"""Append attributes and values to result (all or a selection) and export
		   as continues list of values or list of lists (default)"""
		
		tmp = []
		attrNodes = node.attributes.values()
		for Node in attrNodes:
			attr = Node.localName
			if not selection == None:
				if attr in selection:
					if export == 'string':
						self.result.append(self._TypeCheck(node.getAttribute(attr)))
					elif export == 'list':
						tmp.append(self._TypeCheck(node.getAttribute(attr)))
			else:
			        if export == 'string':
			        	self.result.append(self._TypeCheck(attr))
			        	self.result.append(self._TypeCheck(node.getAttribute(attr)))
			        elif export == 'list':
			        	tmp.append(self._TypeCheck(attr))
			        	tmp.append(self._TypeCheck(node.getAttribute(attr)))
		
		if len(tmp) > 0:
			self.result.append(tmp)
	
	def getElem(self,node=None,selection=None,export='list'):
		
		"""Append element names to result (all or selection) and export as continues list
		   of values or list of lists (default)"""
		
		tmp = []
		element = node.tagName
		if not selection == None:
        		if element in selection:
        			if export == 'string':
        				self.result.append(self._TypeCheck(element))
        			elif export == 'list':
        				tmp.append(self._TypeCheck(element))
        	else:
        		if export == 'string':
        			self.result.append(self._TypeCheck(element))
        		elif export == 'list':
        			tmp.append(self._TypeCheck(element))
		
		if len(tmp) > 0:
			self.result.append(tmp)
	
	def getData(self,node=None,selection=None,export='list'):
		
		"""Append the data fields of the node to result and export as continues list
		   of values or list of lists (default)"""
		
		tmp = []
		for child in node.childNodes:
			if child.nodeType == Node.TEXT_NODE:
				data = child.nodeValue
			if not selection == None:
				if data in selection:
					tmp.append(self._TypeCheck(data))
			else:
				tmp.append(self._TypeCheck(data))
		
		if len(tmp) > 0:
			if export == 'string':
				strContent = string.join(tmp)
				self.result.append(strContent.strip())
			elif export == 'list':
				self.result.append(tmp)
		
	def PrintXML(self,node):
		
		"""Print node selection to xml"""
		
		print node.toxml()
	
	def Evaluate(self,source=None,query=None):
		
		"""Main routine"""
		
		self.query = query
		if source == None:
			source = self.XMLdata
		
		"""Walk the XML tree"""
	     	self.nodeselection[0] = [source]
	     	for level in self.query.keys():
	     		self.nodeselection[level] = []
	     		for node in self.nodeselection[level-1]:
					self._WalkTree(parent=node,level=level)

if __name__ == '__main__':
	
	"""For testing purposes"""
	print USAGE
	query = Xpath('test.xml')
	query.Evaluate(query={1:{'element':'chain','attr':None},2:{'element':'resid','attr':{'ID':['CYT','GUA']}},3:{'element':'atom','attr':{'ID':'P'}}})
	for node in query.nodeselection[2]:
		query.getAttr(node=node,selection=['ID','nr'])
	print query.result
	query.ClearResult()
	for node in query.nodeselection[2]:
		query.Evaluate(source=node,query={1:{'element':'atom','attr':{'ID':"C4'"}}})
		for res in query.nodeselection[1]:
			query.getAttr(node=res,selection='ID')
	print query.result
	
	
	
