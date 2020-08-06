#!/bin/sh

#
# Start the first EC2 instance found with the name provided as the first
# argument. If the region is omitted as the second argument, it is taken
# from the default configuration.
#

set -o errexit
set -o nounset

name="$1"
shift

if [ 0 -lt "$#" ]
then
    region="$1"
    shift
else
    region=
fi

if ! command -v jq
then
    echo jq is missing >&2
    exit 1
fi

start_ec2_instance() {
    local name="$1"
    shift

    local region="$1"
    shift

    local region_arg=
    if [ -n "$region" ]
    then
        region_arg="--region $region"
    fi

    local instance_id="$(aws $region_arg --output json ec2 describe-instances \
        --filters Name=tag:Name,Values="$name" \
        --query "Reservations[*].Instances[*].InstanceId" \
        | jq -r ".[0][0]"
    )"
    aws $region_arg ec2 start-instances --instance-ids "$instance_id"
}

start_ec2_instance "$name" "$region"

