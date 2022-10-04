from .ui import *
from .service import *
from .repository import *
import argparse


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dbinit")
    args = parser.parse_args()
    dbinit = args.dbinit

    if dbinit != "True" and dbinit != "False":
        raise "Invalid argument! Please try again."

    if dbinit == "True":
        dbinit = True
    elif dbinit == "False":
        dbinit = False

    return dbinit


if __name__ == "__main__":
    di["db_file"] = r"./immerverloren"
    dbinit = get_parser()
    ui = BoxUI()

    ui.run(dbinit)
