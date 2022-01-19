import json, copy
from types import SimpleNamespace
from collections import MutableMapping, Sequence


#### Flag setting
debug = True
suite = "basic"


##### Sample test data
data = {
  "data": [{
    "type": "articles",
    "id": "1",
    "attributes": {
      "title": "JSON:API paints my bikeshed!",
      "body": "The shortest article. Ever.",
      "created": "2015-05-22T14:56:29.000Z",
      "updated": "2015-05-22T14:56:28.000Z"
    },
    "relationships": {
      "author": {
        "data": {"id": "42", "type": "people"}
      }
    }
  }],
  "included": [
    {
      "type": "people",
      "id": "42",
      "attributes": {
        "name": "John",
        "age": 80,
        "gender": "male"
      }
    }
  ],
  "name" : "testing",
  "age" : 34,
  "another" : {"field" : "ops", "google" : "camel", "crazy" : {"1":"2","3":"4"}}
}
print(json.dumps(data,indent=3))

variable = "data"

def get_paths(source):
    """
    Function to get complete path for each key in the JSON
    """
    paths = []
    if isinstance(source, MutableMapping):  # found a dict-like structure...
        for k, v in source.items():  # iterate over it; Python 2.x: source.iteritems()
            paths.append([k])  # add the current child path
            paths += [[k] + x for x in get_paths(v)]  # get sub-paths, extend with the current
    # else, check if a list-like structure, remove if you don't want list paths included
    elif isinstance(source, Sequence) and not isinstance(source, str):
        #                          Python 2.x: use basestring instead of str ^
        for i, v in enumerate(source):
            paths.append([i])
            paths += [[i] + x for x in get_paths(v)]  # get sub-paths, extend with the current
    return paths

elements = get_paths(data)

list_keys = []
if debug: print(elements)
if debug: print(elements[3])
"""
remove this - unnecessary 

k=copy.deepcopy(data)
length = len(elements[6])
counter = 1
for i in elements[6]:
	if debug: print(i,counter,length)
	if counter == length:
		k[i] = "377777777773"
	else:
		k = k[i]
	counter += 1
if debug: print(str(k))
if debug: print(dir(k))
if debug: print(data)
"""


### code to generate the complete string path depending upon input from above function

for each in elements:
	if len(each) == 1:
		path = variable + str(each)
	else:
		counter = 0
		path = ""
		for e in each:
			if isinstance(e, str):
				if not counter:
					path = variable + str('["' + e + '"]')
					counter = 1
				else:
					path = path + str('["'+e+'"]')
			else:
				path = path + '[' + str(e) + ']'
	list_keys.append(path)

if debug: print(list_keys)



def set_value(d, selector, val):
    """
    Follow the selector inside `d` to set the value of the last node.
    Function is used to write value to a particular key
    """
    if not selector.startswith("data"):
        raise ValueError("the query does not start with 'data'")

    # start parsing the selector
    parts = selector[len("data"):].split("]")
    if parts[-1] != "":
        raise ValueError("the query does not end with a ']'")
    parts.pop()  # remove the last part, we know it's empty
    current_node = d
    for part in parts[:-1]:  # for each part but not the last
        if (part.startswith("['") and part.endswith("'")) or \
                (part.startswith("[\"") and part.endswith("\"")):  # it's a dictionary access
            key_name = part[2:-1]
            try:
                current_node = current_node[key_name]
            except:
                print("ignore this--4--")
        elif part[1] in ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9"):
            index_val = int(part[1:])
            try:
                current_node = current_node[index_val]
            except:
                print("ignore this--3--")
        else:
            raise ValueError(f"the query part {part[:-1]!r} is syntactically incorrect")
    # then handle the last part
    last_part = parts[-1]
    if (last_part.startswith("['") and last_part.endswith("'")) or \
            (last_part.startswith("[\"") and last_part.endswith("\"")):  # it's a dictionary access
        key_name = last_part[2:-1]
        try:
        	current_node[key_name] = val
        except:
            print("ignore this--1--")
    elif last_part[1] in ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9"):
        index_val = int(last_part[1:])
        try:
            current_node[index_val] = val
        except:
            print("ignore this--2--")
    else:
        raise ValueError(f"the query part {last_part!r} is syntactically incorrect")

    return d


final_list = []
payloads = ['<<<','>>>','{{{}}}', '<script>alert("testing")</script>']

payloads_dict = [ { 'suite':'basic', 'attack_vector' : 'xss' , 'input' : '<script>alert("pentest")</script', 'response' : 'alert("pentest")' },
				{  'suite':'basic', 'attack_vector' : 'xss' , 'input' : '<img src=# onerror\x3D"javascript:alert("pentest")" >', 'response' : 'alert("pentest")'},
				{  'suite':'deep', 'attack_vector' : 'xss' , 'input' : '<image src="javascript:alert(1)">', 'response' : 'alert(1)'},
				{  'suite':'normal', 'attack_vector' : 'character filtration' , 'input' : '<<<>>>{{}}[[]]', 'response' : '<<<>>>{{}}[[]]'},
				{ 'suite':'basic', 'attack_vector' : 'character filtration' , 'input' : '%%&&##@@!!', 'response' : '%%&&##@@!!'}
				]

#### code to generate n number of request data using the payloads and suite
for each in list_keys:
    for p in payloads_dict:
        data2 = copy.deepcopy(data)
        if suite == p['suite']:
            ret = set_value(data2, each, p['input'])
            final_list.append(ret)

if debug: print(len(list_keys), len(final_list), final_list[40], final_list[39], final_list[41])

