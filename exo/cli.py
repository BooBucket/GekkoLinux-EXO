# entry point for CLI
import argparse

def main():
	parser = argparse.ArgumentParser(
		prog="EXO - Gekko Linux Package Assembler",
		description="Gekko's package manager",
		epilog="Why be mean when you can be nice?"
	)

	command_subparser = parser.add_subparsers(dest="command", help="The command to run.", required=True)

	command_subparser.add_parser("install", aliases=["i"], help="Install a package")
	command_subparser.add_parser("delete", aliases=["d"], help="Delete/remove a package")
	command_subparser.add_parser("refresh", aliases=["r"], help="Update installed packages")
	command_subparser.add_parser("list", aliases=["l"], help="List all installed packages")


	parser.parse_args()

if __name__ == "__main__":
	main()
