#!/bin/sh

#
# Local Docker installations like Docker for Mac support local Kubernetes
# clusters. However, they often leave behind old supporting images on updates.
# This cleans them out but assumes the latest images are in use by the cluster
# and so won't be deleted by Docker.
#

docker images \
	| awk '/k8s|kube-/ { print $1 ":" $2 }' \
	| xargs docker rmi

