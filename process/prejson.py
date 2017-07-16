"""
Preprocess json file before json2csv or json2json

"""
import sys
import getopt
import codecs

if __name__ == "__main__":
    inputfile = ''
    output_dir = 'output'
    # Read command options
    try:
        options, args = getopt.getopt(sys.argv[1:], "hi:o:", ["ifile=", "odir="])
    except getopt.GetoptError:
        print('json2csv2.py -i <inputfile> - o <outputdir>')
        sys.exit(2)
    for opt, arg in options:
        if opt == '-h':
            print('json2csv2.py -i <inputfile> - o <outputdir>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--odir"):
            output_dir = arg
    if inputfile == '':
        print('No input file provided')
        sys.exit(2)

    outputfile = inputfile + '.pre'
    output_f = open(output_dir + '/' + outputfile, 'wb')
    with codecs.open(inputfile, 'r', encoding='utf-8', errors='replace') as fd:
        for line in fd:
            # Replace {"metadata": with \n{"metadata":
            newline = line.replace('{"metadata":', '\n{"metadata":')
            # newline = codecs.encode(newline, encoding='utf-8')
            # newline = newline.replace(u'\ufffd', '#')
            # print(newline)
            output_f.write(newline.encode('utf-8', errors='replace'))
            # output_f.truncate(output_f.tell()-1)


