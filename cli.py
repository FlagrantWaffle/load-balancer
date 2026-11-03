
import argparse
from test_rig import TestRig


TR = TestRig()

def handle_inject(args):
    error_handlers = {
        503: lambda: TR.produce_503(args.lb, args.lbport, args.server)
    }

    try:
        error_handlers[args.error]()
        print("Fault injection requested")

    except KeyError:
        print(f"Unsupported Error Code: {args.error}")

    except (ValueError, TypeError) as exc:
        print(f"Invalid Input: {exc}")


def handle_restore(args):
    TR.restore_servers(args.lbport, args.server)
    print("Server restoration requested")


parser = argparse.ArgumentParser(
    description="Load Balancer Test Rig",
    formatter_class=argparse.RawDescriptionHelpFormatter
)

subparsers = parser.add_subparsers(
    dest="command",
    required=True
)

# INJECT
inject_parser = subparsers.add_parser(
    "inject",
    help="Inject a fault into a server"
)

inject_parser.add_argument("lb", help="The name of the load balancer")
inject_parser.add_argument("--lbport", required=True, type=int, help="The load balancer port")
inject_parser.add_argument("--server", required=True, help="The name of the server")
inject_parser.add_argument("--error", required=True, type=int, help="The error to reproduce")

inject_parser.set_defaults(func=handle_inject)


# RESTORE
restore_parser = subparsers.add_parser(
    "restore",
    help="Restore servers to their normal state"
)

restore_parser.add_argument("lb", help="The name of the load balancer")
restore_parser.add_argument("--lbport", required=True, type=int, help="The load balancer port")
restore_parser.add_argument("--server", help="The name of the server")
restore_parser.set_defaults(func=handle_restore)


def main():
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
