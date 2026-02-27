# Incident Event Types (Embedding-Optimized Descriptions)

The events of a troubleshooting service, generally requiring highly skilled technicians. For examples of troubleshooting services:

- Patient visiting the doctor for an ad-hoc incident.
- Plumber responding to an emergency such as a broken pipe.
- Lawyer taking a case to rectify inheritance issues.
- Electricians fixing a transformer hit by lightning.
- Information Technology addressing a crashed software service.

Events are presented in the typical <b>average</b> oridnal in which they occur. That means they can occur in any order and can looped back upon.

## Events

### 1.0 chief_complaint
The initial statement of the problem reported by the customer or user. This describes the symptom or failure that triggered the incident and led the customer to seek help. It is usually written from the customer's perspective and focuses on what is not working. Typical language includes phrases like “customer reports,” “complaining that,” “system not working,” “water is lukewarm,” “pressure is low,” “application crashing,” or “unable to log in.”

### 2.0 background
Contextual information about events or conditions leading up to the problem. This includes prior history, recent changes, unusual usage, environmental factors, or earlier repairs that might explain the issue. Typical language includes “started after,” “recently noticed,” “after guests stayed,” “after the update,” “previous repair,” or “issue began following.”

### 3.0 diagnosis
The expert’s initial explanation of the likely cause of the problem based on the complaint and background information. This is a hypothesis about what is wrong before the repair begins. Typical language includes “appears that,” “likely cause,” “suggests that,” “it seems the issue is,” “suspect the valve,” or “problem may be related to.”

### 4.0 setup_sensors
Actions taken to prepare tools or instruments used to collect diagnostic information. This includes installing gauges, enabling logs, attaching monitoring devices, configuring test equipment, or setting up measurement tools. Typical phrases include “connected gauge,” “enabled logging,” “set up monitoring,” “installed diagnostic tool,” or “attached pressure meter.”

### 5.0 collect_data
The process of gathering measurements or observations from sensors, instruments, or monitoring tools. This stage captures raw readings or logs without interpreting them yet. Typical language includes “recorded readings,” “captured logs,” “ran test,” “measured temperature,” “checked pressure,” or “collected data.”

### 6.0 analyze_data
Interpretation of the collected measurements or logs in order to determine the cause of the issue. The expert reviews readings, compares values, and evaluates patterns. Typical phrases include “analysis shows,” “readings indicate,” “reviewing the data,” “comparison suggests,” or “results show.”

### 7.0 treatment_plan
The proposed solution or corrective action intended to resolve the problem. This step explains what repair, replacement, configuration change, or procedure will be performed. Typical language includes “recommended replacing,” “plan is to repair,” “proposed solution,” “suggest installing,” or “next step is to fix.”

### 8.0 estimate_cost
An estimate of the cost, time, or resources required to perform the proposed repair or treatment. This may include labor, parts, materials, or service charges. Typical language includes “estimated cost,” “labor estimate,” “parts and labor,” “quoted price,” or “repair estimate.”

### 9.0 present_treatment_cost
Communication of the treatment plan and cost estimate to the customer for approval. The expert explains the proposed work and associated charges before beginning the repair. Typical language includes “reviewed estimate,” “presented repair plan,” “explained cost,” “provided quote,” or “discussed repair and price.”

### 10.0 customer_rejects_treatment
The customer declines the proposed repair or refuses the cost estimate. This indicates that the repair will not proceed as planned. Typical language includes “customer declined,” “customer rejected estimate,” “chose not to proceed,” “repair postponed,” or “customer refused service.”

### 11.0 customer_accepts_treatment
The customer approves the proposed treatment plan and authorizes the work to proceed. This indicates formal or informal permission to begin the repair. Typical language includes “customer approved,” “authorized repair,” “agreed to proceed,” or “approved estimate.”

### 12.0 execute_treatment
The technician or expert performs the repair or corrective action described in the treatment plan. This includes installing parts, replacing components, adjusting systems, or applying the fix. Typical language includes “replaced valve,” “installed new cartridge,” “performed repair,” “applied fix,” or “completed installation.”

### 13.0 test_treatment_application
Verification that the repair successfully resolved the issue. The technician runs tests or operates the system to confirm correct behavior after the repair. Typical language includes “tested system,” “verified operation,” “confirmed fix,” “checked performance,” or “problem resolved.”

### 14.0 prepare_report
Preparation of documentation summarizing the incident, including observations, actions taken, and results. This may involve writing service notes, compiling logs, or creating a formal report. Typical language includes “prepared report,” “documented findings,” “recorded service notes,” or “wrote summary.”

### 15.0 present_report
Delivery of the report or documentation to the customer or organization. This can include submitting a report, sending documentation, or presenting findings in a meeting. Typical language includes “submitted report,” “shared findings,” “provided documentation,” or “sent report.”

### 16.0 customer_accept_outcome
The customer confirms that the repair or treatment solved the problem and that the outcome is satisfactory. Typical language includes “customer confirmed resolution,” “issue resolved,” “customer satisfied,” or “repair accepted.”

### 17.0 customer_rejects_outcome
The customer reports that the issue is still present or that the solution did not meet expectations. This may lead to further investigation or additional work. Typical language includes “problem persists,” “customer not satisfied,” “issue still occurring,” or “repair did not fix.”

### 18.0 bill_submitted
The service provider issues an invoice or billing statement for the work performed. This records that charges have been formally sent to the customer. Typical language includes “invoice issued,” “bill submitted,” “service charge sent,” or “billing completed.”

## 19.0 customer_paid
Confirmation that the customer has paid the invoice or completed the financial transaction. Typical language includes “payment received,” “invoice paid,” “customer paid,” or “payment processed.”
