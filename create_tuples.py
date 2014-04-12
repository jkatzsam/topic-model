#Julian Katz-Samuels
#February 15th, 2014

"""
This file 
1. identifies relevant sentences in the json parsed articles,
2. creates for each character tuples (r,w) where w is a word lemma and 
r is a relation as specified in Bammam, O'Connor, Smith, and 
3. creates a file of all the tuples with sentence level data, 
article identifier, and article meta data. 
"""

import json, os, csv, sys, argparse

"""
Development Thoughts:
-might need to clean up the actor field. Right now,
the strings are too long. 

"""

"""
Strategy: 

Create a dictionary of the following form:
{doc_id 
    {sentence/tuple_id
        {actor. tuple, sentence parse
    }}}

Step 1: Use coreference data
The coreference section contains names and all
the sentences where a person is referred to. Use this to
identify the sentences in which a character is referenced.

Step 2: Search for keywords ccprocessed tuples
-only add if that sentence does not contain same tuple

Step 3: Replace all the non-actor words in tuples with 
their lemma
"""



#Helper Functions

def extend_path(path, extension):
    return path + '/' + extension


#Create Tuples
def create_tuples(year, keywords):
    json_path = "/Volumes/data/modified_data/" + year + "/parsed_json"
    article_data = {}
    counter = 0
    for filename in os.listdir(json_path):
        if filename == ".DS_Store":
            continue
        
        #Increment counter
        counter += 1

        file_path = extend_path(json_path, filename)

        #Step 1: Coreference approach
        sentence_data = {}
        relevant_corefs = []
        sentences_found = {} #To make sure there are no repeat sentences

        new_filename = filename[:len(filename)-5] + '.csv'
        with open(file_path, 'rb') as file:
            data = json.load(file)
        #Procedure to identify sentences to extract information from
        if u'coreference' in data:
            coref_keys = data[u'coreference'].keys()
            for key in coref_keys:
                for item in data[u'coreference'][key]:
                    #only extract coreference data if 
                    if item[u'text'] in keywords:
                        relevant_corefs.append(data[u'coreference'][key])
                        continue
                    
            #find text data in sentences that are mentioned in relevant coref data
            for coref in relevant_corefs:
                #Find representative of the coreferences. 
                rep = u""
                for item in coref:
                    if item[u'representative'] == u"true":
                        rep = item[u'text']
                for item in coref:
                    sentence_num = item[u'sentence']
                    if sentence_num in sentences_found: #TODO: could this be a problem
                        continue
                    else:
                        sentences_found[sentence_num] = "found"
                    sentence = unicode("sentence id " + str(sentence_num))
                    if sentence not in sentence_data:
                        sentence_data[sentence] = {}
                        sentence_data[sentence][u"parse"] = data['sentences'][sentence][u"parse"]
                        sentence_data[sentence][u"tokens"] = data['sentences'][sentence][u"tokens"]
                        sentence_data[sentence][u"collapsed-ccprocessed-dependencies"] = []
                        for dep in data["sentences"][sentence][u"collapsed-ccprocessed-dependencies"]:
                            try:
                                conc1 = str(dep[1]) + " " + str(dep[2])
                                conc2 = str(dep[2]) + " " + str(dep[1])
                                dep1 = str(dep[1])
                                dep2 = str(dep[2])
                                dep1_space = " " + dep1 + " "
                                dep2_space = " " + dep2 + " "
                                item_str = str(item[u"text"])
                            except:
                                conc1 = ""
                                conc2 = ""
                                dep1 = dep[1]
                                dep2 = dep[2]
                                dep1_space = dep1
                                dep2_space = dep2
                                item_str = item[u"text"]
                            #Check a number of distinct cases for stirng containment
                            if dep1 == item_str or dep2 == item_str or \
                             conc1 == item_str or conc2 == item_str or \
                             dep1_space in item_str or dep2_space in item_str:
                                sentence_data[sentence][u"collapsed-ccprocessed-dependencies"].append((rep, dep))
                    else:
                        for dep in data["sentences"][sentence][u"collapsed-ccprocessed-dependencies"]:
                            conc1 = unicode(str(dep[1]) + " " + str(dep[2]))
                            conc2 = unicode(str(dep[2]) + " " + str(dep[1]))
                            if dep[1] == item[u"text"] or dep[2] == item[u"text"] or \
                             conc1 == item[u"text"] or conc2 == item[u"text"] and \
                             (rep, dep) not in sentence_data[sentence][u"collapsed-ccprocessed-dependencies"]:
                                #associate the representative name with each dependency tuple
                                sentence_data[sentence][u"collapsed-ccprocessed-dependencies"].append((rep, dep))

        #Step 2: loop through ccprocessed dependencies and grab anything that 
        #I didn't get through the coreference technique. 
        if u'sentences' in data:
            for sentence in data[u'sentences']:
                for dep in data[u'sentences'][sentence][u'collapsed-ccprocessed-dependencies']:
                    if dep[1] in keywords or dep[2] in keywords:
                        if sentence not in sentence_data:
                            sentence_data[sentence] = {}
                            sentence_data[sentence][u"parse"] = data['sentences'][sentence][u"parse"]
                            sentence_data[sentence][u"tokens"] = data['sentences'][sentence][u"tokens"]
                            sentence_data[sentence][u"collapsed-ccprocessed-dependencies"] = []
                            if dep[1] in keywords:
                                sentence_data[sentence][u"collapsed-ccprocessed-dependencies"].append((dep[1],dep))
                            elif dep[2] in keywords:
                                sentence_data[sentence][u"collapsed-ccprocessed-dependencies"].append((dep[2],dep))
                            continue
                        cc = sentence_data[sentence][u"collapsed-ccprocessed-dependencies"]
                        cc_list = [i[1] for i in cc]
                        if dep not in cc_list:
                            if dep[1] in keywords:
                                sentence_data[sentence][u"collapsed-ccprocessed-dependencies"].append((dep[1],dep))
                            elif dep[2] in keywords:
                                sentence_data[sentence][u"collapsed-ccprocessed-dependencies"].append((dep[2],dep))
            if sentence_data != {}:
                article_data[filename[:len(filename)-5]] = sentence_data
            
    #Step 3: Replace words in tuples with lemmas and 
    #throw out the rest of the data
    article_data_stripped = {}
    for article_key, article_value in article_data.iteritems():
        article_data_stripped[article_key] = {}
        for sentence_key, sentence_value in article_value.iteritems():
            sentence_id = sentence_key[12:]
            article_data_stripped[article_key][sentence_id] = {}
            article_data_stripped[article_key][sentence_id][u'collapsed-ccprocessed-dependencies'] = []
            article_data_stripped[article_key][sentence_id][u'parse'] = sentence_value[u'parse']
            cc = sentence_value[u'collapsed-ccprocessed-dependencies']
            for cc_item in cc:
                #designate an actor
                cc_list = cc_item[1]
                if cc_list[1] in keywords:
                    actor = cc_list[1]
                elif cc_list[1] in keywords:
                    actor = cc_list[2]
                else:
                    actor = cc_item[0]
                #replace non-actor words with lemmas
                for token_key, token_value in sentence_value[u'tokens'].iteritems():
                    if cc_list[1] == token_value[u'word']:
                        cc_list[1] = token_value[u'lemma']
                    if cc_list[2] == token_value[u'word']:
                        cc_list[2] = token_value[u'lemma']
                article_data_stripped[article_key][sentence_id][u'collapsed-ccprocessed-dependencies'].append((actor, cc_list))
            
    return article_data_stripped

def write_tuples(year, article_data_stripped):
    """
    input:
        article_data_stripped: dictionary
        year: int
    returns:
        writes file with meta_data from other processed
        files and article_data_stripped
    """

    #Create file with data with the following columns:
    #[docid, sentence_id, actor, tuple, sentence_parse]
    output_path = "/Volumes/data/modified_data/" + year + "/final_data/"
    if not os.path.exists(output_path):
        os.makedirs(output_path)   

    ofile = open(output_path + "tuples_v1.csv", "wb")
    writer = csv.writer(ofile, delimiter=',')

    #path of article meta data
    article_data_path = "/Volumes/data/modified_data/" + year + "/article_data/"
    writer.writerow(['document_id', 
    				'sentence_num', 
    				'actor', 
    				'tuple', 
    				'sentence_parse', 
    				'print_page_number', 
    				'publication_day_of_month',
    				'id-string',
    				'person',
    				'online_sections',
    				'dsk',
    				'publication_day_of_week',
    				'date.publication',
    				'print_section',
    				'name',
    				'publication_month',
    				'publication_year',
    				'item-length',
    				'print_column'])

    for article_key, article_value in article_data_stripped.iteritems():
        #grab article_data

        #bad way to grab article_data_name, but I think that I need to change earlier in process
        for data_name in os.listdir(article_data_path):
            if data_name[:5] == article_key[:5]:
                article_data_name = data_name
                break
        with open(article_data_path + article_data_name, 'rb') as file:
            article_data = json.load(file)
        meta_data = [article_data.get(u'print_page_number', ''), 
    				article_data.get(u'publication_day_of_month', ''),
    				article_data.get(u'id-string', ''),
    				article_data.get(u'person', ''),
    				article_data.get(u'online_sections', ''),
    				article_data.get(u'dsk', ''),
     				article_data.get(u'publication_day_of_week', ''),
     				article_data.get(u'date.publication', ''),
    	 			article_data.get(u'print_section', ''),
    	 			article_data.get(u'name', ''),
    	 			article_data.get(u'publication_month', ''),
    	 			article_data.get(u'publication_year', ''),
    	 			article_data.get(u'item-length', ''),
    	 			article_data.get(u'print_column', '')]
            
        for sentence_key, sentence_value in article_value.iteritems():
                line = [article_key, str(sentence_key)]
                try:
                    parse = str(sentence_value[u'parse'])
                except:
                    parse = ""
                for cc in sentence_value[u'collapsed-ccprocessed-dependencies']:
                    try: 
                        actor = str(cc[0])
                        dep_tuple = str(cc[1])
                        writer.writerow(line + [actor] + [dep_tuple] + [parse] + meta_data)
                    except:
                        continue
    ofile.close()


if __name__ == "__main__":
    #parse arguments to get year and keywords
    parser = argparse.ArgumentParser(description='Process year and a list of keywords')
    parser.add_argument('year', metavar='year', type=str, nargs=1,
                       help='a year string between 1987 and 2007')
    parser.add_argument('keywords', metavar='keywords', type=str, nargs='+',
                       help='A collection of keywords')

    args = parser.parse_args()
    year = args.year[0]
    keywords = args.keywords

    #make keywords into unicode
    uni_keywords = map(unicode, keywords)

    #grab data for tuples
    article_data = create_tuples(year, uni_keywords)
    #write data for tuples
    write_tuples(year, article_data)


