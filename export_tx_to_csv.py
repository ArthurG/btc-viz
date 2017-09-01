import Abe.DataStore as DataStore
import Abe.abe as abe
import Abe.util as util
import sys
import Abe.readconf as readconf
import logging
import csv
from constants import *
from pprint import pprint


def export_store_to_csv(store):
    #all_tx_hash = store.selectall("SELECT tx_hash FROM tx")
    all_tx_hash = store.selectall("SELECT tx_hash FROM tx LIMIT 10000000")
    with open(IN_TRANSACTION_CSV_LOCATION, 'ab') as in_file:
        in_writer = csv.writer(in_file, delimiter=',')
        with open(OUT_TRANSACTION_CSV_LOCATION, 'ab') as out_file:
            out_writer = csv.writer(out_file, delimiter=',')

            for (tx_hash, ) in  all_tx_hash:
                tx_data = store.export_tx(tx_hash = tx_hash, format='browser')

                #Write the tx_in 
                if tx_data["value_in"] is None: 
                    #Write the tx_in -> coinbase case
                    in_writer.writerow([tx_hash, "coinbase", tx_data["value_out"]])
                else:
                    #Write the tx_in -> normal case
                    for in_details in tx_data["in"]:
                        if in_details["binaddr"] is None:
                           continue
                        val = in_details['value']
                        addr = util.hash_to_address(in_details["address_version"], in_details['binaddr'])
                        in_writer.writerow([tx_hash, addr, val])

                #Write the tx_out 
                for out_details in tx_data["out"]:
                    if out_details["binaddr"] is None:
                       continue
                    val = out_details['value']
                    addr = util.hash_to_address(out_details["address_version"], out_details['binaddr'])
                    out_writer.writerow([tx_hash, addr, val])
    return 

DEFAULT_LOG_FORMAT = "%(message)s"

def make_store(args):
    store = DataStore.new(args)
    if (not args.no_load):
        store.catch_up()
    return store


def create_conf():
    return abe.create_conf()


def main(argv):
    if argv[0] == '--show-policy':
        for policy in argv[1:] or list_policies():
            show_policy(policy)
        return 0
    elif argv[0] == '--list-policies':
        print("Available chain policies:")
        for name in list_policies():
            print("  %s" % name)
        return 0

    args, argv = readconf.parse_argv(argv, create_conf())

    if not argv:
        pass
    elif argv[0] in ('-h', '--help'):
        print ("""Usage: python -m Abe.abe [-h] [--config=FILE] [--CONFIGVAR=VALUE]...

A Bitcoin block chain browser.

  --help                    Show this help message and exit.
  --version                 Show the program version and exit.
  --print-htdocs-directory  Show the static content directory name and exit.
  --list-policies           Show the available policy names for --datadir.
  --show-policy POLICY...   Describe the given policy.
  --query /q/COMMAND        Show the given URI content and exit.
  --config FILE             Read options from FILE.

All configuration variables may be given as command arguments.
See abe.conf for commented examples.""")
        return 0
    elif argv[0] in ('-v', '--version'):
        print ABE_APPNAME, ABE_VERSION
        print "Schema version", DataStore.SCHEMA_VERSION
        return 0
    elif argv[0] == '--print-htdocs-directory':
        print find_htdocs()
        return 0
    else:
        sys.stderr.write(
            "Error: unknown option `%s'\n"
            "See `python -m Abe.abe --help' for more information.\n"
            % (argv[0],))
        return 1

    logging.basicConfig(
        stream=sys.stdout,
        level = logging.DEBUG if args.query is None else logging.ERROR,
        format=DEFAULT_LOG_FORMAT)
    if args.logging is not None:
        import logging.config as logging_config
        logging_config.dictConfig(args.logging)

    # Set timezone
    if args.timezone:
        os.environ['TZ'] = args.timezone

    if args.auto_agpl:
        import tarfile

    # --rpc-load-mempool loops forever, make sure it's used with
    # --no-load/--no-serve so users know the implications
    if args.rpc_load_mempool and not (args.no_load or args.no_serve):
        sys.stderr.write("Error: --rpc-load-mempool requires --no-serve\n")
        return 1

    store = make_store(args)
    export_store_to_csv(store)
    if (not args.no_serve):
        #serve(store)
        pass
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
