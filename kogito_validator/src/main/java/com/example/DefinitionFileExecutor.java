package com.example;

import org.kie.kogito.serverless.workflow.executor.StaticWorkflowApplication;
import org.kie.kogito.serverless.workflow.models.JsonNodeModel;
import org.kie.kogito.serverless.workflow.utils.ServerlessWorkflowUtils;
import org.kie.kogito.serverless.workflow.utils.WorkflowFormat;
import io.serverlessworkflow.api.Workflow;
import org.kie.kogito.process.Process;

import java.io.FileReader;
import java.io.IOException;
import java.io.Reader;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;

public class DefinitionFileExecutor {

    public static void main(String[] args) throws IOException {
        System.out.printf("Initialize the workflow: %s\n", args[0]);

        try (Reader reader = new FileReader(args[0]);
             StaticWorkflowApplication application = StaticWorkflowApplication.create()) {
             Workflow workflow = ServerlessWorkflowUtils.getWorkflow(reader, WorkflowFormat.JSON);
             application.process(workflow);

            JsonNodeModel result = application.execute(workflow, Collections.emptyMap());
            System.out.printf("Execution information: %s\n", result);

            List<String> registeredStates = workflow.getStates().stream()
                                        .map(p -> p.getName())
                                        .collect(Collectors.toList());

            List<String> registeredFunctions = workflow.getFunctions().getFunctionDefs().stream()
                                        .map(p -> p.getName())
                                        .collect(Collectors.toList());

            System.out.println("Registered functions:");
            System.out.println(registeredFunctions);

            System.out.println("Registered states:");
            System.out.println(registeredStates);

        } catch (Exception e) {
            System.err.println("[ERROR] Workflow is not valid: " + e.getMessage());
            System.exit(1);
        }
    }
}
