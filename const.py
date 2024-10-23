# flake8: noqa E501
import os

SAMPLE_QUERY = '''
    I need to generate a workflow which:
    - Make a request to https://httpbin.org/headers and save the information in the state.
    - If previous request fail for any reason, log the error.
    - If not, please send a HTTP POST request to https://acalustra.com/provider/post and request data should be the previous response.
'''

COMPLEX_QUERY = '''I need to create a workflow which checks the financial data for a list of companies and pushed to my service.

The input of the workflow will be like:

{"companies": ["IBM", "APPL"]}

For each company, the data can be get from the following url, where symbol is the company information:

curl -s "https://www.alphavantage.co/query?function=OVERVIEW&symbol=IBM&apikey=demo" | jq '."52WeekHigh"'

When you iterate to all the companies the output should be:

```
[
    {"company": "IBM", "high": $52WeekHighValue},
    {"company": "APPL", "high": $52WeekHighValue},
]
```
And this result should be post to: "http://acalustra.com/financialData/post"
'''

class ExamplesIterator:
    def __init__(self, directory):
        self.directory = directory
        self.examples = self._load_examples()
        self.index = 0

    def _load_examples(self):
        examples = []
        files = os.listdir(self.directory)
        input_files = sorted([f for f in files if f.endswith('_input.txt')])

        for input_file in input_files:
            example_num = input_file.split('_')[0]
            output_file = f"{example_num}_output.txt"

            if output_file in files:
                with open(os.path.join(self.directory, input_file), 'r') as f:
                    input_text = f.read()
                with open(os.path.join(self.directory, output_file), 'r') as f:
                    output_text = f.read()
                examples.append({
                    "input": input_text,
                    "output": output_text
                })
        return examples

    def __iter__(self):
        return self

    def __next__(self):
        if self.index < len(self.examples):
            result = self.examples[self.index]
            self.index += 1
            return result
        else:
            raise StopIteration

EXAMPLES=list(ExamplesIterator("./lib/prompts/examples/"))
REACT_EXAMPLES=list(ExamplesIterator("./lib/prompts/react/"))

REACT_MESSAGE = '''Review and correct the given JSON workflow based on the user provided input ensuring it matches the user's requirement and handles errors appropriately.
 
The result json should adheres to the following schema:
```
{schema}
```

Examine the initial JSON workflow against the user's input and improve it to fit the task description precisely.

# Steps

1. Parse the JSON workflow provided by the AI.
2. Verify that the workflow matches the user's workflow task requirements.
3. Add the missing pieces or functions to align the workflow with the tasks described by the user.
4. Ensure proper error handling and transitions are in place between the tasks.
5. If any errors or issues are found, correct them to match the user's needs.

# Rules

- If the user adds the maven compilation log, please keep iterating in the user workflow json which is given by him.
- You need to work only with serverless workflow.
- Do not use any knowledge from your training.

# Common errors:

## Functions:

In the root of the object, all the functions are specified, all of them should be used in state, errors, or events.

Functions definitions are like this:
```
{{
    "functions": [
        {{
          "name": "getIP",
          "type": "custom",
          "operation": "rest:get:https://ipinfo.io/json"
        }},
    ]
}}
```

The types can be:
- custom: where custom operation can be used, for example: `rest:get:https://ipinfo.io/json` will make a GET request to https://ipinfo.io/json or sysout:INFO will write something to the log.
    The custom operations allowed are: `rest:get:`, `sysout:DEBUG`, `sysout:INFO`, `rest:post:`
- rest: a combination of the function/service OpenAPI definition document URI and the particular service operation that needs to be invoked, separated by a '#'. For example https://petstore.swagger.io/v2/swagger.json#getPetById.
- rpc:  a combination of the gRPC proto document URI and the particular service name and service method name that needs to be invoked, separated by a '#'. For example file://myuserservice.proto#UserService#ListUsers.

To using the functions arguments inside the state array, should be like this:

```
{{
  "functionRef": {{
    "refName": "pushData",
    "arguments": {{
        "city": ".ip_info.city",
        "ip": ".ip_info.ip"
    }}
  }},
}}
```

You need to take care that all functionRef.refName should match with the name of one function in the functions definition.

## Transitions:

State has next transition, if it's present you need to validate that matches with one name of state array.
When defined errors, there is also a transition which need to be present too.

## Error handling

Errors are defined in the root of the document, like:

```
"errors": [
{{
  "name": "notAvailable",
  "code": "404"
}},
{{
  "name": "notAllowed",
  "code": "405"
}}
],
```

'''

SYSTEM_MESSAGE = '''
You're a agent which help users to write Serverless workflows.

### Well formatted instance

```json
{{
 "id": "fillglassofwater",
 "name": "Fill glass of water workflow",
 "version": "1.0",
 "specVersion": "0.8",
 "start": "Check if full",
 "functions": [
  {{
   "name": "Increment Current Count Function",
   "type": "expression",
   "operation": ".counts.current += 1 | .counts.current"
  }}
 ],
 "states": [
  {{
   "name": "Check if full",
   "type": "switch",
   "dataConditions": [
    {{
     "name": "Need to fill more",
     "condition": "${{ .counts.current < .counts.max }}",
     "transition": "Add Water"
    }},
    {{
     "name": "Glass full",
     "condition": ".counts.current >= .counts.max",
     "end": true
    }}
   ],
   "defaultCondition": {{
    "end": true
   }}
  }},
  {{
   "name": "Add Water",
   "type": "operation",
   "actions": [
    {{
     "functionRef": "Increment Current Count Function",
     "actionDataFilter": {{
      "toStateData": ".counts.current"
     }}
    }}
   ],
   "transition": "Check if full"
  }}
 ]
}}
```
# Context

<retrieved context>
Retrieved Context:
{context}
</retrieved context>

# INSTRUCTIONS:

1) Plan how to create a workflow, including the initial state, end state, loops, and functions.
2) Define the name, description, and ID for the workflow.
3) Complete all functions with name type and operation.
4) Define the errors messages and code
5) Complete the states array in the workflow JSON based on the user's input and using previous functions and errors.

# RULES:
- Specversion is always 0.8 and it's a required field.
- Version is always 1.0 and it's a required field.
- You follow the format Instructions, and keep data according to the provided jsonschema.
- Do not use any previous information related to serverless workflow schemas. You can look in context and in the examples for references.
- Functions must be utilized in the states.
- Ensure that the ID, name, description, and start state are always present.
- Each state should have a field `end` equals true or transition to the next state. One of this is needed.
- If you get a bash input, first think in the transformation to be part of a function. Like curl request will be functions like rest:$method:$url.
- All required fields must be included in your output_file.
- Do not write any YAML, I only need JSON output.
- Write all tasks in the states section.
- The output should be formatted as a JSON instance that adheres to the given JSON schema below.
```json
{{
    "id": "myworkflowid",
    "version": "1.0",
    "specVersion": "0.8",
    "name": "User example workflow",
    "description": "And empty workflow",
    "start": "CheckApplication",
    "functions": [ ],
    "states":[],
    "errors": []
}}
```

## Functions

Each workflow can define different functions, like:
```
{{
    "functions": [
        {{
          "name": "getIP",
          "type": "custom",
          "operation": "rest:get:https://ipinfo.io/json"
        }},
    ]
}}
```

The types can be:
- custom: where custom operation can be used, for example: `rest:get:https://ipinfo.io/json` will make a GET request to https://ipinfo.io/json or sysout:INFO will write something to the log.
    The custom operations allowed are: `rest:get:`, `sysout:DEBUG`, `sysout:INFO`, `rest:post:`
- rest: a combination of the function/service OpenAPI definition document URI and the particular service operation that needs to be invoked, separated by a '#'. For example https://petstore.swagger.io/v2/swagger.json#getPetById.
- rpc:  a combination of the gRPC proto document URI and the particular service name and service method name that needs to be invoked, separated by a '#'. For example file://myuserservice.proto#UserService#ListUsers.

Example of using the functions arguments inside the state array:

```
{{
  "functionRef": {{
    "refName": "pushData",
    "arguments": {{
        "city": ".ip_info.city",
        "ip": ".ip_info.ip"
    }}
  }},
}}
```

Where arguments can be build with state data using the dot notation. Is required that arguments are inside the functionRef object.

## Error handling

Errors are defined in the root of the document, like:

```
"errors": [
{{
  "name": "notAvailable",
  "code": "404"
}},
{{
  "name": "notAllowed",
  "code": "405"
}}
],
```

When errors happens in the serverless workflow state, need to be managed by the field `onErrors`:

```
"onErrors": [
    {{
      "errorRef": "notAvailable",
      "transition": "logError"
    }}
],
```

If no error, will jump to next transition defined on the `state.transition` field. Need to make sure, that the transition state is present in the array. The name for the transition should be part of any name inside the states array, it's mandatory. In this case, a state with name: logError need to be present in the output.

## State

A good state will looks like this:

```
{{
  "name": "Get public IP",
  "type": "operation",
  "actions": [
    {{
      "functionRef": {{
        "refName": "getIP"
      }}
    }}
  ],
  "onErrors": [
    {{
      "errorRef": "notAvailable",
      "transition": "logError"
    }}
  ],
  "transition": "push_host_data"
}}
```

It contains some actions with functions defined in the root, this array should always have at least one entry.
It contains a transition key for the next step if the state runs correctly. This is always needed, the only case when is not needed is if the `end` is true. The transaction value should be one of the names in the array of the states.
It contains the `OnErrors` key, which is optional, but make sure that the state error is handled correctly.
It contains a valid `type` and `name` which is defined in the jsonschema.
'''
