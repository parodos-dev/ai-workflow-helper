import podman
from podman.errors.exceptions import ContainerError
import logging
import uuid
import os


serverless_image = "registry.redhat.io/openshift-serverless-1-tech-preview/logic-swf-devmode-rhel8:1.32.0"

class ServerlessValidation(object):

    def __init__(self, workflow):
        self.uuid = uuid.uuid4()
        self.temp_file = f"/tmp/workflow_{self.uuid}"
        if not os.path.exists(self.temp_file):
            os.makedirs(self.temp_file)

        logging.info(f"Create a temp file: {self.temp_file}")
        self.workflow = workflow
        self.client = podman.PodmanClient()
        self.client.images.pull(serverless_image)
        self._create_sample_workflow()

    def _create_sample_workflow(self):
        with open(f"{self.temp_file}/workflow.sw.json", "w") as fp:
            fp.write(self.workflow)


    def run(self):
        try:
            container = self.client.containers.run(
                image=serverless_image,
                detach=False,
                remove=False,
                command="/home/kogito/launch/build-app.sh",
                mounts= [
                    {
                        "type": "bind",
                        "source": self.temp_file,
                        "target": "/home/kogito/serverless-workflow-project/src/main/resources",
                        "read_only": False,
                        "relabel": "Z"
                    },
                ]
            )
            result = container.decode()
            return (result, "[ERROR]" not in result)
        except ContainerError as e:
            return (e.stderr, False)
