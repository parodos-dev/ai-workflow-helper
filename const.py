SAMPLE_QUERY = '''
    Please create a serverless wofklow which make a request to https://httpbin.org/headers. if the reuqest is 200 OK, please get the response.headers.host from the json, and make another request to https://acalustra.com/provider/post.
'''

EXAMPLES = [
{
    "input": '''Generate a single Event State with one action that calls the "greeting" function. The event state consumes cloud events of type "greetingEventType". When an even with this type is consumed, the Event state performs a single action that calls the defined "greeting" function.''',
    "output":'''
```json
{{
"id": "eventbasedgreeting",
"version": "1.0",
"specVersion": "0.8",
"name": "Event Based Greeting Workflow",
"description": "Event Based Greeting",
"start": "Greet",
"events": [
 {{
  "name": "GreetingEvent",
  "type": "greetingEventType",
  "source": "greetingEventSource"
 }}
],
"functions": [
  {{
     "name": "greetingFunction",
     "operation": "file://myapis/greetingapis.json#greeting"
  }}
],
"states":[
  {{
     "name":"Greet",
     "type":"event",
     "onEvents": [{{
         "eventRefs": ["GreetingEvent"],
         "eventDataFilter": {{
            "data": "${{ .greet }}",
            "toStateData": "${{ .greet }}"
         }},
         "actions":[
            {{
               "functionRef": {{
                  "refName": "greetingFunction",
                  "arguments": {{
                    "name": "${{ .greet.name }}"
                  }}
               }}
            }}
         ]
     }}],
     "stateDataFilter": {{
        "output": "${{ .payload.greeting }}"
     }},
     "end": true
  }}
]
}}
```
    '''
},

{
        "input": '''In this example we show the use of scheduled cron-based start event property. The example workflow checks the users inbox every 15 minutes and send them a text message when there are important emails.
        ''',
        "output": '''```json
{{
"id": "checkInbox",
"name": "Check Inbox Workflow",
"version": "1.0",
"specVersion": "0.8",
"description": "Periodically Check Inbox",
"start": {{
    "stateName": "CheckInbox",
    "schedule": {{
        "cron": "0 0/15 * * * ?"
    }}
}},
"functions": [
    {{
        "name": "checkInboxFunction",
        "operation": "http://myapis.org/inboxapi.json#checkNewMessages"
    }},
    {{
        "name": "sendTextFunction",
        "operation": "http://myapis.org/inboxapi.json#sendText"
    }}
],
"states": [
    {{
        "name": "CheckInbox",
        "type": "operation",
        "actionMode": "sequential",
        "actions": [
            {{
                "functionRef": "checkInboxFunction"
            }}
        ],
        "transition": "SendTextForHighPriority"
    }},
    {{
        "name": "SendTextForHighPriority",
        "type": "foreach",
        "inputCollection": "${{ .messages }}",
        "iterationParam": "singlemessage",
        "actions": [
            {{
                "functionRef": {{
                    "refName": "sendTextFunction",
                    "arguments": {{
                        "message": "${{ .singlemessage }}"
                    }}
                }}
            }}
        ],
        "end": true
    }}
]
}}
```'''
},
{
        "input": "This example shows off the Switch State and the subflow action. The workflow is started with application information data as input",
        "output": '''
```json
{{
   "id": "applicantrequest",
   "version": "1.0",
   "specVersion": "0.8",
   "name": "Applicant Request Decision Workflow",
   "description": "Determine if applicant request is valid",
   "start": "CheckApplication",
   "functions": [
     {{
        "name": "sendRejectionEmailFunction",
        "operation": "http://myapis.org/applicationapi.json#emailRejection"
     }}
   ],
   "states":[
      {{
         "name":"CheckApplication",
         "type":"switch",
         "dataConditions": [
            {{
              "condition": "${{ .applicants | .age >= 18 }}",
              "transition": "StartApplication"
            }},
            {{
              "condition": "${{ .applicants | .age < 18 }}",
              "transition": "RejectApplication"
            }}
         ],
         "defaultCondition": {{
            "transition": "RejectApplication"
         }}
      }},
      {{
        "name": "StartApplication",
        "type": "operation",
        "actions": [
          {{
            "subFlowRef": "startApplicationWorkflowId"
          }}
        ],
        "end": true
      }},
      {{
        "name":"RejectApplication",
        "type":"operation",
        "actionMode":"sequential",
        "actions":[
           {{
              "functionRef": {{
                 "refName": "sendRejectionEmailFunction",
                 "arguments": {{
                   "applicant": "${{ .applicant }}"
                 }}
              }}
           }}
        ],
        "end": true
    }}
   ]
}}
```
'''
}
]

SYSTEM_MESSAGE = '''
You're a agent which help users to write Serverless workflows.

## Schema

```json
{schema}
```

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

# INSTRUCTIONS:
- Based on user input, translate all actions in tasks
- Based on tasks, please write a mermaid diagram to make it clear
- Define the functions needed in serverless workflow
- Write all tasks in the stages section.
- Display all Instructions steps
- ServerlessWorkflow should follow the defined schema bellow.

CONTEXT:
{context}
'''


SYSTEM_MESSAGE_B = '''You are an expert Serverless Workflow generator, responsible for generating valid Serverless Workflows JSON manifests. You must always generate output in raw JSON format and ensure that all required fields such as `id`, `specVersion`, `states`, and `key` are included. Your output should always be wrapped in ```json. Don't rely on data you know about Serverless workflow specification. When a schema includes references to other objects in the schema, look them up when relevant. You may lookup any FIELD in a resource too, not just the containing top-level resource.

Always ensure that the generated JSON follows this basic structure:
```json
{{
   "id": "applicantrequest",
   "version": "1.0",
   "specVersion": "0.8",
   "name": "Applicant Request Decision Workflow",
   "description": "Determine if applicant request is valid",
   "start": "CheckApplication",
   "functions": [
     {{
        "name": "sendRejectionEmailFunction",
        "operation": "http://myapis.org/applicationapi.json#emailRejection"
     }}
   ],
   "states":[
      {{
         "name":"CheckApplication",
         "type":"switch",
         "dataConditions": [
            {{
              "condition": "${{ .applicants | .age >= 18 }}",
              "transition": "StartApplication"
            }},
            {{
              "condition": "${{ .applicants | .age < 18 }}",
              "transition": "RejectApplication"
            }}
         ],
         "defaultCondition": {{
            "transition": "RejectApplication"
         }}
      }},
      {{
        "name": "StartApplication",
        "type": "operation",
        "actions": [
          {{
            "subFlowRef": "startApplicationWorkflowId"
          }}
        ],
        "end": true
      }},
      {{
        "name":"RejectApplication",
        "type":"operation",
        "actionMode":"sequential",
        "actions":[
           {{
              "functionRef": {{
                 "refName": "sendRejectionEmailFunction",
                 "arguments": {{
                   "applicant": "${{ .applicant }}"
                 }}
              }}
           }}
        ],
        "end": true
    }}
   ]
}}
```
please start with this template:

```json
{{
   "id": "<workflow_id>",
   "version": "1.0",
   "specVersion": "0.8",
   "name": "<workflow_name>",
   "description": "<workflow_description>",
   "start": "<init_start_node>",
   "functions": [],
   "states":[]
}}
```
Where you should chnage the labels under <>.

The following are a few examples on how a workflow is defined and compiles based on workflow schema specification, keep in similar way:
Example 1:
IMPUT:
This example shows a single Event State with one action that calls the "greeting" function. The event state consumes cloud events of type "greetingEventType". When an even with this type is consumed, the Event state performs a single action that calls the defined "greeting" function.

OUTPUT:
```json
{{
"id": "eventbasedgreeting",
"version": "1.0",
"specVersion": "0.8",
"name": "Event Based Greeting Workflow",
"description": "Event Based Greeting",
"start": "Greet",
"events": [
 {{
  "name": "GreetingEvent",
  "type": "greetingEventType",
  "source": "greetingEventSource"
 }}
],
"functions": [
  {{
     "name": "greetingFunction",
     "operation": "file://myapis/greetingapis.json#greeting"
  }}
],
"states":[
  {{
     "name":"Greet",
     "type":"event",
     "onEvents": [{{
         "eventRefs": ["GreetingEvent"],
         "eventDataFilter": {{
            "data": "${{ .greet }}",
            "toStateData": "${{ .greet }}"
         }},
         "actions":[
            {{
               "functionRef": {{
                  "refName": "greetingFunction",
                  "arguments": {{
                    "name": "${{ .greet.name }}"
                  }}
               }}
            }}
         ]
     }}],
     "stateDataFilter": {{
        "output": "${{ .payload.greeting }}"
     }},
     "end": true
  }}
]
}}
```

Example 2:
INPUT
In this example we show the use of scheduled cron-based start event
property. The example workflow checks the users inbox every 15 minutes and send
them a text message when there are important emails.

OUTPUT:
```json
{{
"id": "checkInbox",
"name": "Check Inbox Workflow",
"version": "1.0",
"specVersion": "0.8",
"description": "Periodically Check Inbox",
"start": {{
    "stateName": "CheckInbox",
    "schedule": {{
        "cron": "0 0/15 * * * ?"
    }}
}},
"functions": [
    {{
        "name": "checkInboxFunction",
        "operation": "http://myapis.org/inboxapi.json#checkNewMessages"
    }},
    {{
        "name": "sendTextFunction",
        "operation": "http://myapis.org/inboxapi.json#sendText"
    }}
],
"states": [
    {{
        "name": "CheckInbox",
        "type": "operation",
        "actionMode": "sequential",
        "actions": [
            {{
                "functionRef": "checkInboxFunction"
            }}
        ],
        "transition": "SendTextForHighPriority"
    }},
    {{
        "name": "SendTextForHighPriority",
        "type": "foreach",
        "inputCollection": "${{ .messages }}",
        "iterationParam": "singlemessage",
        "actions": [
            {{
                "functionRef": {{
                    "refName": "sendTextFunction",
                    "arguments": {{
                        "message": "${{ .singlemessage }}"
                    }}
                }}
            }}
        ],
        "end": true
    }}
]
}}
```

Example3:
INPUT:
This example shows off the Switch State and the subflow action.
The workflow is started with application information data as input:
OUTPUT
```json
{{
   "id": "applicantrequest",
   "version": "1.0",
   "specVersion": "0.8",
   "name": "Applicant Request Decision Workflow",
   "description": "Determine if applicant request is valid",
   "start": "CheckApplication",
   "functions": [
     {{
        "name": "sendRejectionEmailFunction",
        "operation": "http://myapis.org/applicationapi.json#emailRejection"
     }}
   ],
   "states":[
      {{
         "name":"CheckApplication",
         "type":"switch",
         "dataConditions": [
            {{
              "condition": "${{ .applicants | .age >= 18 }}",
              "transition": "StartApplication"
            }},
            {{
              "condition": "${{ .applicants | .age < 18 }}",
              "transition": "RejectApplication"
            }}
         ],
         "defaultCondition": {{
            "transition": "RejectApplication"
         }}
      }},
      {{
        "name": "StartApplication",
        "type": "operation",
        "actions": [
          {{
            "subFlowRef": "startApplicationWorkflowId"
          }}
        ],
        "end": true
      }},
      {{
        "name":"RejectApplication",
        "type":"operation",
        "actionMode":"sequential",
        "actions":[
           {{
              "functionRef": {{
                 "refName": "sendRejectionEmailFunction",
                 "arguments": {{
                   "applicant": "${{ .applicant }}"
                 }}
              }}
           }}
        ],
        "end": true
    }}
   ]
}}
```
{format_instructions}

Make sure that all required fields are always present in your output.

This is the context that you have:
{context}
'''
