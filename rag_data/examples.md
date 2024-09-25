# Example 0

This example shows a single Operation State with one
action that calls the “greeting” function. The workflow data input is
assumed to be the name of the person to greet:
```json
{
"id": "greeting",
"version": "1.0",
"specVersion": "0.8",
"name": "Greeting Workflow",
"description": "Greet Someone",
"start": "Greet",
"functions": [
  {
     "name": "greetingFunction",
     "operation": "file://myapis/greetingapis.json#greeting"
  }
],
"states":[
  {
     "name":"Greet",
     "type":"operation",
     "actions":[
        {
           "functionRef": {
              "refName": "greetingFunction",
              "arguments": {
                "name": "${ .person.name }"
              }
           },
           "actionDataFilter": {
              "results": "${ .greeting }"
           }
        }
     ],
     "end": true
  }
]
}
```


# Example 1

This example shows a single Event State with one action
that calls the “greeting” function. The event state consumes cloud
events of type “greetingEventType”. When an even with this type is
consumed, the Event state performs a single action that calls the
defined “greeting” function.
```json
{
"id": "eventbasedgreeting",
"version": "1.0",
"specVersion": "0.8",
"name": "Event Based Greeting Workflow",
"description": "Event Based Greeting",
"start": "Greet",
"events": [
 {
  "name": "GreetingEvent",
  "type": "greetingEventType",
  "source": "greetingEventSource"
 }
],
"functions": [
  {
     "name": "greetingFunction",
     "operation": "file://myapis/greetingapis.json#greeting"
  }
],
"states":[
  {
     "name":"Greet",
     "type":"event",
     "onEvents": [{
         "eventRefs": ["GreetingEvent"],
         "eventDataFilter": {
            "data": "${ .greet }",
            "toStateData": "${ .greet }"
         },
         "actions":[
            {
               "functionRef": {
                  "refName": "greetingFunction",
                  "arguments": {
                    "name": "${ .greet.name }"
                  }
               }
            }
         ]
     }],
     "stateDataFilter": {
        "output": "${ .payload.greeting }"
     },
     "end": true
  }
]
}
```


# Example 2

In this example we show how to iterate over data using the ForEach State. The state
will iterate over a collection of simple math expressions which are
passed in as the workflow data input:
```json
{
"id": "solvemathproblems",
"version": "1.0",
"specVersion": "0.8",
"name": "Solve Math Problems Workflow",
"description": "Solve math problems",
"start": "Solve",
"functions": [
{
  "name": "solveMathExpressionFunction",
  "operation": "http://myapis.org/mapthapis.json#solveExpression"
}
],
"states":[
{
 "name":"Solve",
 "type":"foreach",
 "inputCollection": "${ .expressions }",
 "iterationParam": "singleexpression",
 "outputCollection": "${ .results }",
 "actions":[
   {
      "functionRef": {
         "refName": "solveMathExpressionFunction",
         "arguments": {
           "expression": "${ .singleexpression }"
         }
      }
   }
 ],
 "stateDataFilter": {
    "output": "${ .results }"
 },
 "end": true
}
]
}
```


# Example 3

This example uses a Parallel State to execute
two branches (simple wait states) at the same time. The completionType
type is set to “allOf”, which means the parallel state has to wait for
both branches to finish execution before it can transition (end workflow
execution in this case as it is an end state).
```json
{
"id": "parallelexec",
"version": "1.0",
"specVersion": "0.8",
"name": "Parallel Execution Workflow",
"description": "Executes two branches in parallel",
"start": "ParallelExec",
"states":[
  {
     "name": "ParallelExec",
     "type": "parallel",
     "completionType": "allOf",
     "branches": [
        {
          "name": "ShortDelayBranch",
          "actions": [{
            "subFlowRef": "shortdelayworkflowid"
          }]
        },
        {
          "name": "LongDelayBranch",
          "actions": [{
            "subFlowRef": "longdelayworkflowid"
          }]
        }
     ],
     "end": true
  }
]
}
```


# Example 4

This example uses a Operation State to invoke
a function async. This functions sends an email to a customer. Async
function execution is a “fire-and-forget” type of invocation. The
function is invoked and workflow execution does not wait for its
results.
```json
{
 "id": "sendcustomeremail",
 "version": "1.0",
 "specVersion": "0.8",
 "name": "Send customer email workflow",
 "description": "Send email to a customer",
 "start": "Send Email",
 "functions": [
  {
   "name": "emailFunction",
   "operation": "file://myapis/emailapis.json#sendEmail"
  }
 ],
 "states":[
  {
   "name":"Send Email",
   "type":"operation",
   "actions":[
    {
     "functionRef": {
      "invoke": "async",
      "refName": "emailFunction",
      "arguments": {
       "customer": "${ .customer }"
      }
     }
    }
   ],
   "end": true
  }
 ]
}
```


# Example 5

This example uses a Operation State to invoke
a SubFlow async. This
SubFlow is responsible for performing some customer business logic.
Async SubFlow invocation is a “fire-and-forget” type of invocation. The
SubFlow is invoked and workflow execution does not wait for its results.
In addition, we specify that the SubFlow should be allowed to continue
its execution event if the parent workflow completes its own execution.
This is done by defining the actions onParentComplete
property to continue.
```json
{
 "id": "onboardcustomer",
 "version": "1.0",
 "specVersion": "0.8",
 "name": "Onboard Customer",
 "description": "Onboard a Customer",
 "start": "Onboard",
 "states":[
  {
   "name":"Onboard", 
   "type":"operation",
   "actions":[
    {
     "subFlowRef": {
      "invoke": "async",
      "onParentComplete": "continue",
      "workflowId": "customeronboardingworkflow",
      "version": "1.0"
     }
    }
   ],
   "end": true
  }
 ]
}
```


# Example 6

In this example we use an Event-based Switch State to wait for
arrival of the “VisaApproved”, or “VisaRejected” Cloud Events. Depending
on which type of event happens, the workflow performs a different
transition. If none of the events arrive in the defined 1 hour timeout
period, the workflow transitions to the “HandleNoVisaDecision”
state.
```json
{
"id": "eventbasedswitchstate",
"version": "1.0",
"specVersion": "0.8",
"name": "Event Based Switch Transitions",
"description": "Event Based Switch Transitions",
"start": "CheckVisaStatus",
"events": [
{
    "name": "visaApprovedEvent",
    "type": "VisaApproved",
    "source": "visaCheckSource"
},
{
    "name": "visaRejectedEvent",
    "type": "VisaRejected",
    "source": "visaCheckSource"
}
],
"states":[
  {
     "name":"CheckVisaStatus",
     "type":"switch",
     "eventConditions": [
        {
          "eventRef": "visaApprovedEvent",
          "transition": "HandleApprovedVisa"
        },
        {
          "eventRef": "visaRejectedEvent",
          "transition": "HandleRejectedVisa"
        }
     ],
     "eventTimeout": "PT1H",
     "defaultCondition": {
        "transition": "HandleNoVisaDecision"
     }
  },
  {
    "name": "HandleApprovedVisa",
    "type": "operation",
    "actions": [
      {
        "subFlowRef": "handleApprovedVisaWorkflowID"
      }
    ],
    "end": true
  },
  {
      "name": "HandleRejectedVisa",
      "type": "operation",
      "actions": [
        {
          "subFlowRef": "handleRejectedVisaWorkflowID"
        }
      ],
      "end": true
  },
  {
      "name": "HandleNoVisaDecision",
      "type": "operation",
      "actions": [
        {
          "subFlowRef": "handleNoVisaDecisionWorkflowId"
        }
      ],
      "end": true
  }
]
}
```


# Example 7

This example shows off the Switch State and the subflow
action. The workflow is started with application information data as
input:
```json
{
   "id": "applicantrequest",
   "version": "1.0",
   "specVersion": "0.8",
   "name": "Applicant Request Decision Workflow",
   "description": "Determine if applicant request is valid",
   "start": "CheckApplication",
   "functions": [
     {
        "name": "sendRejectionEmailFunction",
        "operation": "http://myapis.org/applicationapi.json#emailRejection"
     }
   ],
   "states":[
      {
         "name":"CheckApplication",
         "type":"switch",
         "dataConditions": [
            {
              "condition": "${ .applicants | .age >= 18 }",
              "transition": "StartApplication"
            },
            {
              "condition": "${ .applicants | .age < 18 }",
              "transition": "RejectApplication"
            }
         ],
         "defaultCondition": {
            "transition": "RejectApplication"
         }
      },
      {
        "name": "StartApplication",
        "type": "operation",
        "actions": [
          {
            "subFlowRef": "startApplicationWorkflowId"
          }
        ],
        "end": true
      },
      {
        "name":"RejectApplication",
        "type":"operation",
        "actionMode":"sequential",
        "actions":[
           {
              "functionRef": {
                 "refName": "sendRejectionEmailFunction",
                 "arguments": {
                   "applicant": "${ .applicant }"
                 }
              }
           }
        ],
        "end": true
    }
   ]
}
```


# Example 8

In this example we show off the states error handling capability. The
workflow data input that’s passed in contains missing order information
that causes the function in the “ProvisionOrder” state to throw a
runtime exception. With the “onErrors” definition we can transition the
workflow to different error handling states. Each type of error in this
example is handled by simple delay states. If no errors are encountered
the workflow can transition to the “ApplyOrder” state.
```json
{
"id": "provisionorders",
"version": "1.0",
"specVersion": "0.8",
"name": "Provision Orders",
"description": "Provision Orders and handle errors thrown",
"start": "ProvisionOrder",
"functions": [
  {
     "name": "provisionOrderFunction",
     "operation": "http://myapis.org/provisioningapi.json#doProvision"
  }
],
"errors": [
 {
  "name": "Missing order id"
 },
 {
  "name": "Missing order item"
 },
 {
  "name": "Missing order quantity"
 }
],
"states":[
  {
    "name":"ProvisionOrder",
    "type":"operation",
    "actionMode":"sequential",
    "actions":[
       {
          "functionRef": {
             "refName": "provisionOrderFunction",
             "arguments": {
               "order": "${ .order }"
             }
          }
       }
    ],
    "stateDataFilter": {
       "output": "${ .exceptions }"
    },
    "transition": "ApplyOrder",
    "onErrors": [
       {
         "errorRef": "Missing order id",
         "transition": "MissingId"
       },
       {
         "errorRef": "Missing order item",
         "transition": "MissingItem"
       },
       {
        "errorRef": "Missing order quantity",
        "transition": "MissingQuantity"
       }
    ]
},
{
   "name": "MissingId",
   "type": "operation",
   "actions": [
     {
       "subFlowRef": "handleMissingIdExceptionWorkflow"
     }
   ],
   "end": true
},
{
   "name": "MissingItem",
   "type": "operation",
   "actions": [
     {
       "subFlowRef": "handleMissingItemExceptionWorkflow"
     }
   ],
   "end": true
},
{
   "name": "MissingQuantity",
   "type": "operation",
   "actions": [
     {
       "subFlowRef": "handleMissingQuantityExceptionWorkflow"
     }
   ],
   "end": true
},
{
   "name": "ApplyOrder",
   "type": "operation",
   "actions": [
     {
       "subFlowRef": "applyOrderWorkflowId"
     }
   ],
   "end": true
}
]
}
```


# Example 9

In this example we submit a job via an operation state action
(serverless function call). It is assumed that it takes some time for
the submitted job to complete and that it’s completion can be checked
via another separate serverless function call.
```json
{
  "id": "jobmonitoring",
  "version": "1.0",
  "specVersion": "0.8",
  "name": "Job Monitoring",
  "description": "Monitor finished execution of a submitted job",
  "start": "SubmitJob",
  "functions": [
    {
      "name": "submitJob",
      "operation": "http://myapis.org/monitorapi.json#doSubmit"
    },
    {
      "name": "checkJobStatus",
      "operation": "http://myapis.org/monitorapi.json#checkStatus"
    },
    {
      "name": "reportJobSuceeded",
      "operation": "http://myapis.org/monitorapi.json#reportSucceeded"
    },
    {
      "name": "reportJobFailed",
      "operation": "http://myapis.org/monitorapi.json#reportFailure"
    }
  ],
  "states":[
    {
      "name":"SubmitJob",
      "type":"operation",
      "actionMode":"sequential",
      "actions":[
      {
          "functionRef": {
            "refName": "submitJob",
            "arguments": {
              "name": "${ .job.name }"
            }
          },
          "actionDataFilter": {
            "results": "${ .jobuid }"
          }
      }
      ],
      "stateDataFilter": {
          "output": "${ .jobuid }"
      },
      "transition": "WaitForCompletion"
  },
  {
      "name": "WaitForCompletion",
      "type": "sleep",
      "duration": "PT5S",
      "transition": "GetJobStatus"
  },
  {
      "name":"GetJobStatus",
      "type":"operation",
      "actionMode":"sequential",
      "actions":[
      {
        "functionRef": {
            "refName": "checkJobStatus",
            "arguments": {
              "name": "${ .jobuid }"
            }
          },
          "actionDataFilter": {
            "results": "${ .jobstatus }"
          }
      }
      ],
      "stateDataFilter": {
          "output": "${ .jobstatus }"
      },
      "transition": "DetermineCompletion"
  },
  {
    "name":"DetermineCompletion",
    "type":"switch",
    "dataConditions": [
      {
        "condition": "${ .jobStatus == \"SUCCEEDED\" }",
        "transition": "JobSucceeded"
      },
      {
        "condition": "${ .jobStatus == \"FAILED\" }",
        "transition": "JobFailed"
      }
    ],
    "defaultCondition": {
      "transition": "WaitForCompletion"
    }
  },
  {
      "name":"JobSucceeded",
      "type":"operation",
      "actionMode":"sequential",
      "actions":[
      {
        "functionRef": {
            "refName": "reportJobSuceeded",
            "arguments": {
              "name": "${ .jobuid }"
            }
        }
      }
      ],
      "end": true
  },
  {
    "name":"JobFailed",
    "type":"operation",
    "actionMode":"sequential",
    "actions":[
    {
        "functionRef": {
          "refName": "reportJobFailed",
          "arguments": {
            "name": "${ .jobuid }"
          }
        }
    }
    ],
    "end": true
  }
  ]
}
```


# Example 10

This example shows how we can produce a CloudEvent on completion of a
workflow. Let’s say we have the following workflow data containing
orders that need to be provisioned by our workflow:
```json
{
"id": "sendcloudeventonprovision",
"version": "1.0",
"specVersion": "0.8",
"name": "Send CloudEvent on provision completion",
"start": "ProvisionOrdersState",
"events": [
{
    "name": "provisioningCompleteEvent",
    "type": "provisionCompleteType",
    "kind": "produced"
}
],
"functions": [
{
    "name": "provisionOrderFunction",
    "operation": "http://myapis.org/provisioning.json#doProvision"
}
],
"states": [
{
    "name": "ProvisionOrdersState",
    "type": "foreach",
    "inputCollection": "${ .orders }",
    "iterationParam": "singleorder",
    "outputCollection": "${ .provisionedOrders }",
    "actions": [
        {
            "functionRef": {
                "refName": "provisionOrderFunction",
                "arguments": {
                    "order": "${ .singleorder }"
                }
            }
        }
    ],
    "end": {
        "produceEvents": [{
            "eventRef": "provisioningCompleteEvent",
            "data": "${ .provisionedOrders }"
        }]
    }
}
]
}
```


# Example 11

In this example a hospital patient is monitored by a Vial Sign
Monitoring system. This device can produce three different Cloud Events,
namely “High Body Temperature”, “High Blood Pressure”, and “High
Respiration Rate”. Our workflow which needs to take proper actions
depending on the event the Vital Sign Monitor produces needs to start if
any of these events occur. For each of these events a new instance of
the workflow is started.
```json
{
"id": "patientVitalsWorkflow",
"name": "Monitor Patient Vitals",
"version": "1.0",
"specVersion": "0.8",
"start": "MonitorVitals",
"events": [
{
    "name": "HighBodyTemperature",
    "type": "org.monitor.highBodyTemp",
    "source": "monitoringSource",
    "correlation": [
      {
        "contextAttributeName": "patientId"
      }
    ]
},
{
    "name": "HighBloodPressure",
    "type": "org.monitor.highBloodPressure",
    "source": "monitoringSource",
    "correlation": [
      {
        "contextAttributeName": "patientId"
      }
    ]
},
{
    "name": "HighRespirationRate",
    "type": "org.monitor.highRespirationRate",
    "source": "monitoringSource",
    "correlation": [
      {
        "contextAttributeName": "patientId"
      }
    ]
}
],
"functions": [
{
    "name": "callPulmonologist",
    "operation": "http://myapis.org/patientapis.json#callPulmonologist"
},
{
    "name": "sendTylenolOrder",
    "operation": "http://myapis.org/patientapis.json#tylenolOrder"
},
{
    "name": "callNurse",
    "operation": "http://myapis.org/patientapis.json#callNurse"
}
],
"states": [
{
"name": "MonitorVitals",
"type": "event",
"exclusive": true,
"onEvents": [{
        "eventRefs": ["HighBodyTemperature"],
        "actions": [{
            "functionRef": {
                "refName": "sendTylenolOrder",
                "arguments": {
                    "patientid": "${ .patientId }"
                }
            }
        }]
    },
    {
        "eventRefs": ["HighBloodPressure"],
        "actions": [{
            "functionRef": {
                "refName": "callNurse",
                "arguments": {
                    "patientid": "${ .patientId }"
                }
            }
        }]
    },
    {
        "eventRefs": ["HighRespirationRate"],
        "actions": [{
            "functionRef": {
                "refName": "callPulmonologist",
                "arguments": {
                    "patientid": "${ .patientId }"
                }
            }
        }]
    }
],
"end": {
    "terminate": true
}
}]
}
```


# Example 12

In this example our workflow is instantiated when all requirements of
a college application are completed. These requirements include a
student submitting an application, the college receiving the students
SAT scores, as well as a student recommendation letter from a former
teacher.
```json
{
"id": "finalizeCollegeApplication",
"name": "Finalize College Application",
"version": "1.0",
"specVersion": "0.8",
"start": "FinalizeApplication",
"events": [
{
    "name": "ApplicationSubmitted",
    "type": "org.application.submitted",
    "source": "applicationsource",
    "correlation": [
    {
      "contextAttributeName": "applicantId"
    }
   ]
},
{
    "name": "SATScoresReceived",
    "type": "org.application.satscores",
    "source": "applicationsource",
    "correlation": [
      {
      "contextAttributeName": "applicantId"
      }
    ]
},
{
    "name": "RecommendationLetterReceived",
    "type": "org.application.recommendationLetter",
    "source": "applicationsource",
    "correlation": [
      {
      "contextAttributeName": "applicantId"
      }
    ]
}
],
"functions": [
{
    "name": "finalizeApplicationFunction",
    "operation": "http://myapis.org/collegeapplicationapi.json#finalize"
}
],
"states": [
{
    "name": "FinalizeApplication",
    "type": "event",
    "exclusive": false,
    "onEvents": [
        {
            "eventRefs": [
                "ApplicationSubmitted",
                "SATScoresReceived",
                "RecommendationLetterReceived"
            ],
            "actions": [
                {
                    "functionRef": {
                        "refName": "finalizeApplicationFunction",
                        "arguments": {
                            "student": "${ .applicantId }"
                        }
                    }
                }
            ]
        }
    ],
    "end": {
        "terminate": true
    }
}
]
}
```


# Example 13

In this example our serverless workflow needs to integrate with an
external microservice to perform a credit check. We assume that this
external microservice notifies a human actor which has to make the
approval decision based on customer information. Once this decision is
made the service emits a CloudEvent which includes the decision
information as part of its payload. The workflow waits for this callback
event and then triggers workflow transitions based on the credit check
decision results.
```json
{
    "id": "customercreditcheck",
    "version": "1.0",
    "specVersion": "0.8",
    "name": "Customer Credit Check Workflow",
    "description": "Perform Customer Credit Check",
    "start": "CheckCredit",
    "functions": [
        {
            "name": "creditCheckFunction",
            "operation": "http://myapis.org/creditcheckapi.json#doCreditCheck"
        },
        {
            "name": "sendRejectionEmailFunction",
            "operation": "http://myapis.org/creditcheckapi.json#rejectionEmail"
        }
    ],
    "events": [
        {
            "name": "CreditCheckCompletedEvent",
            "type": "creditCheckCompleteType",
            "source": "creditCheckSource",
            "correlation": [
              {
                "contextAttributeName": "customerId"
              }
           ]
        }
    ],
    "states": [
        {
            "name": "CheckCredit",
            "type": "callback",
            "action": {
                "functionRef": {
                    "refName": "callCreditCheckMicroservice",
                    "arguments": {
                        "customer": "${ .customer }"
                    }
                }
            },
            "eventRef": "CreditCheckCompletedEvent",
            "timeouts": {
              "stateExecTimeout": "PT15M"
            },
            "transition": "EvaluateDecision"
        },
        {
            "name": "EvaluateDecision",
            "type": "switch",
            "dataConditions": [
                {
                    "condition": "${ .creditCheck | .decision == \"Approved\" }",
                    "transition": "StartApplication"
                },
                {
                    "condition": "${ .creditCheck | .decision == \"Denied\" }",
                    "transition": "RejectApplication"
                }
            ],
            "defaultCondition": {
               "transition": "RejectApplication"
            }
        },
        {
            "name": "StartApplication",
            "type": "operation",
            "actions": [
              {
                "subFlowRef": "startApplicationWorkflowId"
              }
            ],
            "end": true
        },
        {
            "name": "RejectApplication",
            "type": "operation",
            "actionMode": "sequential",
            "actions": [
                {
                    "functionRef": {
                        "refName": "sendRejectionEmailFunction",
                        "arguments": {
                            "applicant": "${ .customer }"
                        }
                    }
                }
            ],
            "end": true
        }
    ]
}
```


# Example 14

In this example our serverless workflow needs to handle bits for an
online car auction. The car auction has a specific start and end time.
Bids are only allowed to be made during this time period. All bids
before or after this time should not be considered. We assume that the
car auction starts at 9am UTC on March 20th 2020 and ends at 3pm UTC on
March 20th 2020.
```json
{
    "id": "handleCarAuctionBid",
    "version": "1.0",
    "specVersion": "0.8",
    "name": "Car Auction Bidding Workflow",
    "description": "Store a single bid whole the car auction is active",
    "start": {
      "stateName": "StoreCarAuctionBid",
      "schedule": "R/PT2H"
    },
    "functions": [
        {
            "name": "StoreBidFunction",
            "operation": "http://myapis.org/carauctionapi.json#storeBid"
        }
    ],
    "events": [
        {
            "name": "CarBidEvent",
            "type": "carBidMadeType",
            "source": "carBidEventSource"
        }
    ],
    "states": [
        {
          "name": "StoreCarAuctionBid",
          "type": "event",
          "exclusive": true,
          "onEvents": [
            {
                "eventRefs": ["CarBidEvent"],
                "actions": [{
                    "functionRef": {
                        "refName": "StoreBidFunction",
                        "arguments": {
                            "bid": "${ .bid }"
                        }
                    }
                }]
            }
          ],
          "end": true
        }
    ]
}
```


# Example 15

In this example we show the use of scheduled cron-based start event
property. The example workflow checks the users inbox every 15 minutes
and send them a text message when there are important emails.
```json
{
"id": "checkInbox",
"name": "Check Inbox Workflow",
"version": "1.0",
"specVersion": "0.8",
"description": "Periodically Check Inbox",
"start": {
    "stateName": "CheckInbox",
    "schedule": {
        "cron": "0 0/15 * * * ?"
    }
},
"functions": [
    {
        "name": "checkInboxFunction",
        "operation": "http://myapis.org/inboxapi.json#checkNewMessages"
    },
    {
        "name": "sendTextFunction",
        "operation": "http://myapis.org/inboxapi.json#sendText"
    }
],
"states": [
    {
        "name": "CheckInbox",
        "type": "operation",
        "actionMode": "sequential",
        "actions": [
            {
                "functionRef": "checkInboxFunction"
            }
        ],
        "transition": "SendTextForHighPriority"
    },
    {
        "name": "SendTextForHighPriority",
        "type": "foreach",
        "inputCollection": "${ .messages }",
        "iterationParam": "singlemessage",
        "actions": [
            {
                "functionRef": {
                    "refName": "sendTextFunction",
                    "arguments": {
                        "message": "${ .singlemessage }"
                    }
                }
            }
        ],
        "end": true
    }
]
}
```


# Example 16

In this example we want to make a Veterinary appointment for our dog
Mia. The vet service can be invoked only via an event, and its
completion results with the appointment day and time is returned via an
event as well.
```json
{
    "id": "VetAppointmentWorkflow",
    "name": "Vet Appointment Workflow",
    "description": "Vet service call via events",
    "version": "1.0",
    "specVersion": "0.8",
    "start": "MakeVetAppointmentState",
    "events": [
        {
            "name": "MakeVetAppointment",
            "source": "VetServiceSource",
            "type": "events.vet.appointments",
            "kind": "produced"
        },
        {
            "name": "VetAppointmentInfo",
            "source": "VetServiceSource",
            "type": "events.vet.appointments",
            "kind": "consumed"
        }
    ],
    "states": [
        {
            "name": "MakeVetAppointmentState",
            "type": "operation",
            "actions": [
                {
                    "name": "MakeAppointmentAction",
                    "eventRef": {
                       "triggerEventRef": "MakeVetAppointment",
                       "data": "${ .patientInfo }",
                       "resultEventRef":  "VetAppointmentInfo"
                    },
                    "actionDataFilter": {
                        "results": "${ .appointmentInfo }"
                    }
                }
            ],
            "timeouts": {
              "actionExecTimeout": "PT15M"
            },
            "end": true
        }
    ]
}
```


# Example 17

This example shows how function and event definitions can be
declared independently and referenced by workflow definitions. This is
useful when you would like to reuse event and function definitions
across multiple workflows. In those scenarios it allows you to make
changed/updates to these definitions in a single place without having to
modify multiple workflows.
```json
{
  "id": "patientonboarding",
  "name": "Patient Onboarding Workflow",
  "version": "1.0",
  "specVersion": "0.8",
  "start": "Onboard",
  "states": [
    {
      "name": "Onboard",
      "type": "event",
      "onEvents": [
        {
          "eventRefs": [
            "NewPatientEvent"
          ],
          "actions": [
            {
              "functionRef": "StorePatient",
              "retryRef": "ServicesNotAvailableRetryStrategy",
              "retryableErrors": ["ServiceNotAvailable"]
            },
            {
              "functionRef": "AssignDoctor",
              "retryRef": "ServicesNotAvailableRetryStrategy",
              "retryableErrors": ["ServiceNotAvailable"]
            },
            {
              "functionRef": "ScheduleAppt",
              "retryRef": "ServicesNotAvailableRetryStrategy",
              "retryableErrors": ["ServiceNotAvailable"]
            }
          ]
        }
      ],
      "onErrors": [
        {
          "errorRef": "ServiceNotAvailable",
          "end": true
        }
      ],
      "end": true
    }
  ],
  "events": [
    {
      "name": "StorePatient",
      "type": "new.patients.event",
      "source": "newpatient/+"
    }
  ],
  "functions": [
    {
      "name": "StoreNewPatientInfo",
      "operation": "api/services.json#addPatient"
    },
    {
      "name": "AssignDoctor",
      "operation": "api/services.json#assignDoctor"
    },
    {
      "name": "ScheduleAppt",
      "operation": "api/services.json#scheduleAppointment"
    }
  ],
  "errors": [
   {
    "name": "ServiceNotAvailable",
    "code": "503"
   }
  ],
  "retries": [
    {
      "name": "ServicesNotAvailableRetryStrategy",
      "delay": "PT3S",
      "maxAttempts": 10
    }
  ]
}
```


# Example 18

In this example we want to use a workflow to onboard a new patient
(at a hospital for example). To onboard a patient our workflow is
invoked via a “NewPatientEvent” event. This events payload contains the
patient information, for example:
```json
{
  "id": "order",
  "name": "Purchase Order Workflow",
  "version": "1.0",
  "specVersion": "0.8",
  "start": "StartNewOrder",
  "timeouts": {
    "workflowExecTimeout": {
      "duration": "PT30D",
      "runBefore": "CancelOrder"
    }
  },
  "states": [
    {
      "name": "StartNewOrder",
      "type": "event",
      "onEvents": [
        {
          "eventRefs": ["OrderCreatedEvent"],
          "actions": [
            {
              "functionRef": {
                "refName": "LogNewOrderCreated"
              }
            }
          ]
        }
      ],
      "transition": {
        "nextState": "WaitForOrderConfirmation"
      }
    },
    {
      "name": "WaitForOrderConfirmation",
      "type": "event",
      "onEvents": [
        {
          "eventRefs": ["OrderConfirmedEvent"],
          "actions": [
            {
              "functionRef": {
                "refName": "LogOrderConfirmed"
              }
            }
          ]
        }
      ],
      "transition": {
        "nextState": "WaitOrderShipped"
      }
    },
    {
      "name": "WaitOrderShipped",
      "type": "event",
      "onEvents": [
        {
          "eventRefs": ["ShipmentSentEvent"],
          "actions": [
            {
              "functionRef": {
                "refName": "LogOrderShipped"
              }
            }
          ]
        }
      ],
      "end": {
        "terminate": true,
        "produceEvents": [
          {
            "eventRef": "OrderFinishedEvent"
          }
        ]
      }
    },
    {
      "name": "CancelOrder",
      "type": "operation",
      "actions": [
        {
          "functionRef": {
            "refName": "CancelOrder"
          }
        }
      ],
      "end": {
        "terminate": true,
        "produceEvents": [
          {
            "eventRef": "OrderCancelledEvent"
          }
        ]
      }
    }
  ],
  "events": [
    {
      "name": "OrderCreatedEvent",
      "type": "my.company.orders",
      "source": "/orders/new",
      "correlation": [
        {
          "contextAttributeName": "orderid"
        }
      ]
    },
    {
      "name": "OrderConfirmedEvent",
      "type": "my.company.orders",
      "source": "/orders/confirmed",
      "correlation": [
        {
          "contextAttributeName": "orderid"
        }
      ]
    },
    {
      "name": "ShipmentSentEvent",
      "type": "my.company.orders",
      "source": "/orders/shipped",
      "correlation": [
        {
          "contextAttributeName": "orderid"
        }
      ]
    },
    {
      "name": "OrderFinishedEvent",
      "type": "my.company.orders",
      "kind": "produced"
    },
    {
      "name": "OrderCancelledEvent",
      "type": "my.company.orders",
      "kind": "produced"
    }
  ],
  "functions": [
    {
      "name": "LogNewOrderCreated",
      "operation": "http.myorg.io/ordersservices.json#logcreated"
    },
    {
      "name": "LogOrderConfirmed",
      "operation": "http.myorg.io/ordersservices.json#logconfirmed"
    },
    {
      "name": "LogOrderShipped",
      "operation": "http.myorg.io/ordersservices.json#logshipped"
    },
    {
      "name": "CancelOrder",
      "operation": "http.myorg.io/ordersservices.json#calcelorder"
    }
  ]
}
```


# Example 19

In this example our workflow processes purchase orders. An order
event triggers instance of our workflow. To complete the created order,
our workflow must first wait for an order confirmation event (correlated
to the order id), and then wait for the shipment sent event (also
correlated to initial order id). We do not want to place an exact
timeout limit for waiting for the confirmation and shipment events, as
this might take a different amount of time depending on the size of the
order. However we do have the requirement that a total amount of time
for the order to be confirmed, once its created, is 30 days. If the
created order is not completed within 30 days it needs to be
automatically closed.
```json
{
  "id": "roomreadings",
  "name": "Room Temp and Humidity Workflow",
  "version": "1.0",
  "specVersion": "0.8",
  "start": "ConsumeReading",
  "timeouts": {
    "workflowExecTimeout": {
      "duration": "PT1H",
      "runBefore": "GenerateReport"
    }
  },
  "keepActive": true,
  "states": [
    {
      "name": "ConsumeReading",
      "type": "event",
      "onEvents": [
        {
          "eventRefs": ["TemperatureEvent", "HumidityEvent"],
          "actions": [
            {
              "functionRef": {
                "refName": "LogReading"
              }
            }
          ],
          "eventDataFilter": {
            "toStateData": "${ .readings }"
          }
        }
      ],
      "end": true
    },
    {
      "name": "GenerateReport",
      "type": "operation",
      "actions": [
        {
          "functionRef": {
            "refName": "ProduceReport",
            "arguments": {
              "data": "${ .readings }"
            }
          }
        }
      ],
      "end": {
        "terminate": true
      }
    }
  ],
  "events": [
    {
      "name": "TemperatureEvent",
      "type": "my.home.sensors",
      "source": "/home/rooms/+",
      "correlation": [
        {
          "contextAttributeName": "roomId"
        }
      ]
    },
    {
      "name": "HumidityEvent",
      "type": "my.home.sensors",
      "source": "/home/rooms/+",
      "correlation": [
        {
          "contextAttributeName": "roomId"
        }
      ]
    }
  ],
  "functions": [
    {
      "name": "LogReading",
      "operation": "http.myorg.io/ordersservices.json#logreading"
    },
    {
      "name": "ProduceReport",
      "operation": "http.myorg.io/ordersservices.json#produceReport"
    }
  ]
}
```


# Example 20

In this example we have two IoT sensors for each room in our house.
One reads temperature values and the other humidity values of each room.
We get these measurements for each of our rooms as CloudEvents. We can
correlate events send by our sensors by the room it is in.
```json
{
 "id": "checkcarvitals",
 "name": "Check Car Vitals Workflow",
 "version": "1.0",
 "specVersion": "0.8",
 "start": "WhenCarIsOn",
 "states": [
  {
   "name": "WhenCarIsOn",
   "type": "event",
   "onEvents": [
    {
     "eventRefs": ["CarTurnedOnEvent"]
    }
   ],
   "transition": "DoCarVitalChecks"
  },
  {
   "name": "DoCarVitalChecks",
   "type": "operation",
   "actions": [
    {
     "subFlowRef": "vitalscheck",
     "sleep": {
      "after": "PT1S"
     }
    }
   ],
   "transition": "CheckContinueVitalChecks"
  },
  {
   "name": "CheckContinueVitalChecks",
   "type": "switch",
   "eventConditions": [
    {
     "name": "Car Turned Off Condition",
     "eventRef": "CarTurnedOffEvent",
     "end": true
    }
   ],
   "defaultCondition": {
    "transition": "DoCarVitalChecks"
   }
  }
 ],
 "events": [
  {
   "name": "CarTurnedOnEvent",
   "type": "car.events",
   "source": "my/car"
  },
  {
   "name": "CarTurnedOffEvent",
   "type": "car.events",
   "source": "my/car"
  }
 ]
}
```


# Example 21

In this example we need to check car vital signs while our car is
driving. The workflow should start when we receive the
“CarTurnedOnEvent” event and stop when the “CarTurnedOffEvent” event is
consumed. While the car is driving our workflow should repeatedly check
the vitals every 1 second.
```json
{
 "id": "booklending",
 "name": "Book Lending Workflow",
 "version": "1.0",
 "specVersion": "0.8",
 "start": "Book Lending Request",
 "states": [
  {
   "name": "Book Lending Request",
   "type": "event",
   "onEvents": [
    {
     "eventRefs": ["Book Lending Request Event"]
    }
   ],
   "transition": "Get Book Status"
  },
  {
   "name": "Get Book Status",
   "type": "operation",
   "actions": [
    {
     "functionRef": {
      "refName": "Get status for book",
      "arguments": {
       "bookid": "${ .book.id }"
      }
     }
    }
   ],
   "transition": "Book Status Decision"
  },
  {
   "name": "Book Status Decision",
   "type": "switch",
   "dataConditions": [
    {
     "name": "Book is on loan",
     "condition": "${ .book.status == \"onloan\" }",
     "transition": "Report Status To Lender"
    },
    {
     "name": "Check is available",
     "condition": "${ .book.status == \"available\" }",
     "transition": "Check Out Book"
    }
   ],
   "defaultCondition": {
    "end": true
   }
  },
  {
   "name": "Report Status To Lender",
   "type": "operation",
   "actions": [
    {
     "functionRef": {
      "refName": "Send status to lender",
      "arguments": {
       "bookid": "${ .book.id }",
       "message": "Book ${ .book.title } is already on loan"
      }
     }
    }
   ],
   "transition": "Wait for Lender response"
  },
  {
   "name": "Wait for Lender response",
   "type": "switch",
   "eventConditions": [
    {
     "name": "Hold Book",
     "eventRef": "Hold Book Event",
     "transition": "Request Hold"
    },
    {
     "name": "Decline Book Hold",
     "eventRef": "Decline Hold Event",
     "transition": "Cancel Request"
    }
   ],
   "defaultCondition": {
    "end": true
   }
  },
  {
   "name": "Request Hold",
   "type": "operation",
   "actions": [
    {
     "functionRef": {
      "refName": "Request hold for lender",
      "arguments": {
       "bookid": "${ .book.id }",
       "lender": "${ .lender }"
      }
     }
    }
   ],
   "transition": "Sleep two weeks"
  },
  {
   "name": "Sleep two weeks",
   "type": "sleep",
   "duration": "PT2W",
   "transition": "Get Book Status"
  },
  {
   "name": "Check Out Book",
   "type": "operation",
   "actions": [
    {
     "functionRef": {
      "refName": "Check out book with id",
      "arguments": {
       "bookid": "${ .book.id }"
      }
     }
    },
    {
     "functionRef": {
      "refName": "Notify Lender for checkout",
      "arguments": {
       "bookid": "${ .book.id }",
       "lender": "${ .lender }"
      }
     }
    }
   ],
   "end": true
  }
 ],
 "functions": "file://books/lending/functions.json",
 "events": "file://books/lending/events.json"
}
```


# Example 22

In this example we want to create a book lending workflow. The
workflow starts when a lender submits a book lending request (via event
“Book Lending Request Event”). The workflow describes our business logic
around lending a book, from checking its current availability, to
waiting on the lender’s response if the book is currently not available,
to checking out the book and notifying the lender.
```json
{
 "id": "fillglassofwater",
 "name": "Fill glass of water workflow",
 "version": "1.0",
 "specVersion": "0.8",
 "start": "Check if full",
 "functions": [
  {
   "name": "Increment Current Count Function",
   "type": "expression",
   "operation": ".counts.current += 1 | .counts.current"
  }
 ],
 "states": [
  {
   "name": "Check if full",
   "type": "switch",
   "dataConditions": [
    {
     "name": "Need to fill more",
     "condition": "${ .counts.current < .counts.max }",
     "transition": "Add Water"
    },
    {
     "name": "Glass full",
     "condition": ".counts.current >= .counts.max",
     "end": true
    }
   ],
   "defaultCondition": {
    "end": true
   }
  },
  {
   "name": "Add Water",
   "type": "operation",
   "actions": [
    {
     "functionRef": "Increment Current Count Function",
     "actionDataFilter": {
      "toStateData": ".counts.current"
     }
    }
   ],
   "transition": "Check if full"
  }
 ]
}
```


# Example 23

In this example we showcase the power of expression
functions. Our workflow definition is assumed to have the following
data input:
```json
{
 "id":"notifycustomerworkflow",
 "name":"Notify Customer",
 "version":"1.0",
 "specVersion": "0.8",
 "start":"WaitForCustomerEvent",
 "states":[
  {
   "name":"WaitForCustomerEvent",
   "type":"event",
   "onEvents":[
    {
     "eventRefs":[
      "CustomerEvent"
     ],
     "eventDataFilter":{
      "data":"${ .customerId }",
      "toStateData":"${ .eventCustomerId }"
     },
     "actions":[
      {
       "functionRef":{
        "refName":"NotifyCustomerFunction",
        "arguments":{
         "customerId":"${ .eventCustomerId }"
        }
       }
      }
     ]
    }
   ],
   "stateDataFilter":{
    "output":"${ .count = .count + 1 }"
   },
   "transition":"CheckEventQuota"
  },
  {
   "name":"CheckEventQuota",
   "type":"switch",
   "dataConditions":[
    {
     "condition":"${ try(.customerCount) != null and .customerCount > .quota.maxConsumedEvents }",
     "end":{
      "continueAs": {
       "workflowId": "notifycustomerworkflow",
       "version": "1.0",
       "data": "${ del(.customerCount) }"
      }
     }
    }
   ],
   "defaultCondition":{
    "transition":"WaitForCustomerEvent"
   }
  }
 ],
 "events":[
  {
   "name":"CustomerEvent",
   "type":"org.events.customerEvent",
   "source":"customerSource"
  }
 ],
 "functions":[
  {
   "name":"NotifyCustomerFunction",
   "operation":"http://myapis.org/customerapis.json#notifyCustomer"
  }
 ]
}
```


# Example 24

In this example we want to create an online food ordering workflow.
The below image outlines the workflow structure and the available
services:
```json
{
 "id": "customerbankingtransactions",
 "name": "Customer Banking Transactions Workflow",
 "version": "1.0",
 "specVersion": "0.8",
 "autoRetries": true,
 "constants": {
  "largetxamount" : 5000
 },
 "states": [
  {
   "name": "ProcessTransactions",
   "type": "foreach",
   "inputCollection": "${ .customer.transactions }",
   "iterationParam": "${ .tx }",
   "actions": [
    {
     "name": "Process Larger Transaction",
     "functionRef": "Banking Service - Larger Tx",
     "condition": "${ .tx >= $CONST.largetxamount }"
    },
    {
     "name": "Process Smaller Transaction",
     "functionRef": "Banking Service - Smaller Tx",
     "condition": "${ .tx < $CONST.largetxamount }"
    }
   ],
   "end": true
  }
 ],
 "functions": [
  {
   "name": "Banking Service - Larger Tx",
   "type": "asyncapi",
   "operation": "banking.yaml#largerTransation"
  },
  {
   "name": "Banking Service - Smaller T",
   "type": "asyncapi",
   "operation": "banking.yaml#smallerTransation"
  }
 ]
}
```

