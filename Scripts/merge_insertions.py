#! /usr/bin/env python


import os
from subprocess import call


def overlap(start1, stop1, start2, stop2):
    """returns True if sets of coordinates overlap. Assumes coordinates are on same chromosome"""
    for y in xrange(start2, stop2+100):
        if start1 <= y <= stop1:
            return True
        else:
            pass


def create_master_dict(master, accession_name):
    with open(master, 'r') as masterfile:
        x = 0
        master_insertions = {}
        for line in masterfile:
            line = line.rsplit()
            if line[0] == 'ins_chr':
                pass
            else:
                master_insertions[x] = {'ins_chrom': line[0], 'ins_start': int(line[1]), 'ins_end': int(line[2]),
                                        'agi': line[6], 'ref_chrom': line[3], 'ident': line[7],
                                        'ref_start': int(line[4]), 'ref_end': int(line[5]), 'accessions': [accession_name]}
                x += 1
        return master_insertions


def merge_insertions(master_dict, ins_file, accession_name):
    with open(ins_file, 'r') as insertions:
        for line in insertions:
            line = line.rsplit()
            ins_chrom = line[0]
            if ins_chrom == 'ins_chr':
                pass
            else:
                ins_chrom = ins_chrom
                ins_start = int(line[1])
                ins_end = int(line[2])
                agi = line[6]
                ident = line[7]
                ref_chrom = line[3]
                ref_start = int(line[4])
                ref_end = int(line[5])
                i = len(master_dict)-1
                x = 0
                while x <= i:
                    # find out if there is another insertion the same in another accession: same insertion chromosome, same TE
                    if master_dict[x]['ins_chrom'] == ins_chrom and master_dict[x]['agi'] == agi and ref_chrom == master_dict[x]['ref_chrom'] and ref_start == master_dict[x]['ref_start']:
                        # does it overlap with the insertion coordinated for current accession
                        if overlap(master_dict[x]['ins_start'], master_dict[x]['ins_end'], ins_start, ins_end) is True:
                            # same insertion, append accession name to list for that insertion
                            master_dict[x]['accessions'].append(accession_name)
                            break
                            # refine insertion coordinates
                            if master_dict['ins_end'] > ins_start > master_dict['ins_start']:
                                master_dict['ins_start'] = ins_start
                            elif master_dict['ins_start'] < ins_end < master_dict['ins_end']:
                                master_dict['ins_end'] = ins_end
                            else:
                                pass
                        elif x == i:
                            master_dict[x+1] = {'ins_chrom': line[0], 'ins_start': int(line[1]), 'ins_end': int(line[2]),
                                        'agi': line[6], 'ref_chrom': line[3], 'ident': line[7],
                                        'ref_start': int(line[4]), 'ref_end': int(line[5]), 'accessions': [accession_name]}
                            break
                        else:
                            x += 1
                            pass
                    elif x == i:  # end of dictionary and still not found
                        master_dict[x+1] = {'ins_chrom': line[0], 'ins_start': int(line[1]), 'ins_end': int(line[2]),
                                        'agi': line[6], 'ref_chrom': line[3], 'ident': line[7],
                                        'ref_start': int(line[4]), 'ref_end': int(line[5]), 'accessions': [accession_name]}
                        break
                    else:
                        x += 1
                        pass


for dirs in os.listdir('.'):
    if os.path.isdir(dirs) is True:
        os.chdir(dirs)
        if os.path.isfile('insertions_{d}.bed'.format(d=dirs)) is True:
            print "processing {dirs}".format(dirs=dirs)
            try:
                master_insertions
            except NameError:
                master_insertions = create_master_dict('insertions_{d}.bed'.format(d=dirs), dirs)
            else:
                merge_insertions(master_insertions, 'insertions_{d}.bed'.format(d=dirs), dirs)
            os.chdir('..')
        else:
            os.chdir('..')
    else:
        pass


with open('insertions.bed', 'w+') as outfile:
    for key, value in master_insertions.iteritems():
        accessions = set(value['accessions'])  # removes duplicates
        outfile.write("""{ins_chrom}\t{ins_start}\t{ins_end}\t{ref_chrom}\t{ref_start}\t{ref_end}\t{agi}\t{accessions}\n""".format(ins_chrom=value['ins_chrom'],
                                                                                                                                         ins_start=value['ins_start'],
                                                                                                                                         ins_end=value['ins_end'],
                                                                                                                                         agi=value['agi'],
                                                                                                                                         ref_chrom=value['ref_chrom'],
                                                                                                                                         ref_start=value['ref_start'],
                                                                                                                                         ref_end=value['ref_end'],
                                                                                                                                         accessions=','.join(accessions)))

call("""awk 'BEGIN {FS=OFS="\t"} {print $1,$2,$3,$7,$8}' insertions.bed > insertions_poly_te.bed""", shell=True)
call("""awk 'BEGIN {FS=OFS="\t"} {print $4,$5,$6,$1,$2,$3}' insertions.bed > circos_all.txt""", shell=True)