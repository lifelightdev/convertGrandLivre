import argparse
from extract_file import extract_file


def main(name):
    # python - m main --file 'Grand_livre de test.pdf'
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--file", action="store", required=True, help="Saisir le nom du fichier du grand livre")
    args = parser.parse_args()
    file = extract_file(args.file)

if __name__ == '__main__':
    main()
