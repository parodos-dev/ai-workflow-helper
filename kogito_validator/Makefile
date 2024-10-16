build:
	podman build -t quay.io/parodos-dev/kogito-validator .

push:
	podman run quay.io/parodos-dev/kogito-validator

test:
	podman run  -v /tmp/workflow.sw.json:/workflow.sw.json -ti eloycoto/kogito
