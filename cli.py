import argparse
from test_rig import TestRig


TR = TestRig()
parser = argparse.ArgumentParser(description="Load Balancer Test Rig", formatter_class=argparse.RawDescriptionHelpFormatter)

parser.add_argument("lb", help="The name of the load balancer")
parser.add_argument("--lbport", required=True, help="The port the load balancer is exposed on")
parser.add_argument("--server", required=True, help="The name of the server")
parser.add_argument("--error", required=True, help="The error to reproduce")

args = parser.parse_args()
print(args.lb)
print(args.lbport)
print(args.server)
print(args.error)

if args is None:
    parser.print_help()
    raise SystemExit(0)

args_to_rig = {
    503: lambda: TR.produce_503(args.lb, args.lbport, args.server)
}

try:
    error_handler = args_to_rig[int(args.error)]()
    print("attempting to send args to rig")
    

except KeyError as exc:
    print(f"Unsupported Error Code: {exc}")

except (ValueError, TypeError) as exc:
    print(f"Invalid Input: {exc}")
