#!/usr/bin/env python3
"""Count current (non-history) FHIR resources at a FHIR endpoint.

The script asks the server for its CapabilityStatement ([base]/metadata),
collects every resource type the server allows clients to search, and runs a
"_summary=count" search for each one. That search returns a `searchset` Bundle
whose `total` field is the number of *current* resources of that type -- a
plain search never reaches into `_history`, so superseded versions are never
counted.

Two totals are reported:

  * TOTAL resources            -- every resource type summed together.
  * TOTAL excluding foundation -- the same sum minus the "foundation" resource
                                  types (profiles, value sets, code systems and
                                  other server-configuration metadata; see
                                  FOUNDATION_RESOURCE_TYPES). This figure
                                  approximates how much real health data the
                                  server actually holds.

Only the Python standard library is used, so no `pip install` is required.

Usage examples:

  # Count everything on a local onFHIR server
  python count_fhir_resources.py http://localhost:6080/fhir

  # Also list resource types that have zero instances
  python count_fhir_resources.py http://localhost:6080/fhir --show-zeros

  # Treat extra resource types as foundation, on top of the built-in set
  python count_fhir_resources.py http://localhost:6080/fhir --exclude Subscription

  # Talk to a SMART-on-FHIR protected server using a bearer token
  python count_fhir_resources.py https://example.org/fhir --token "$ACCESS_TOKEN"
  FHIR_TOKEN="$ACCESS_TOKEN" python count_fhir_resources.py https://example.org/fhir
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

# Media type requested from the server, per the FHIR REST spec.
FHIR_ACCEPT = "application/fhir+json"

# FHIR "foundation" resource types: server-configuration and metadata
# resources rather than actual health data. An onFHIR server persists its own
# profiles, value sets and code systems as ordinary resources, which otherwise
# inflates the resource count. These types are subtracted to produce the
# "TOTAL excluding foundation" figure; callers can add more with --exclude.
FOUNDATION_RESOURCE_TYPES = frozenset({
    # Conformance module
    "CapabilityStatement",
    "StructureDefinition",
    "ImplementationGuide",
    "SearchParameter",
    "MessageDefinition",
    "OperationDefinition",
    "CompartmentDefinition",
    "StructureMap",
    "GraphDefinition",
    # Terminology module
    "ValueSet",
    "CodeSystem",
})


def _get(url, token, timeout):
    """Issue a GET request and return the decoded JSON body.

    When `token` is supplied it is sent as a Bearer Authorization header, so the
    script works against SMART-on-FHIR protected servers as well as open ones.
    """
    headers = {"Accept": FHIR_ACCEPT}
    if token:
        headers["Authorization"] = "Bearer " + token
    request = urllib.request.Request(url, headers=headers, method="GET")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def discover_resource_types(base, token, timeout):
    """Return the sorted resource types the server lets clients search.

    The list comes from the server's CapabilityStatement. Only types that
    advertise the `search-type` interaction are kept -- a type without it
    cannot answer a `_summary=count` query. Exits the process with a clear
    message if the CapabilityStatement cannot be fetched or parsed.
    """
    try:
        statement = _get(base + "/metadata", token, timeout)
    except (urllib.error.URLError, urllib.error.HTTPError, OSError) as err:
        sys.exit("Could not fetch CapabilityStatement from %s/metadata: %s"
                 % (base, err))
    except json.JSONDecodeError as err:
        sys.exit("CapabilityStatement at %s/metadata is not valid JSON: %s"
                 % (base, err))

    types = []
    for rest in statement.get("rest", []):
        for resource in rest.get("resource", []):
            kind = resource.get("type")
            interactions = {i.get("code") for i in resource.get("interaction", [])}
            if kind and "search-type" in interactions:
                types.append(kind)
    if not types:
        sys.exit("No searchable resource types found in the CapabilityStatement.")
    return sorted(set(types))


def count_resource(base, kind, token, timeout):
    """Return the count of current resources for a single resource type.

    `_summary=count` asks the server to return only the match count -- in
    `Bundle.total` -- instead of the resources themselves, which keeps the
    request cheap regardless of how much data the type holds.
    """
    bundle = _get("%s/%s?_summary=count" % (base, kind), token, timeout)
    total = bundle.get("total")
    if not isinstance(total, int):
        raise ValueError("response has no integer 'total' field")
    return total


def main():
    parser = argparse.ArgumentParser(
        description="Count current (non-history) FHIR resources at an endpoint.",
        epilog=(
            "examples:\n"
            "  python count_fhir_resources.py http://localhost:6080/fhir\n"
            "  python count_fhir_resources.py https://matrix.srdc.com.tr/dt4h/onfhir\n"
            "  python count_fhir_resources.py http://localhost:6080/fhir --show-zeros\n"
            "  python count_fhir_resources.py https://example.org/fhir --token \"$ACCESS_TOKEN\""
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "endpoint",
        help="FHIR base URL, e.g. http://localhost:6080/fhir")
    parser.add_argument(
        "--token", default=os.environ.get("FHIR_TOKEN"),
        help="Bearer token for protected servers (or set FHIR_TOKEN env var).")
    parser.add_argument(
        "--show-zeros", action="store_true",
        help="Include resource types with a count of 0 in the breakdown.")
    parser.add_argument(
        "--exclude", action="append", metavar="TYPE", default=[],
        help="Extra resource type to treat as a foundation resource "
             "(repeatable). The built-in foundation set is always excluded; "
             "this only adds to it.")
    parser.add_argument(
        "--timeout", type=float, default=30.0,
        help="Per-request timeout in seconds (default: 30).")
    args = parser.parse_args()

    # Tolerate a trailing slash so both ".../fhir" and ".../fhir/" work.
    base = args.endpoint.rstrip("/")

    print("Fetching CapabilityStatement from %s/metadata ..." % base)
    types = discover_resource_types(base, args.token, args.timeout)
    print("Counting %d resource type(s)...\n" % len(types))

    # Count each type independently; a failure on one type (e.g. a server-side
    # error) is recorded in `errors` and the run continues with the rest.
    counts = {}
    errors = {}
    for kind in types:
        try:
            counts[kind] = count_resource(base, kind, args.token, args.timeout)
        except (urllib.error.URLError, urllib.error.HTTPError, OSError,
                json.JSONDecodeError, ValueError) as err:
            errors[kind] = str(err)

    # Built-in foundation set plus anything the caller added with --exclude.
    foundation = FOUNDATION_RESOURCE_TYPES | set(args.exclude)

    # Breakdown, biggest counts first; foundation rows are flagged.
    width = max((len(k) for k in counts), default=0)
    for kind, total in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
        if total == 0 and not args.show_zeros:
            continue
        marker = "  (foundation)" if kind in foundation else ""
        print("  %-*s  %d%s" % (width, kind, total, marker))

    grand_total = sum(counts.values())
    foundation_total = sum(t for k, t in counts.items() if k in foundation)
    data_total = grand_total - foundation_total

    print("\n" + "-" * 40)
    print("Resource types counted:      %d" % len(counts))
    print("TOTAL resources:             %d" % grand_total)
    print("Foundation resources:        %d" % foundation_total)
    print("TOTAL excluding foundation:  %d" % data_total)

    excluded_present = sorted(k for k in foundation if k in counts)
    if excluded_present:
        print("\nFoundation types excluded from the last total: %s"
              % ", ".join(excluded_present))

    # A non-zero exit code lets callers/CI detect that some types failed.
    if errors:
        print("\n%d resource type(s) could not be counted:" % len(errors))
        for kind, message in sorted(errors.items()):
            print("  %s: %s" % (kind, message))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
