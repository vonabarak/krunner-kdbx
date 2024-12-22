import argparse

from .runner import Runner

def main():
	parser = argparse.ArgumentParser(prog="krunner_kdbx", description="krunner plugin for querying KeepassXC database files")
	subparsers = parser.add_subparsers(dest="command")
	helper = subparsers.add_parser("helper", help="run helper for password input")
	helper.add_argument("-g", "--gui", help="use GUI", action="store_true", dest="gui")
	args = parser.parse_args()

	if args.command == "helper":
		from krunner_kdbx.helper import open_db
		open_db(gui=args.gui)
		return

	runner = Runner()
	runner.start()

if __name__ == '__main__':
	main()
