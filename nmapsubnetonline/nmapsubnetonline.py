import argparse
import glob
import ipaddress
from loguru import logger
from os import path, makedirs
import signal
import sys

# Custom imports
from liblog.liblog import initLogger
from nmapstreamparser.nmapstreamparser import extract_hosts

FILELOGGER_PATH = "/var/log"
FILELOGGER = "nmapsubnetonline.log"
NMAP_EXTENSION = ".xml"  # Nmap file extension (.gnmap or .xml)


def init():
    signal.signal(signal.SIGTERM, sigterm_handle)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGQUIT, signal_handler)
    signal.signal(signal.SIGTSTP, signal_handler)


def signal_handler(sig, frame):
    """
    Handles Ctrl+C signal interupt
    """
    print()
    logger.warning("Ctrl+C caught...")
    logger.warning("Doing cleanup...")
    sys.exit(0)


def sigterm_handle(sig, frame):
    """
    hanles SIGTERM signals
    """
    logger.warning("SIGTERM received...Exiting...")
    sys.exit(0)


def do_argparse() -> dict:
    """
    Description:
        argparse creates a commandline and handles argument parsing

    Returns:
        dictionary
    """
    # Vars
    args = {}

    # Create the parser
    parser = argparse.ArgumentParser(
        description="Verify an nmap file against a target range file to determine if the network is online or offline",
        epilog="Example: nmapSubnetOnline -r ranges.txt -n nmap.xml",
    )

    # Add arguments
    # parser.add_argument("-n", "--num", help="Number of workers to start",  default=1, type=int, action="store")
    # parser.add_argument("-e","--enable",help="Enable '--num' amount of workers", default=False, action="store_true")
    # parser.add_argument("-d","--disable",help="Disable '--num' amount of workers", default=False, action="store_true")
    # parser.add_argument("--ui", help="Enable UI", default=False, action="store_true")
    parser.add_argument(
        "-r",
        "--ranges",
        help="Range file to check for online hosts",
        default="",
        action="store",
        required=True,
    )
    parser.add_argument(
        "-n",
        "--nmap",
        help="Path to nmap output file (Supports multiple flags)",
        action="append",
    )
    parser.add_argument(
        "-d", "--dir", help="Directory of nmap output files", default="", action="store"
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Directory for output files",
        default="./",
        action="store",
    )
    parser.add_argument(
        "--debug", help="Enable debug", default=False, action="store_true"
    )
    parser.add_argument(
        "--quiet", help="Enable quiet mode", default=False, action="store_true"
    )
    # parser.add_argument("--daemon", help="Enable logging to `/var/log` and disable logging to stdout", default=False, action="store_true")

    # Parse the arguments
    args_parser = parser.parse_args()

    # if not args_parser.enable and not args_parser.disable:
    #     parser.format_usage().strip()
    #     print(f"{__file__}: error -e/--enable or -d/--disable must be provided")
    #     sys.exit()

    # Set arguments
    # args["num"] = args_parser.num
    # args["enable"] = args_parser.enable
    # args["disable"] = args_parser.disable
    args["ui"] = False
    args["rangeFile"] = args_parser.ranges
    args["nmapFiles"] = args_parser.nmap
    args["nmapDir"] = args_parser.dir
    args["outputDir"] = args_parser.output
    args["debug"] = args_parser.debug
    args["quiet"] = args_parser.quiet
    args["daemon"] = False

    # Return
    return args


def verifyArgs(args: dict) -> dict:
    nmapFiles = []
    # Verify args["nmapFiles"] and args["nmapDir"]
    if args["nmapFiles"] != None:
        if len(args["nmapFiles"]) > 0:
            for file in args["nmapFiles"]:
                # Verify we were given a .xml file
                if file.lower().endswith(".xml"):
                    nmapFiles.append(file)
                else:
                    logger.warning("Skipping file: '{file}'")
    if args["nmapDir"] != None:
        if args["nmapDir"] and path.exists(args["nmapDir"]):
            files = glob.glob(path.join(args["nmapDir"], f"*{NMAP_EXTENSION}"))
            if len(files) > 0:
                nmapFiles.extend(files)
    if len(nmapFiles) == 0:
        logger.error("No nmap files found")
        sys.exit(1)
    else:
        args["nmapFiles"] = nmapFiles

    # Verify args["rangeFile"]
    if not path.exists(args["rangeFile"]):
        logger.error(f"Range file '{args['rangeFile']}' does not exist")
        sys.exit(1)

    # Verify args["outputDir"]
    if not path.exists(args["outputDir"]):
        logger.debug(f"Creating output directory '{args['outputDir']}'")
        try:
            makedirs(args["outputDir"])
        except Exception as e:
            logger.error(f"Error creating directory '{args['outputDir']}': {e}")
            sys.exit(1)

    return args


def is_ip_in_subnet(ip, subnet):
    return ipaddress.ip_address(ip) in ipaddress.ip_network(subnet, strict=False)


def check_online(hosts, networks):
    for host in hosts:
        for network in networks:
            if is_ip_in_subnet(host, network["network"]):
                network["online"] = True
                break


def nmapsubnetonline(args: dict):
    global FILELOGGER
    init()
    logger.enable(__name__)
    # logger.enable("submodule.submodule")
    if args["daemon"]:
        flogger = FILELOGGER
        FILELOGGER = path.join(FILELOGGER_PATH, flogger)
    initLogger(
        args["debug"], args["quiet"], args["daemon"], args["ui"], FILELOGGER, logger
    )
    logger.success(f"{path.basename(__name__)} has started")

    # Verify args
    args = verifyArgs(args)

    # Read range file
    logger.info(f"Reading range file '{args['rangeFile']}'")
    with open(args["rangeFile"], "r") as f:
        ranges = f.readlines()
    ranges = [x.strip() for x in ranges]

    # Convert ranges into dict of network ranges
    networks = []
    for r in ranges:
        networks.append({"network": r, "online": False})

    # Read nmap files
    for nmapFile in args["nmapFiles"]:
        logger.info(f"Reading nmap file '{nmapFile}'")
        hosts = []
        try:
            hosts = extract_hosts(nmapFile)
            logger.debug(f"Hosts found: {hosts}")
        except Exception as e:
            logger.error("Error parsing nmap file '{nmapFile}'")
            continue

        try:
            check_online(hosts, networks)
        except Exception as e:
            logger.error("Error durin check_online for '{nmapFile}'")
            continue

    for network in networks:
        if network["online"]:
            logger.debug(f"[+] Network {network['network']} is online")
        else:
            logger.debug(f"[!] Network {network['network']} is offline")

    # Output csv file of all networks
    logger.info("Outputting results to csv file")
    base_name, ext = path.splitext(path.basename(args["rangeFile"]))
    csv_output = f"{base_name}_formatted.csv"
    with open(path.join(args["outputDir"], csv_output), "w") as f:
        f.write("Network,Online\n")
        for network in networks:
            #f.write(f"{network['network']},{network['online']}\n")
            if network["online"]:
                f.write(f"{network['network']},Available\n")
            else:
                f.write(f"{network['network']},Unavailable\n")


def main():
    args = do_argparse()
    nmapsubnetonline(args)


if __name__ == "__main__":
    main()
