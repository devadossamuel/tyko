import os
import argparse

def locate_ini_file(root):
    def filter_alebmic_ini(entry: os.DirEntry) -> bool:

        if not entry.is_file():
            return False

        if entry.name != "alembic.ini":
            return False

        return True

    return next(filter(filter_alebmic_ini, os.scandir(root))).path


def create_edited(ini_file, sqlalchemy_url) -> str:
    new_doc_lines = []
    with open(ini_file, "r") as f:
        for line in f:
            if "sqlalchemy.url" in line:
                new_doc_lines.append("sqlalchemy.url = {}".format(sqlalchemy_url))
            else:
                new_doc_lines.append(line.strip())
    return "\n".join(new_doc_lines)


def main():
    parser = argparse.ArgumentParser(description='configure alembic.ini.')
    parser.add_argument("sqlalchemy_url")
    args = parser.parse_args()

    ini_file = locate_ini_file(root=os.path.dirname(__file__))
    new_data = create_edited(ini_file=ini_file,
                             sqlalchemy_url=args.sqlalchemy_url)
    print(new_data, end="")
#     todo write data this out to a filename


if __name__ == '__main__':
    main()
    