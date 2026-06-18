## Schematics and Structured Diagrams as Knowledge Graph Properties

Some knowledge cannot be adequately represented through labels, classes, and hierarchies alone. A class hierarchy can tell us that an electric motor is a kind of vehicle component, but it does not show where the motor is located, how it connects to the battery, or what other parts depend on it.

In those cases, a schematic or structured diagram can be treated as a rich external property of a knowledge graph entity.

A car, for example, may link to an engineering schematic:

```turtle
:CarModelS
    a :VehicleModel ;
    :hasSchematic :ModelS_ChassisSchematic .

:ModelS_ChassisSchematic
    a :EngineeringSchematic ;
    :fileLocation <https://example.org/model-s-chassis.svg> ;
    :depictsPart :BatteryPack ;
    :depictsPart :FrontMotor ;
    :depictsPart :RearMotor .
```

The individual parts shown in the schematic can also be represented as knowledge graph entities:

```turtle
:BatteryPack
    a :VehicleComponent ;
    :partOf :CarModelS .

:FrontMotor
    a :ElectricMotor ;
    :partOf :CarModelS ;
    :poweredBy :BatteryPack .
```

The schematic preserves the spatial and structural information that would be awkward to express entirely as triples. The knowledge graph preserves the identity and meaning of each component.

### Anchoring Diagram Elements to Knowledge Graph Entities

For greater precision, identifiable elements within the schematic can be linked directly to nodes in the graph. SVG files are especially useful because each visual element can have a stable identifier.

```turtle
:BatteryPackAnchor
    a :SchematicAnchor ;
    :belongsToSchematic :ModelS_ChassisSchematic ;
    :identifiesEntity :BatteryPack ;
    :svgElementId "battery-pack-01" .

:FrontMotorAnchor
    a :SchematicAnchor ;
    :belongsToSchematic :ModelS_ChassisSchematic ;
    :identifiesEntity :FrontMotor ;
    :svgElementId "front-motor-01" .
```

A user could select the battery pack in the drawing and retrieve its specifications, supplier, failure history, maintenance instructions, or related risks. The schematic therefore becomes a visual index into the knowledge graph.

### Design Schematics and Individual Objects

A schematic may describe either a class of objects or one specific individual.

A design schematic describes what a type of car is expected to contain:

```turtle
:ModelSBatteryPack
    a owl:Class ;
    rdfs:subClassOf :BatteryPack .
```

An as-built schematic may identify the actual battery installed in a specific vehicle:

```turtle
:EugenesCar
    a :CarModelS ;
    :hasInstalledPart :Battery_SN84721 ;
    :hasSchematic :EugenesCar_AsBuiltSchematic .

:Battery_SN84721
    a :ModelSBatteryPack ;
    :serialNumber "84721" ;
    :installedIn :EugenesCar .
```

This is similar to the difference between a class definition and an instantiated object. The generic schematic describes the design. The as-built schematic describes what actually exists.

## Diagrams That Go Beyond Traditional Ontologies

The same pattern applies to many structures that are not traditional ontologies. These diagrams may contain nodes and relationships, but their meaning comes from arrangement, direction, sequence, dependency, or flow. A simple class hierarchy is not enough.

| Diagram type          | What it captures that a hierarchy does not                    |
| --------------------- | ------------------------------------------------------------- |
| Engineering schematic | Physical placement, assembly, and connectivity                |
| UML diagram           | Software structure, inheritance, composition, and interaction |
| Workflow              | Sequence, branching, conditions, and responsibility           |
| Strategy map          | Cause-and-effect relationships among objectives               |
| Trophic cascade       | Ecological influence across species and environmental effects |
| Network topology      | Connectivity, routing, dependency, and failure paths          |
| Process map           | Activities, decisions, handoffs, and exceptions               |
| Building plan         | Spatial relationships among rooms, systems, and equipment     |

### UML Diagrams

A UML class diagram can show inheritance, composition, interfaces, and cardinality. Some of that information can be translated into RDF or OWL, but the diagram remains valuable because it presents the overall design in a form that people can quickly understand.

```turtle
:OrderSystem
    a :SoftwareSystem ;
    :hasUMLDiagram :OrderSystemClassDiagram .

:OrderSystemClassDiagram
    a :UMLClassDiagram ;
    :fileLocation <https://example.org/order-system.svg> ;
    :depictsEntity :Order ;
    :depictsEntity :Customer ;
    :depictsEntity :OrderLine .
```

The classes in the diagram may also be linked to source code, database tables, APIs, and documentation:

```turtle
:Order
    a :SoftwareClass ;
    :implementedInFile <https://example.org/src/Order.cs> ;
    :storedInTable :OrdersTable ;
    :depictedIn :OrderSystemClassDiagram .
```

The graph can answer questions about the class, while the UML diagram shows how the design fits together.

### Workflows

A workflow does more than classify activities. It shows what happens first, what follows, where decisions occur, and which paths are possible.

```turtle
:LoanApprovalProcess
    a :BusinessProcess ;
    :hasWorkflowDiagram :LoanApprovalWorkflow .

:LoanApprovalWorkflow
    a :WorkflowDiagram ;
    :depictsStep :ReceiveApplication ;
    :depictsStep :CheckCredit ;
    :depictsStep :ApproveLoan .
```

The graph may explicitly represent important transitions:

```turtle
:ReceiveApplication
    :nextStep :CheckCredit .

:CheckCredit
    :onPass :ApproveLoan ;
    :onFail :ManualReview .
```

The workflow diagram preserves the complete visual flow, including branches, loops, swim lanes, and exceptions. The knowledge graph provides semantic links to employees, policies, applications, risks, and performance measures.

### Strategy Maps

A strategy map is not primarily a taxonomy. It represents hypotheses about how one objective contributes to another.

```turtle
:CorporateStrategy
    a :Strategy ;
    :hasStrategyMap :GrowthStrategyMap .

:GrowthStrategyMap
    a :StrategyMap ;
    :includesObjective :ImproveEmployeeSkills ;
    :includesObjective :ImproveCustomerService ;
    :includesObjective :IncreaseRevenue .
```

The causal chain can be represented in the graph:

```turtle
:ImproveEmployeeSkills
    :contributesTo :ImproveCustomerService .

:ImproveCustomerService
    :contributesTo :IncreaseCustomerRetention .

:IncreaseCustomerRetention
    :contributesTo :IncreaseRevenue .
```

The diagram shows the proposed chain of influence across learning, operations, customers, and financial outcomes. The graph can connect each objective to KPIs, responsible departments, initiatives, assumptions, and supporting evidence.

### Trophic Cascades

A trophic cascade describes how changes involving one species can indirectly affect many others. A hierarchy may classify wolves, elk, plants, and rivers, but it does not capture the dynamic chain among them.

```turtle
:YellowstoneCascade
    a :EcologicalModel ;
    :hasDiagram :YellowstoneTrophicCascadeDiagram .

:Wolf
    :preysOn :Elk .

:Elk
    :feedsOn :Willow .

:WolfPopulationIncrease
    :reduces :ElkBrowsing ;
    :indirectlySupports :WillowGrowth .
```

The diagram can show the direction and sign of each effect, including indirect relationships:

```turtle
:WillowGrowth
    :supports :BeaverPopulation .

:BeaverPopulation
    :affects :WetlandFormation .
```

The graph preserves the explicit entities and relationships. The trophic cascade diagram makes the broader chain of ecological consequences easier to see.

### Network and Infrastructure Diagrams

A network topology may show servers, routers, firewalls, data stores, and communication paths.

```turtle
:ProductionEnvironment
    a :ITEnvironment ;
    :hasTopologyDiagram :ProductionNetworkDiagram .

:WebServer01
    a :WebServer ;
    :connectsTo :ApplicationServer01 .

:ApplicationServer01
    :connectsTo :CustomerDatabase .
```

The topology diagram adds placement, zones, boundaries, redundancy, and traffic direction. The graph can add operational information such as ownership, patch status, vulnerabilities, dependencies, and incident history.

## The Diagram as a First-Class Node

It is possible to store a diagram merely as a file property:

```turtle
:CarModelS
    :schematicFile <https://example.org/model-s.svg> .
```

However, a stronger approach is to make the diagram itself a node:

```turtle
:CarModelS
    :hasSchematic :ModelS_ChassisSchematic .

:ModelS_ChassisSchematic
    a :EngineeringSchematic ;
    :fileLocation <https://example.org/model-s.svg> ;
    :version "3.2" ;
    :createdBy :EngineeringDepartment ;
    :effectiveDate "2026-05-01"^^xsd:date ;
    :depicts :CarModelS .
```

The diagram can then have its own metadata, version history, provenance, access rules, annotations, and relationships to the entities it depicts.

This is especially important when multiple diagrams describe the same object from different perspectives:

```turtle
:CarModelS
    :hasSchematic :ElectricalSchematic ;
    :hasSchematic :CoolingSystemSchematic ;
    :hasSchematic :ChassisAssemblyDiagram ;
    :hasSchematic :RepairPartsDiagram .
```

Each representation answers a different kind of question.

## Why Keep the Original Artifact?

A knowledge graph could attempt to convert every line, symbol, connector, and position into triples. In some cases that may be useful, but it is rarely necessary to reproduce the complete artifact.

A diagram often contains meaning through:

* spatial arrangement,
* proximity,
* visual grouping,
* direction,
* sequence,
* containment,
* shape,
* scale,
* color,
* and notation conventions.

Much of that meaning is difficult to preserve naturally in a traditional ontology.

The more practical approach is to keep both:

1. The original diagram or model as the rich source artifact.
2. The knowledge graph representation of its important entities, relationships, and metadata.

The external artifact preserves detail and context. The knowledge graph makes its contents searchable, linkable, governable, and available for reasoning.

A useful general term for this pattern is a **semantic schematic**:

> A semantic schematic is a visual or structured representation whose identifiable elements are linked to entities in a knowledge graph.

This pattern can apply to engineering drawings, workflows, UML diagrams, strategy maps, trophic cascades, organizational charts, building plans, process maps, and many other representations in which labels and class hierarchies alone are not enough.
