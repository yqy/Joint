#coding=utf8
import sys
import ltp
sys.path.append("./lib/")
from srilm import SRILm
import BuildTree
import sample

def get_node_info(node_list,coref_dict):
    nn_list = []
    for node_item in node_list:
        if not node_item.word == None:
            if node_item.tag.find("n") >= 0: #candidate
                head_path = "None"
                head_index = int(node_item.head)
                if head_index >= 0:
                    hp = []
                    head_father = node_list[head_index].parent 
                    father = node_item
                    while not father == head_father:
                        hp.append(father.tag)
                        father = father.parent
                    hp.append(head_father.tag)
                    hp.append(node_list[head_index].tag)
                    head_path = "_".join(hp)
                root_path = "None" 
                rp = []
                find_times = 0
                father = node_item
                while not father.tag == "ROOT":
                    rp.append(father.tag)
                    father = father.parent
                rp.append(father.tag)
                root_path = "_".join(rp)
                nn_list.append((coref_dict,node_item,head_path,root_path))
    return nn_list
                
def getFeature(coref_dict,node_list,candidate_list,lm):
    fl = []           
    Mlist = ["他","他们"]
    Flist = ["她","她们"]
    sing = ["他","我","你","它","她","您","其"]
    comp = ["他们","我们","你们","它们","咱们","大家","她们"]

    for node_item in node_list:
        if node_item.word is None:
            continue
        if node_item.word.find("*") >= 0:    
            np_tag = ""
            if coref_dict.has_key(int(node_item.index)):
                np_tag = coref_dict[int(node_item.index)]
            head_path = "None"
            head_index = int(node_item.head)
            if head_index >= 0:
                hp = []
                head_father = node_list[head_index].parent 
                father = node_item
                while not father == head_father:
                    hp.append(father.tag)
                    father = father.parent
                hp.append(head_father.tag)
                hp.append(node_list[head_index].tag)
                head_path = "_".join(hp)
            root_path = "None" 
            rp = []
            father = node_item
            while not father.tag == "ROOT":
                rp.append(father.tag)
                father = father.parent
            rp.append(father.tag)
            root_path = "_".join(rp)
            for nn_list in candidate_list:
                for (i_coref_dict,i_node_item,i_head_path,i_root_path) in nn_list:
                    ifl = []
                                        
                    i_index = int(i_node_item.index)
                    coref = "0"
                    if i_coref_dict.has_key(i_index):
                        if not np_tag == "":
                            if i_coref_dict[i_index] == np_tag:
                                coref = "1"
                    ifl.append("coref:%s"%coref)
                    ifl.append("i_word:%s"%i_node_item.word)
                    i_pos = i_node_item.tag
                    ifl.append("i_pos:%s"%i_pos)
                    i_ner = i_node_item.ner
                    ifl.append("i_ner:%s"%i_ner)
                    i_gram = i_node_item.parent.tag 
                    ifl.append("i_gram:%s"%i_gram)
                    ifl.append("i_head_path:%s"%i_head_path)
                    ifl.append("i_root_path:%s"%i_root_path)
                
                    j_pos = node_item.tag
                    ifl.append("j_pos:%s"%j_pos)
                    j_ner = node_item.ner
                    ifl.append("j_ner:%s"%j_ner)
                    j_gram = node_item.parent.tag 
                    ifl.append("j_gram:%s"%j_gram)
                    ifl.append("j_head_path:%s"%head_path)
                    ifl.append("j_root_path:%s"%root_path)
                    
                    index = int(node_item.index)
                    score = 0.0
                    if index >= 1:
                        pre_word = node_list[index-1].word
                        score = lm.sentence_probability("%s %s"%(i_node_item.word,pre_word))
                    ifl.append("score:%f"%score)

                    ifl.append("j_word:%s"%node_item.word)
                    
                    sex = "None"
                    if node_item.word.strip("*") in Mlist:
                        sex = "M"
                    elif node_item.word.strip("*") in Flist:
                        sex = "F"
                    ifl.append("sex:%s"%sex)
                    
                    sc = "None"
                    if node_item.word.strip("*") in sing:
                        sc = "single"
                    elif node_item.word.strip("*") in comp:
                        sc = "complex"
                    ifl.append("sc:%s"%sc)
                    fl.append(ifl)
    return fl
