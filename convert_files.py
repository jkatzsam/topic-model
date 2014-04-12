#Julian Katz-Samuels
#February 12th, 2014

"""
This file does the following:
1. converts raw files from New York Times Corpus into JSON files.
2. determines which articles are relevant to a given issue using keywords.
3. For those that are relevant, converts relevant articles into a 
flat dictionary as a json file and saves a complementary file 
that just has the text of the article and its title.

I takes two arguments: a year argument and a keyword argument. 
"""


"""
Development Notes:

I need a better way to filter out articles. 

"""

import os, json, time, argparse
import xml.etree.ElementTree as ET

###helper classes

class decode_xml:
    """
    A class for decoding xml files in NYT Corpus
    into data that I need.
    """
    def __init__(self, file, root):
        self.file = file
        self.root = root
        self.article_data = {}
    def get_data(self):
        #grab meta data
        for type in self.root.findall('head'): 
            for child in type.getchildren(): 

                if child.tag == "meta":
                    values = child.attrib.values()
                    self.article_data[values[1]] = values[0]
 
                if child.tag == "docdata":
                    for child1 in child.getchildren():
                
                        if child1.tag == "doc-id":
                            for key, value in child1.attrib.iteritems():
                                self.article_data[key] = value
                
                        if child1.tag == "identified-content":
                            for child2 in child1.getchildren():
                                values = child2.attrib.values()
                
                                if child2.tag == "person" or child2.tag == "org":
                                    if child2.tag in self.article_data:
                                        self.article_data[child2.tag].append(values[0])
                                    else:
                                        self.article_data[child2.tag] = [values[0]]
                                else:
                                    if len(values) == 2:
                                        if values[0] in self.article_data:
                                            self.article_data[values[0]].append(values[1])
                                        else:
                                            self.article_data[values[0]] = [values[1]]
                
                if child.tag == "pubdata":
                    for key, value in child.attrib.iteritems():
                        self.article_data[key] = value

        #grab text data
        for type in self.root.findall('body'): 
            for child in type.getchildren(): 

                #grab content text data
                if child.tag == "body.content":
                    for child1 in child.getchildren():
                        class_type = child1.attrib['class']
                        if child1.tag == "block" and class_type == 'full_text':
                            self.article_data['text'] = []
                            for child2 in child1.getchildren():
                                self.article_data['text'].append(child2.text)
                            ls = self.article_data['text']
                            self.article_data['text'] = ' '.join(ls)
                
                #grab title data
                if child.tag == "body.head":
                    for child1 in child.getchildren():
                        if child1.tag == "hedline":
                            for child2 in child1.getchildren():
                                if child2.attrib == {}:
                                    self.article_data['title'] = child2.text
                                    continue
                                

def convert_files(year, keywords)
    start_time = time.time()
    #Step 1: Convert all files in folder to json format 

    #create folder for year if it doesn't exist
    year_path = "/Volumes/data/modified_data/" + year + '/'
    if not os.path.exists(year_path):
        os.makedirs(year_path)

    text_path = year_path + "/text/"
    nyt_path = "/Volumes/data/raw_data/" + year + "/"
    json_path = year_path + "json/"
    article_path = year_path + "article_data/"
    article_counter = 0 #counts number of articles
    text_counter = 0 #counts the number of articles with text
    relevant_counter = 0
    for dir1 in os.listdir(nyt_path):
        if dir1 == ".DS_Store":
            continue
            
        json_path_1 = json_path + dir1 + '/'
        nyt_path_1 = nyt_path + dir1 + '/'
        
        #create folders if they don't exist
        if not os.path.exists(json_path_1):
            os.makedirs(json_path_1)      

        for dir2 in os.listdir(nyt_path_1):
            if dir2 == ".DS_Store":
                continue
                
            json_path_2 = json_path_1 + dir2 + '/'
            nyt_path_2 = nyt_path_1 + dir2 + '/'
            
            if not os.path.exists(json_path_2):
                os.makedirs(json_path_2)
                
            for filename in os.listdir(nyt_path_2):
                if filename == ".DS_Store":
                    continue
                    
                #create new names
                new_filename = filename[:len(filename)-4] + '.json'
                input_object = nyt_path_2 + filename

                #decode xml format
                tree = ET.parse(input_object)
                root = tree.getroot()
                decode = decode_xml(tree, root)
                decode.get_data()
                article_data = decode.article_data

                if 'title' in article_data:
                    title = article_data['title']
                if 'text' in article_data:
                    text = article_data['text']

                #delete title and text elements from article_dictionary
                article_data.pop('title', None)
                article_data.pop('text', None)

                #Only save articles that contain keywords
                for word in keywords:
                    if word in text or word in title:
                        relevant_counter += 1                 
                        #Write text and tile files
                        with open(text_path + filename[:len(filename)-4] + ".txt", 'w') as file:
                            file.write(text.encode('utf-8'))
                        with open(text_path + filename[:len(filename)-4] + "_title.txt", 'w') as file:
                            file.write(title.encode('utf-8'))

                        #Save article_data in another file
                        with open(article_path + filename[:len(filename)-4] + '_data' + '.json', 'wb') as outfile:
                            json.dump(article_data, outfile)
                        break

if __name__ == "__main__":
    #parse arguments
    parser = argparse.ArgumentParser(description='Process year and a list of keywords')
    parser.add_argument('year', metavar='year', type=str, nargs=1,
                       help='a year string between 1987 and 2007')
    parser.add_argument('keywords', metavar='keywords', type=str, nargs='+',
                       help='A collection of keywords')

    args = parser.parse_args()
    year = args.year[0]
    keywords = args.keywords

    #convert_files
    convert_files(year, keywords)
  
    
###Testing Code

# for type in root.findall('head'): 
#     for child in type.getchildren(): 
#         print child.tag
#         if child.tag == "title":
#             l = child
#         if child.tag == "docdata":
#             print "DOC DATA STUFF"
#             for child1 in child.getchildren():
#                 print child1.tag

# for type in root.findall('body'): 
#     for child in type.getchildren(): 
#         print child.tag, child.attrib
#         if child.tag == "body.content":
#             print "DOC DATA STUFF"
#             for child1 in child.getchildren():
#                 print child1.tag, child1.attrib
#                 class_type = child1.attrib['class']
#                 if child1.tag == "block" and class_type == 'full_text':
#                     for child2 in child1.getchildren():
#                         # print "NEW BLOCK OF TEXT"
#                         print child2.tag, child2.attrib
#                         print child2.text
#                         # print child2.text
    

# for type in root.findall('body'): 
#     for child in type.getchildren(): 
#         if child.tag == "body.head":
#             for child1 in child.getchildren():
#                 if child1.tag == "hedline":
#                     for child2 in child1.getchildren():
#                         print child2.tag, child2.attri
#                         print child2.text
#                         # print child2.text
    