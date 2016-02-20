from model import Genome, Feature, GOTerm, Pathway, EnzymeCode, initialize, make_session
import csv


def opener(obj):
    if hasattr(obj, 'read'):
        return obj
    else:
        return open(obj, 'rb')


def safesplit(string, token=';'):
    try:
        acc = []
        while True:
            position = string.index(token)
            pre, sep, suf = string.partition(token)
            if string[position - 1] == "\\":
                acc.extend((pre, sep))
                string = suf
            else:
                pre, sep, suf = string.partition(token)
                acc.append(pre)
                yield ''.join(acc)
                acc = []
                string = suf
    except ValueError:
        pass

    if len(acc) != 0 or string != '':
        acc.append(string)
        yield ''.join(acc)


def parse_go(gostring, feature):
    for token in safesplit(gostring):
        if token == '':
            continue
        id, description = token.split("|")
        yield GOTerm(go_id=id, description=description, feature_id=feature.patric_id)


def parse_pathway(pathwaystring, feature):
    for token in safesplit(pathwaystring):
        if token == '':
            continue
        id, description = token.split("|")
        yield Pathway(pathway_id=id, description=description, feature_id=feature.patric_id)


def parse_ec(ecstring, feature):
    for token in safesplit(ecstring):
        if token == '':
            continue
        id, description = token.split("|")
        yield EnzymeCode(enzyme_id=id, description=description, feature_id=feature.patric_id)


def load_features(database_path, source_tsv):
    with opener(source_tsv) as handle:
        reader = csv.DictReader(handle, delimiter='\t')

        # Track parser state, since features are sorted by genome
        current_genome_accession = None
        current_genome = None

        # Connect to the database
        session = make_session(database_path)

        # These headers describe the genome, not relevant for features
        genome_headers = ["genome_id", "genome_name"]

        i = 0
        for line in reader:
            if line['accession'] != current_genome_accession:
                current_genome = Genome(
                    genome_id=line['genome_id'], accession=line['accession'], genome_name=line['genome_name'])
                session.add(current_genome)
                current_genome_accession = current_genome.accession

            if line["feature_type"] == "source":
                continue

            for field in genome_headers:
                line.pop(field)

            go_terms = line.pop("go")
            pathways = line.pop("pathway")
            enzymes = line.pop("ec")

            new_feature = Feature(**line)
            session.add(new_feature)

            session.add_all(parse_go(go_terms, new_feature))
            session.add_all(parse_pathway(pathways, new_feature))
            session.add_all(parse_ec(enzymes, new_feature))

            if i % 1000 == 0:
                print("Loaded the %dth feature, " % i)
                session.commit()
            i += 1
        session.commit()


def main(database_path, source_tsv):
    initialize(database_path)
    load_features(database_path, source_tsv)

if __name__ == '__main__':
    import sys
    main(sys.argv[1], sys.argv[2])
