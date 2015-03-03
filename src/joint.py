#coding=utf8
import sys
from subprocess import *
sys.path.append("./lib/")
sys.path.append("./module/")
import os
import ec
import coref
import sample
import time
import ltp
import BuildTree
from srilm import SRILm

def get_p_info(p):
    Mlist = ["他","他们"]
    Flist = ["她","她们"]
    sing = ["他","我","你","它","她","您","其"]
    comp = ["他们","我们","你们","它们","咱们","大家","她们"]
    ifl = []
    ifl.append("j_word:*%s*"%p)
    sex = "None"
    if p.strip("*") in Mlist:
        sex = "M" 
    elif p.strip("*") in Flist:
        sex = "F" 
    ifl.append("sex:%s"%sex)
    sc = "None"
    if p.strip("*") in sing:
        sc = "single"
    elif p.strip("*") in comp:
        sc = "complex"
    ifl.append("sc:%s"%sc)
    return " ".join(ifl)

def get_coref_sentence_for_joint(raw_sentence,ec_sentence,coref_info):
    index_dict = {}
    index = 0
    pure_index = 0
    words = raw_sentence.split(" ")
    for word in words:
        if word.startswith("*"):
            index_dict[pure_index+0.1] = index
        else:
            index_dict[pure_index] = index
            pure_index += 1
        index += 1
    index = 0
    pure_index = 0
    words = ec_sentence.split(" ")
    change_index_dict = {}
    for word in words:
        if word.startswith("*"):
            if index_dict.has_key(pure_index+0.1):
                change_index_dict[index_dict[pure_index+0.1]] = index
        else:
            if index_dict.has_key(pure_index):
                change_index_dict[index_dict[pure_index]] = index
            pure_index += 1
        index += 1
    line = coref_info.split("\t")
    out = []
    if len(line) > 1:
        for i in range(len(line)/3):
            flag = line[i*3]
            index = int(line[i*3+1]) - 1
            ec = line[i*3+2] 
            if index in change_index_dict:
                real_index = change_index_dict[index]+1 
                out.append(str(flag))
                out.append(str(real_index))
                out.append(str(ec))
                words[real_index-1] = ec
        ec_sentence = " ".join(words)
        if len(out) == 0:
            return ("None",ec_sentence)
        return ("\t".join(out),ec_sentence)
    else:
        return ("None",ec_sentence)
def joint(CMD_PATH):
    trans_set = set()
    f = open("./dict/trans.word")
    while True:
        line = f.readline()
        if not line:break
        line = line.strip()
        trans_set.add(line)
    ec_right_result = open("./result/ec.result.st","w")
    coref_right_result = open("./result/coref.result.st","w")
    ec_result = open("./result/ec.result","w")
    coref_result = open("./result/coref.result","w")
    joint_ec_result = open("./result/ec.result.joint","w")
    joint_coref_result = open("./result/coref.result.joint","w")
    ecType_result = open("./result/ecType.st","w")

    lm = SRILm(open("./dict/model.srilm", "r"))
    scir = ltp.LTP()
    candidate_list = []
    maxNum = 3
    n = 1
    word_num = 1
    ln = 1
    pronouns_last = []
    while True:
        line = sys.stdin.readline()
        if not line:break
        line = line.strip()
        print >> sys.stderr, "%d %s"%(ln,line)
        ln += 1
        raw_line = []
        inside_index = 0
        index = 0
        pro_list = []
        ec_right_result_list = []
        ec_result_list = []
        pro = "0"
        ec_num = 0
        for word in line.strip().split(" "):
            if word.find("*") >= 0:
                pro_list.append(inside_index)
                pro = word
            else:
                raw_line.append(word)
                inside_index += 1
                ec_right_result_list.append(pro.strip("*"))
                pro = "0"
            index += 1

        raw_sentence = " ".join(raw_line)
        if len(raw_sentence) < 2:
            line = sys.stdin.readline()
            continue
        info_dict = scir.get_info(raw_sentence)
        node_list = BuildTree.build_tree(info_dict)
        ec_dict = {} 
        feature_list,tmp_pro = ec.getFeature(ec_dict,node_list,trans_set,pronouns_last)
        pronouns_last = list(tmp_pro)
        fw = open("./tmp_data/feature.ec","w")
        for feature in feature_list:
            fv = str(word_num) + "\t" + feature[0] + "\t" + " ".join(feature[1:])
            fw.write(fv+"\n")
            word_num += 1
        fw.close()
        cmd = "%s/go_max_ec.sh %s/conf.sh"%(CMD_PATH,CMD_PATH) 
        os.system(cmd)
        pro_dict = {}
        f_ec = open("./tmp_data/result.ec")
        real_index = 0
        ec_joint_result_list = []
        result_for_ec_recover = []        
        while True:
            ec_info = f_ec.readline()
            if not ec_info:break 
            ec_info = ec_info.strip().split("\t")
            rf = 0.0 
            rt = ""
            pro_dict.setdefault(real_index,{})
            for i in range(1,len(ec_info)/2+1):
                type_freq = {}
                pro_type = ec_info[i*2-1].split(":")[-1].strip("*")
                freq  = float(ec_info[i*2])
                if freq > rf: 
                    rt = pro_type
                    rf = freq
                if not pro_type == "0":
                    pro_dict[real_index][pro_type] = freq
            if rt == "0":
                if rf >= 0.5:
                    result_for_ec_recover.append(rt)
                else:
                    result_for_ec_recover.append("*ec*")
                    ec_num += 1
            else:
                result_for_ec_recover.append("*ec*")
                ec_num += 1
            ec_result_list.append(rt)
            ec_joint_result_list.append(rt)
            real_index += 1
        f_ec.close()

        ec_sentence_list = []
        words = raw_sentence.strip().split(" ")    
        for i in range(len(words)):
            if not result_for_ec_recover[i] == "0":
                ec_sentence_list.append(result_for_ec_recover[i]) 
            ec_sentence_list.append(words[i])
        ec_sentence = " ".join(ec_sentence_list)
        raw_sentence = line.strip() 
        line = sys.stdin.readline().strip()        
        coref_info_raw = line
        coref_info,ec_sentence = get_coref_sentence_for_joint(raw_sentence,ec_sentence,coref_info_raw)
        pro_list = []
        inside_index = 0
        for word in ec_sentence.split(" "):
            if word.find("*") >= 0:
                pro_list.append(inside_index)
            else:
                inside_index += 1
        info_dict = scir.get_info(ec_sentence)
        node_list = BuildTree.build_tree(info_dict) 
        line = coref_info.strip()
        coref_dict = {}
        line = line.split("\t")
        if len(line) > 1:
            for i in range(len(line)/3):
                flag = line[i*3]
                index = int(line[i*3+1]) - 1
                coref_dict[index] = flag
        nn_list = coref.get_node_info(node_list,coref_dict) 
        candidate_list.append(nn_list)
        if len(candidate_list) > maxNum:
            candidate_list = candidate_list[1:]
        feature_list = coref.getFeature(coref_dict,node_list,candidate_list,lm)           
        coref_num = len(feature_list)
        if len(pro_list) == 0:
            continue
        corefEachEc = coref_num/ec_num
        word_num = 1
        freq_list = []
        pro_result_list = []
        coref_right_result_list = []
        ecType_for_coref = []
        fw = open("./tmp_data/feature.coref","w")
        ec_index = 0
        ec_times = 0
        index = 0
        for feature in feature_list:
            fv = str(word_num) + "\t" + feature[0] + "\t" + " ".join(feature[1:])
            result = feature[0].split(":")[1]
            pro_position = pro_list[ec_index]
            if not pro_dict.has_key(pro_position):
                continue
            pro_info = pro_dict[pro_position]

            pronoun = feature[-3].split(":")[1].strip("*")
            for pro_type in pro_info.keys():
                freq_list.append(pro_info[pro_type])
                pro_result_list.append(pro_type)
                if not pro_type == pronoun:
                    new_info = get_p_info(pro_type)
                    fv =str(word_num) + "\t" + feature[0] + "\t" + " ".join(feature[1:-3]) + " " + new_info 
                    coref_right_result_list.append("0")
                else:
                    coref_right_result_list.append(result)
                ecType_for_coref.append(pronoun)
                fw.write(fv+"\n") 
            ec_times += 1
            if ec_times == corefEachEc:
                change_ec_index = ec_index
                ec_times = 0
                ec_index += 1
                fw.close()
                cmd = "%s/go_max_coref.sh %s/conf.sh"%(CMD_PATH,CMD_PATH)      
                os.system(cmd)
                f_coref = open("./tmp_data/result.coref")
                f_svm = open("./tmp_data/feature.svm","w")
                coref_result_list = []
                coref_joint_result_list = []
                coref_result_index = -1
                now_index = 0
                coref_result_freq = 0.0
                while True:
                    coref_result_line = f_coref.readline()
                    if not coref_result_line:
                        break
                    coref_freq = float(coref_result_line.strip().split("\t")[4])
                    coref_result_list.append("0")
                    coref_joint_result_list.append("0")
                    if coref_freq >= 0.5 and coref_freq > coref_result_freq:
                        coref_result_freq = coref_freq
                        coref_result_index = now_index
                    f_svm.write("%s 1:%f 2:%f\n"%(coref_right_result_list[index],float(freq_list[index]),coref_freq)) 
                    index += 1
                    now_index += 1
                f_svm.close()
                if coref_result_index >= 0:
                    coref_result_list[coref_result_index] = "1"
                for coref_result_item in coref_result_list:
                    coref_result.write(coref_result_item+"\n")
                cmd = "%s/start_svm.sh %s/conf.sh > ./tmp_data/t"%(CMD_PATH,CMD_PATH)      
                os.system(cmd)
                fr = open("./tmp_data/result.svm")
                fr.readline()
                coref_joint_result_index = -1
                now_index = 0
                coref_joint_result_freq = 0.0
                while True:
                    j = fr.readline()
                    if not j:break
                    point = float(j.strip().split(" ")[2])
                    if point > coref_joint_result_freq and point >= 0.5:
                        coref_joint_result_index = now_index
                        coref_joint_result_freq = point
                    now_index += 1
                if coref_joint_result_index >= 0:
                    coref_joint_result_list[coref_joint_result_index] = "1" 
                    ec_joint_result_list[change_ec_index] = pro_result_list[coref_joint_result_index] 
                for coref_joint_result_item in coref_joint_result_list:
                    joint_coref_result.write(coref_joint_result_item+"\n")
                fw = open("./tmp_data/feature.coref","w")
                pro_result_list = [] 
            word_num += 1
        fw.close()
        for result in coref_right_result_list:
            coref_right_result.write(result+"\n")
        for ecType in ecType_for_coref:
            ecType_result.write(ecType.strip()+"\n")
        for ecs in ec_joint_result_list: 
            joint_ec_result.write(ecs+"\n") 
        for ecs in ec_right_result_list:
            ec_right_result.write(ecs+"\n")
        for ecs in ec_result_list:
            ec_result.write(ecs+"\n")
if __name__ == "__main__":
    config = open("./conf")
    conf = {}
    while True:
        line = config.readline()
        if not line:break
        line = line.strip().split("=") 
        conf[line[0]] = line[1]
    joint(conf["CMD_PATH"])


