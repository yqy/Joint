#coding=utf8
import sys
import ltp
sys.path.append("./lib/")
from srilm import SRILm
import BuildTree
import sample
                
def getFeature(ec_dict,node_list,trans_set,pronouns_last):
    fl = []           
    nearset_pronoun = "None"
    pronoun_set = set()
    pronoun_list = ["你","你们","我","我们","它","它们","他","他们","她","她们"]
    for node_item in node_list:
        if not node_item.word is None:
            ifl = []
            is_ec = "0"
            index = int(node_item.index)
            if ec_dict.has_key(index):
                is_ec = ec_dict[index]
            if not is_ec == "0":
                pronoun_set.add(is_ec)
            ifl.append("is_ec:%s"%is_ec)
            word_t = node_item.word 
            ifl.append("word_t:%s"%word_t)
            pos_t = node_item.tag
            ifl.append("pos_t:%s"%pos_t)
            gram_t = node_item.parent.tag 
            ifl.append("gram_t:%s"%gram_t)

            head_index = int(node_item.head)
            word_h = "None"
            pos_h = "None"
            gram_h = "None"
            if head_index >= 0:
                head_item = node_list[head_index]
                word_h = head_item.word
                pos_h = head_item.tag
                gram_h = head_item.parent.tag
            ifl.append("word_h:%s"%word_h) 
            ifl.append("pos_h:%s"%pos_h) 
            ifl.append("gram_h:%s"%gram_h) 
            
            pre_index = int(node_item.index - 1)
            word_p = "None"
            pos_p = "None"
            gram_p = "None"
            if pre_index >= 0:
                pre_item = node_list[pre_index]
                word_p = pre_item.word
                pos_p = pre_item.tag
                gram_p = pre_item.parent.tag
            ifl.append("word_p:%s"%word_p) 
            ifl.append("pos_p:%s"%pos_p) 
            ifl.append("gram_p:%s"%gram_p) 
            
            pos_h_t = "%s_%s"%(pos_h,pos_t)
            ifl.append("pos_h_t:%s"%pos_h_t)
            pos_t_p = "%s_%s"%(pos_t,pos_p)
            ifl.append("pos_t_p:%s"%pos_t_p)
            
            word_distance = 0
            if head_index >= 0:
                word_distance = index - head_index
            ifl.append("word_distance:%s"%word_distance)
            
            normalized_distance = "same"
            if head_index >= 0: 
                if word_distance == 1:
                    normalized_distance = "imme_after"
                elif word_distance == -1: 
                    normalized_distance = "imme_before"
                elif word_distance > 1 and word_distance < 5:
                    normalized_distance = "near_after"
                elif word_distance < -1 and word_distance > -5: 
                    normalized_distance = "near_before"
                else:
                    normalized_distance = "other"
            ifl.append("normalized_distance:%s"%normalized_distance)

            verb_distance = 0
            if head_index >= 0:
                for i in range(head_index+1,index):
                    if node_list[i].tag == "v":
                        verb_distance += 1
                for i in range(index+1,head_index):
                    if node_list[i].tag == "v":
                        verb_distance += 1
            ifl.append("verb_distance:%d"%verb_distance)

            comma_distance = 0
            if head_index >= 0:
                for i in range(head_index+1,index):
                    if node_list[i].word == "，" or node_list[i].word == ",":
                        comma_distance += 1
                for i in range(index+1,head_index):
                    if node_list[i].word == "，" or node_list[i].word == ",":
                        comma_distance += 1
            ifl.append("comma_distance:%d"%comma_distance)

            is_trans = "other"
            if pre_index >= 0:
                if node_list[pre_index].tag == "v":
                    is_trans = "no"
                    if node_list[pre_index].word in trans_set:
                        is_trans = "yes"
            ifl.append("is_trans:%s"%is_trans)

            is_verb_head = "0"
            if head_index >= 0:
                if node_list[head_index].tag == "v":
                    is_verb_head = "1"
            ifl.append("is_verb_head:%s"%is_verb_head)

            head_path = "None"
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
            ifl.append("head_path:%s"%head_path)
            root_path = "None" 
            rp = []
            father = node_item
            while not father.tag == "ROOT":
                rp.append(father.tag)
                father = father.parent
            rp.append(father.tag)
            root_path = "_".join(rp)
            ifl.append("root_path:%s"%root_path)
            ifl.append("nearset_pronoun:%s"%nearset_pronoun) 
            if node_item.word in pronoun_list:
                nearset_pronoun = node_item.word
            ifl.append("pronouns:%s"%("_".join(pronouns_last)))
            fl.append(ifl)
    return fl,pronoun_set
