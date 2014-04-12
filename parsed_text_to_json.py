#Julian Katz-Samuels
#February 15th, 2014

"""
This file grabs token, dependency, and parse data from
the outputed parsed text .xml files, puts it in dictionaries,
and save as json file.
"""

#3rd party modules
import os, json, sys
import xml.etree.ElementTree as ET

#custom modules
from convert_files import decode_xml

#Helper Functions

def extend_path(path, extension):
    return path + '/' + extension

def create_path(path):
    if not os.path.exists(path):
        os.makedirs(path)

#helper class for parsing xml file
class decode_xml_parsed(decode_xml):
    def get_data(self):
        coref_counter = 1
        for type in root.findall('document'):
            for child in type.getchildren():
                self.article_data[child.tag] = {}
                for child1 in child.getchildren():
                    if 'id' in child1.attrib:
                        sentence_id_list = child1.attrib.keys() + child1.attrib.values()
                        sentence_id = "sentence " + sentence_id_list[0] + ' ' + sentence_id_list[1]
                        self.article_data[child.tag][sentence_id] = {}
                    if child1.tag != "coreference":
                        for child2 in child1.getchildren():
                            if child2.tag == "parse":
                                self.article_data[child.tag][sentence_id]["parse"] = child2.text
                            elif child2.tag == "tokens":
                                self.article_data[child.tag][sentence_id]["tokens"] = {}
                                for child3 in child2.getchildren():
                                    if child3.tag == "token":
                                        token_id_list = child3.attrib.keys() + child3.attrib.values()
                                        token_id = token_id_list[0] + ' ' + token_id_list[1]
                                        self.article_data[child.tag][sentence_id]["tokens"][token_id] = {}
                                        for child4 in child3.getchildren():
                                            self.article_data[child.tag][sentence_id]["tokens"][token_id][child4.tag] = child4.text
                            elif child2.tag == "dependencies" and child2.attrib["type"] == "collapsed-ccprocessed-dependencies":
                                self.article_data[child.tag][sentence_id]["collapsed-ccprocessed-dependencies"] = []
                                for child3 in child2.getchildren():
                                    dep =[]
                                    type = child3.attrib.values()[0]
                                    dep.append(type)
                                    for child4 in child3.getchildren():
                                        dep.append(child4.text) #Note: governor comes first, then dependent
                                    self.article_data[child.tag][sentence_id]["collapsed-ccprocessed-dependencies"].append(dep)
                    elif child1.tag == "coreference":
                        coref_counter += 1 #increment counter
                        coref_num = "coreference " + str(coref_counter)
                        self.article_data[child.tag][coref_num] = []
                        for child2 in child1.getchildren():
                            l = {}
                            if "representative" in child2.attrib and child2.attrib["representative"] == "true":
                                l["representative"] = "true"
                            else:
                                l["representative"] = "false"
                            for child3 in child2.getchildren():
                                l[child3.tag] = child3.text
                            self.article_data[child.tag][coref_num].append(l)
        
        

#program
def parsed_text_to_json(year):
    parsed_path = "/Volumes/data/modified_data/" + year + "/parsed"
    parsed_json_path = "/Volumes/data/modified_data/" + year + "/parsed_json"

    #create json folder if it doesn't exist
    create_path(parsed_json_path)

    #counter
    counter = 0

    for filename in os.listdir(parsed_path):
        if filename == ".DS_Store":
            continue
        filepath = extend_path(parsed_path, filename)

        print filepath

        counter += 1
        print counter

        tree = ET.parse(filepath)
        root = tree.getroot()
        decode = decode_xml_parsed(tree, root)
        decode.get_data()
        article_data = decode.article_data
        output_path = extend_path(parsed_json_path, filename[:len(filename)-4])

        print output_path

        with open(output_path + '_data' + '.json', 'wb') as outfile:
            json.dump(article_data, outfile)
    
if __name__ == "__main__":
    #specify year to have certain files to parse. 
    year = sys.argv[1]
    #convert parsed text to json
    parsed_text_to_json(year)


###testing code

                    
                                
                     
                     
