import argparse


def main(args):
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--image", required=True, help="Path to input image")
    parsed_args, unparsed_args = parser.parse_known_args()
    main(parsed_args)
