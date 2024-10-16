build:
	podman build -t quay.io/parodos-dev/kogito-validator .

push:
	podman push quay.io/parodos-dev/kogito-validator

test:
	podman run  -v /tmp/workflow.sw.json:/workflow.sw.json -ti quay.io/parodos-dev/kogito-validator
