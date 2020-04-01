import sys
import math
import matplotlib.pyplot as plt
from collections import defaultdict

class Doc:
  def __init__(self, docno, relevance):
    self.docno = docno
    self.relevance = relevance

precision_map, recall_map, f1_map = {}, {}, {}

def retrieve_qrel(qrel):
    qrel_dict = defaultdict(dict)
    with open(qrel, 'r') as file:
        line = file.readline()
        while line:
            list = line.split()
            queryno, docno, relevance = int(list[0]), list[2], int(list[3])
            doc = Doc(docno, relevance)
            if relevance != 0:
                if queryno not in qrel_dict:
                    qrel_dict[queryno] = [doc]
                else:
                    qrel_dict[queryno].append(doc)
            line = file.readline()
    return qrel_dict

def retrieve_results(results):
    results_dict = defaultdict(dict)
    with open(results, 'r') as file:
        line = file.readline()
        while line:
            list = line.split()
            queryno, docno, rank = int(list[0]), list[2], int(list[3])
            if queryno not in results_dict:
                results_dict[queryno] = [(docno, rank)]
            else:
                results_dict[queryno].append((docno, rank))
            line = file.readline()
    return results_dict

def calculate_dcg(relevance_list):
    dcg = 0
    for i, relevance in enumerate(relevance_list):
        if i == 0:
            dcg += relevance
        else:
            dcg += relevance / math.log(1.0 + i)
    return dcg

def print_by_k(precision_by_k, recall_by_k, f1_by_k):
    global precision_map, recall_map, f1_map
    for k, precision in precision_by_k.items():
        precision_map[k].append(precision)
        print('precision @{}: {:.4f}'.format(k, precision))
    for k, tuple in recall_by_k.items():
        recall, matched, out_of = tuple[0], tuple[1], tuple[2]
        recall_map[k].append(recall)
        print('recall @{}: {:.4f} / {} out of {}'.format(k, recall, matched, out_of))
    for k, f1 in f1_by_k.items():
        f1_map[k].append(f1)
        print('f1 @{}: {:.4f}'.format(k, f1))


def trec_eval(qrel, results):
    global precision_map, recall_map, f1_map
    k_list = [5, 10, 20, 50, 100, 1000]

    for k in k_list:
        precision_map[k], recall_map[k], f1_map[k] = [], [], []
    avg_precision_map, r_precision_map, nDCG_map = {}, {}, []

    for queryno, docs in results.items():
        docno_relevance_map, relevance_list = {}, []
        precision_by_k, recall_by_k, f1_by_k = {}, {}, {}

        for doc in qrel[queryno]:
            docno_relevance_map[doc.docno] = doc.relevance

        qrel_docs = [doc.docno for doc in qrel[queryno]]
        relevance_sum = sum([doc.relevance for doc in qrel[queryno]])
        k, psum, relevant_num, relevant_docs = 0, 0, 0, len(qrel_docs)

        print('------ queryno:', queryno, '------')
        list = [res for res in results[queryno] if res[0] in qrel_docs and int(res[1]) < relevance_sum]
        r_vector_sum = sum([int(docno_relevance_map[item[0]]) for item in list])

        ## R PRECISION ##
        r_precision = r_vector_sum / relevance_sum

        for doc in docs:
            k += 1
            if doc[0] in qrel_docs:
                precision = int(docno_relevance_map[doc[0]]) * (1 + relevant_num) / k
                psum += precision
                relevant_num += int(docno_relevance_map[doc[0]])
                value = docno_relevance_map[doc[0]]
                relevance_list.append(value)
            else:
                relevance_list.append(0)
            if k in k_list and relevant_num > 0:
                ## PRECISION @ k ##
                precision = relevant_num / k
                precision_by_k[k] = precision
                ## RECALL @ k ##
                recall = relevant_num / relevant_docs
                recall_by_k[k] = (recall, relevant_num, relevant_docs)
                ## F1 @ k ##
                f1 = (2 * precision * recall) / (precision + recall)
                f1_by_k[k] = f1
        print_by_k(precision_by_k, recall_by_k, f1_by_k)

        ## nDCG ##
        dcg = calculate_dcg(relevance_list)
        relevance_list.sort(reverse=True)
        sorted_dcg = calculate_dcg(relevance_list)
        ndcg = dcg / sorted_dcg

        ## AVG PRECISION ##
        avg_precision = psum / relevance_sum

        print('nDCG: {:.4f} where DCG: {:.4f} and sorted_DCG: {:.4f}'.format(ndcg, dcg, sorted_dcg))
        print('Avg-Precision: {:.4f}'.format(avg_precision), 'psum & relevant docs', psum, relevance_sum, relevant_num)
        print('R-Precision: {:.4f}'.format(r_precision), 'list_len & relevant docs', r_vector_sum, relevance_sum)

        nDCG_map.append(ndcg)
        avg_precision_map[queryno] = float(avg_precision)
        r_precision_map[queryno] = float(r_precision)

    print('------ total # of queries:', len(results), '------')
    for k in k_list:
        print('avg precision @{}: {:.4f}'.format(k, sum(precision_map[k]) / len(results)))
    for k in k_list:
        print('avg recall @{}: {:.4f}'.format(k, sum(recall_map[k]) / len(results)))
    for k in k_list:
        print('avg f1 @{}: {:.4f}'.format(k, sum(f1_map[k]) / len(results)))
    print('total avg-nDCG: {:.4f}'.format(sum(nDCG_map) / len(results)))
    print('total avg-precision: {:.4f}'.format(sum(avg_precision_map.values()) / len(results)))
    print('total r-precision: {:.4f}'.format(sum(r_precision_map.values()) / len(results)))

def precision_recall_plot(precision_map, recall_map):
    q1_precisions = [item[0] for item in precision_map.values()]
    q1_recalls = [item[0] for item in recall_map.values()]
    plt.plot([1, 2, 3, 4], [1, 4, 9, 16])

def main():
    arg = list(sys.argv)
    qrel, results = retrieve_qrel(arg[1]), retrieve_results(arg[2])
    trec_eval(qrel, results)
    precision_recall_plot(precision_map, recall_map)

main()