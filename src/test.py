from collections import Counter
import csv
import spacy
from pathlib import Path


def load_entities():
    # distributed alongside this notebook
    entities_loc = Path.cwd() / "TestData"/"entities.csv"

    names = dict()
    descriptions = dict()
    with entities_loc.open("r", encoding="utf8") as csvfile:
        csvreader = csv.reader(csvfile, delimiter=",")
        for row in csvreader:
            qid = row[0]
            name = row[1]
            desc = row[2]
            names[qid] = name
            descriptions[qid] = desc
    return names, descriptions


def createDB():
    name_dict, desc_dict = load_entities()
    for QID in name_dict.keys():
        print(f"{QID}, name={name_dict[QID]}, desc={desc_dict[QID]}")

    from spacy.kb import KnowledgeBase, Candidate
    nlp = spacy.load("en_core_web_md")
    # 定義KnowledgeBase容器
    # 每個實體設定 300D的 entity_vecto長度
    kb = KnowledgeBase(vocab=nlp.vocab, entity_vector_length=300)

    for qid, desc in desc_dict.items():
        desc_doc = nlp(desc)
        desc_enc = desc_doc.vector
        # 正常加入實體時要提供該單字出現的次數(freq)，本次demo隨便設定一個數字
        # We also need to provide a frequency, which is a raw count of how many times a certain entity appears in an annotated corpus
        kb.add_entity(entity=qid, entity_vector=desc_enc, freq=342)

    # 加入aliases，且在此假設當字串為全名時 100%機率指向該entity
    for qid, name in name_dict.items():
        kb.add_alias(alias=name, entities=[qid], probabilities=[1])

    qids = name_dict.keys()
    probs = [0.3 for qid in qids]
    # 若當字串只有Emerson (而非全名)時，我們假設三位Emerson都一樣有名，所以機率各是30%
    # sum([probs]) should be <= 1 !
    kb.add_alias(alias="Emerson", entities=qids, probabilities=probs)

    print(f"Entities in the KB: {kb.get_entity_strings()}")
    print(f"Aliases in the KB: {kb.get_alias_strings()}")

    print(
        f"Candidates for 'Roy Stanley Emerson': {[c.entity_ for c in kb.get_alias_candidates('Roy Stanley Emerson')]}")
    print(
        f"Candidates for 'Emerson': {[c.entity_ for c in kb.get_alias_candidates('Emerson')]}")
    print(
        f"Candidates for 'Sofie': {[c.entity_ for c in kb.get_alias_candidates('Sofie')]}")
    '''
    輸出:
    Q312545, name=Roy Stanley Emerson, desc=Australian tennis player
    Q48226, name=Ralph Waldo Emerson, desc=American philosopher, essayist, and poet
    Q215952, name=Emerson Ferreira da Rosa, desc=Brazilian footballer
    Entities in the KB: ['Q215952', 'Q312545', 'Q48226']
    Aliases in the KB: ['Roy Stanley Emerson', 'Emerson Ferreira da Rosa', 'Ralph Waldo Emerson', 'Emerson']
    Candidates for 'Roy Stanley Emerson': ['Q312545']
    Candidates for 'Emerson': ['Q312545', 'Q48226', 'Q215952']
    Candidates for 'Sofie': []
    '''
    return kb,qids

# 寫出訓練檔


def writeDB():
    import os
    output_dir = Path.cwd() / "TestData" / "my_output"
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    #kb.dump(output_dir / "my_kb")

    nlp.to_disk(output_dir / "my_nlp")


def train_el(kb,qids):
    import json
    from pathlib import Path

    dataset = []
    json_loc = Path.cwd() / "TestData" / "emerson_annotated_text.jsonl"
    with json_loc.open("r", encoding="utf8") as jsonfile:
        for line in jsonfile:
            example = json.loads(line)
            text = example["text"]
            if example["answer"] == "accept":
                QID = example["accept"][0]
                offset = (example["spans"][0]["start"],
                          example["spans"][0]["end"])
                links_dict = {QID: 1.0}
            # 返回格式
            dataset.append((text, {"links": {offset: links_dict}}))
    print(dataset[0])
    '''
    輸出
    ('Interestingly, Emerson is one of only five tennis players all-time to win multiple 
slam sets in two disciplines, only matched by Frank Sedgman, Margaret Court, Martina 
Navratilova and Serena Williams.', {'links': {(15, 22): {'Q312545': 1.0}}})
    '''
    
    #檢測該dataset已標記的資料筆數
    gold_ids = []
    for text, annot in dataset:
        for span, links_dict in annot["links"].items():
            for link, value in links_dict.items():
                if value:
                    gold_ids.append(link)

    print(Counter(gold_ids))
    
    #將8筆資料設為訓練集，2筆設為驗證集
    import random
    train_dataset = []
    test_dataset = []
    for QID in qids:
        indices = [i for i, j in enumerate(gold_ids) if j == QID]
        train_dataset.extend(dataset[index] for index in indices[0:8])  # first 8 in training
        test_dataset.extend(dataset[index] for index in indices[8:10])  # last 2 in test
        
    random.shuffle(train_dataset)
    random.shuffle(test_dataset)
    
    
    nlp = spacy.load("en_core_web_md")
    TRAIN_DOCS = []
    for text, annotation in train_dataset:
        doc = nlp(text)     # to make this more efficient, you can use nlp.pipe() just once for all the texts
        TRAIN_DOCS.append((doc, annotation))
    
    #加入 pipeline
    entity_linker = nlp.create_pipe("entity_linker", config={"incl_prior": False})
    entity_linker.set_kb(kb) # ERROR
    nlp.add_pipe(entity_linker, last=True)
    
    
    from spacy.util import minibatch, compounding
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "entity_linker"]
    with nlp.disable_pipes(*other_pipes):   # train only the entity_linker
        optimizer = nlp.begin_training()
        for itn in range(500):   # 500 iterations takes about a minute to train
            random.shuffle(TRAIN_DOCS)
            batches = minibatch(TRAIN_DOCS, size=compounding(4.0, 32.0, 1.001))  # increasing batch sizes
            losses = {}
            for batch in batches:
                texts, annotations = zip(*batch)
                nlp.update(
                    texts,  
                    annotations,   
                    drop=0.2,      # prevent overfitting
                    losses=losses,
                    sgd=optimizer,
                )
            #每50次iterations就print目前的losses
            if itn % 50 == 0:
                print(itn, "Losses", losses)   # print the training loss
    print(itn, "Losses", losses)
    
if(__name__ == "__main__"):
    kb, qid = createDB()
    # writeDB()
    
    train_el(kb,qid)
