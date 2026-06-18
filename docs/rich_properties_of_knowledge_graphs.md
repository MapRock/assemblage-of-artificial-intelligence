# Appendix F – Rich Properties

## F.1 Beyond Simple Properties

Knowledge graphs are usually introduced through relatively simple properties:

```turtle
:EugenesCar
    :manufacturer :Honda ;
    :modelName "Accord" ;
    :modelYear "2024"^^xsd:gYear .
```

These properties work well for values and relationships that can be represented clearly as literals or links to other entities. However, not every important property can be adequately expressed as a string, number, class, or ordinary relationship.

A car may also have:

* an engineering schematic;
* a three-dimensional CAD model;
* a wiring diagram;
* a maintenance manual;
* a photograph;
* a diagnostic recording;
* or a simulation model.

These artifacts may contain spatial, visual, temporal, mathematical, or procedural knowledge that would be difficult—and sometimes pointless—to reproduce completely as RDF triples.

In this book, I use the term **rich property** for this pattern:

> A rich property is an external digital artifact—such as a diagram, model, document, recording, or executable object—that describes an entity more fully than ordinary RDF literals and relationships can. The artifact remains in its native format, while the knowledge graph records its identity, metadata, meaning, and links to important elements within it.

The individual mechanisms behind this idea are not new. RDF has always allowed one resource to link to another resource. Media annotation, digital twins, model registries, document management, and engineering systems all use related patterns. What is less commonly emphasized is that these different artifacts form one general category: properties whose knowledge is too rich to flatten entirely into ordinary graph statements.

## F.2 The Artifact as a First-Class Node

The simplest approach is to attach a file location directly to an entity:

```turtle
:EugenesCar
    :schematicFile <https://example.org/eugenes-car.svg> .
```

This identifies the file, but it tells us little about it. A stronger approach is to represent the schematic itself as a node:

```turtle
:EugenesCar
    :hasSchematic :EugenesCarSchematic .

:EugenesCarSchematic
    a :EngineeringSchematic ;
    :fileLocation <https://example.org/eugenes-car.svg> ;
    :version "3.1" ;
    :createdBy :EngineeringDepartment ;
    :effectiveDate "2026-05-01"^^xsd:date ;
    :depicts :EugenesCar .
```

The schematic can now have its own:

* identity;
* format;
* author;
* version;
* creation date;
* provenance;
* access rules;
* lifecycle status;
* and relationships to the entities it depicts.

The rich property is therefore not merely an attachment. It becomes a governed and graph-addressable resource.

## F.3 Engineering Schematics

Some objects are best understood visually. A car schematic can identify the engine, battery, suspension, wiring, and other parts while showing where those parts are located and how they fit together.

A class hierarchy may tell us that an electric motor is a kind of vehicle component. It does not naturally show where the motor is located, how it connects to the battery, or which assemblies must be removed to reach it.

```turtle
:CarModelS
    a :VehicleModel ;
    :hasSchematic :ModelSChassisSchematic .

:ModelSChassisSchematic
    a :EngineeringSchematic ;
    :fileLocation <https://example.org/model-s-chassis.svg> ;
    :depictsPart :BatteryPack ;
    :depictsPart :FrontMotor ;
    :depictsPart :RearMotor .
```

The depicted parts may also be explicit knowledge graph entities:

```turtle
:BatteryPack
    a :VehicleComponent ;
    :partOf :CarModelS .

:FrontMotor
    a :ElectricMotor ;
    :partOf :CarModelS ;
    :poweredBy :BatteryPack .
```

The schematic preserves physical placement, geometry, and assembly context. The knowledge graph preserves identity, classification, relationships, and facts about each component.

## F.4 Anchoring Elements Within a Rich Property

The graph can link not only to the entire artifact but also to identifiable elements within it. SVG is especially useful because individual visual elements can have stable identifiers.

```turtle
:BatteryPackAnchor
    a :SchematicAnchor ;
    :belongsToSchematic :ModelSChassisSchematic ;
    :identifiesEntity :BatteryPack ;
    :svgElementID "battery-pack-01" .

:FrontMotorAnchor
    a :SchematicAnchor ;
    :belongsToSchematic :ModelSChassisSchematic ;
    :identifiesEntity :FrontMotor ;
    :svgElementID "front-motor-01" .
```

The SVG might contain:

```xml
<g id="battery-pack-01">...</g>
<g id="front-motor-01">...</g>
```

A user could select the battery pack in the drawing and retrieve:

* its specifications;
* supplier;
* maintenance procedures;
* replacement history;
* failure risks;
* compatible parts;
* and vehicles in which it is installed.

The schematic becomes a **visual index into the knowledge graph**.

This resembles established semantic-media annotation practices, where a graph entity is connected to a region of an image, a portion of a document, or a segment of audio or video. The broader rich-property pattern applies the same idea to many kinds of structured artifacts.

## F.5 Design Schematics and As-Built Schematics

A rich property may describe either a class of objects or a specific individual.

A generic schematic describes the intended design of a vehicle model:

```turtle
:ModelSBatteryPack
    a owl:Class ;
    rdfs:subClassOf :BatteryPack .
```

An as-built schematic can describe the actual components installed in one vehicle:

```turtle
:EugenesCar
    a :CarModelS ;
    :hasInstalledPart :BatterySN84721 ;
    :hasSchematic :EugenesCarAsBuiltSchematic .

:BatterySN84721
    a :ModelSBatteryPack ;
    :serialNumber "84721" ;
    :installedIn :EugenesCar .
```

The design schematic describes what a type of object is expected to contain. The as-built schematic describes what actually exists.

This is comparable to the distinction between a class definition and an instantiated object.

## F.6 Multiple Views of the Same Entity

One object may have several rich properties, each offering a different view:

```turtle
:CarModelS
    :hasSchematic :ElectricalSchematic ;
    :hasSchematic :CoolingSystemSchematic ;
    :hasSchematic :ChassisAssemblyDiagram ;
    :hasSchematic :RepairPartsDiagram ;
    :hasModel :ModelS3DCADModel .
```

Each artifact answers different questions.

| Rich property        | Primary purpose                                             |
| -------------------- | ----------------------------------------------------------- |
| Electrical schematic | Wiring, circuits, connectors, and current paths             |
| Cooling schematic    | Coolant flow, pumps, radiators, and dependencies            |
| Assembly diagram     | Physical placement and part assembly                        |
| Repair-parts diagram | Replaceable components and part numbers                     |
| 3D CAD model         | Geometry, dimensions, clearances, and spatial relationships |

No single representation is necessarily the complete truth. Each is a view of the same entity created for a particular purpose.

## F.7 Structures Beyond Traditional Ontologies

Rich properties are especially useful for graphs and diagrams that are not simply taxonomies or traditional ontologies.

A taxonomy answers questions such as:

> What kind of thing is this?

An ontology can add:

> What properties and relationships may this kind of thing have?

However, many useful knowledge structures also depend on:

* direction;
* sequence;
* placement;
* geometry;
* flow;
* dependency;
* feedback;
* cardinality;
* visual grouping;
* or hypothesized cause and effect.

Labels and class hierarchies alone are not enough.

| Diagram or model      | Knowledge not adequately captured by a class hierarchy |
| --------------------- | ------------------------------------------------------ |
| Engineering schematic | Placement, assembly, interfaces, and connectivity      |
| UML diagram           | Composition, inheritance, interfaces, and cardinality  |
| Workflow              | Sequence, branching, roles, loops, and exceptions      |
| Strategy map          | Intended influence among strategic objectives          |
| Trophic cascade       | Direct and indirect ecological effects                 |
| Network topology      | Routing, zones, redundancy, and failure paths          |
| Building plan         | Spatial layout, containment, and access                |
| Process map           | Activities, decisions, handoffs, and bottlenecks       |
| Neural network        | Layers, weights, activations, and learned behavior     |
| Simulation model      | Dynamic behavior under changing inputs                 |

These structures may themselves be graph-shaped, but they are not necessarily ontologies. A graph is a general data structure. An ontology is one particular use of a graph for defining concepts and formal relationships.

## F.8 UML Diagrams

A UML class diagram can show inheritance, composition, interfaces, associations, and cardinality. Much of this information can be translated into graph statements, but the visual diagram remains valuable because it presents the software design as an integrated whole.

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

The depicted classes can link to other resources:

```turtle
:Order
    a :SoftwareClass ;
    :implementedInFile <https://example.org/src/Order.cs> ;
    :storedInTable :OrdersTable ;
    :depictedIn :OrderSystemClassDiagram .
```

The graph can answer detailed questions about `:Order`. The UML diagram shows how `:Order` fits into the broader design.

A future system might allow a user to click a UML class and move directly to:

* its source file;
* database table;
* API endpoints;
* unit tests;
* documentation;
* known defects;
* and responsible development team.

## F.9 Workflows

A workflow does more than classify activities. It shows what happens first, what follows, where decisions occur, and which paths are possible.

```turtle
:LoanApprovalProcess
    a :BusinessProcess ;
    :hasWorkflowDiagram :LoanApprovalWorkflow .

:LoanApprovalWorkflow
    a :WorkflowDiagram ;
    :depictsStep :ReceiveApplication ;
    :depictsStep :CheckCredit ;
    :depictsStep :ApproveLoan ;
    :depictsStep :ManualReview .
```

Important transitions can also be represented explicitly:

```turtle
:ReceiveApplication
    :nextStep :CheckCredit .

:CheckCredit
    :onPass :ApproveLoan ;
    :onFail :ManualReview .
```

The graph representation allows the process to be queried and reasoned over. The original workflow preserves:

* branches;
* loops;
* decision symbols;
* swim lanes;
* timing expectations;
* exceptions;
* and the overall visual path.

The workflow may also link each step to policies, roles, systems, event types, KPIs, and historical process-mining results.

## F.10 Strategy Maps

A strategy map is not primarily a taxonomy. It represents a set of hypotheses about how one objective contributes to another.

```turtle
:CorporateStrategy
    a :Strategy ;
    :hasStrategyMap :GrowthStrategyMap .

:GrowthStrategyMap
    a :StrategyMap ;
    :includesObjective :ImproveEmployeeSkills ;
    :includesObjective :ImproveCustomerService ;
    :includesObjective :IncreaseCustomerRetention ;
    :includesObjective :IncreaseRevenue .
```

The intended chain can be represented in the graph:

```turtle
:ImproveEmployeeSkills
    :contributesTo :ImproveCustomerService .

:ImproveCustomerService
    :contributesTo :IncreaseCustomerRetention .

:IncreaseCustomerRetention
    :contributesTo :IncreaseRevenue .
```

However, the map may also communicate meaning through layout. Objectives may be grouped into perspectives such as:

* learning and growth;
* operations;
* customers;
* and financial performance.

The strategy map preserves the executive-level view. The graph can connect each objective to:

* KPIs;
* responsible departments;
* initiatives;
* assumptions;
* evidence;
* risks;
* and observed results.

The relationships in a strategy map should not automatically be treated as proven causation. They may be hypotheses that the organization intends to test. The graph can record that distinction:

```turtle
:EmployeeSkillsToCustomerService
    a :StrategicHypothesis ;
    :sourceObjective :ImproveEmployeeSkills ;
    :targetObjective :ImproveCustomerService ;
    :confidence 0.72 ;
    :supportedBy :EmployeeCustomerStudy2025 .
```

## F.11 Trophic Cascades

A trophic cascade describes how a change involving one species can indirectly affect many others.

A taxonomy can classify wolves, elk, willow trees, and beavers. It does not adequately express the dynamic sequence of effects among them.

```turtle
:YellowstoneCascade
    a :EcologicalModel ;
    :hasDiagram :YellowstoneTrophicCascadeDiagram .

:Wolf
    :preysOn :Elk .

:Elk
    :feedsOn :Willow .
```

The broader effects may also be represented:

```turtle
:WolfPopulationIncrease
    :reduces :ElkBrowsing .

:ReducedElkBrowsing
    :supports :WillowGrowth .

:WillowGrowth
    :supports :BeaverPopulation .

:BeaverPopulation
    :affects :WetlandFormation .
```

The knowledge graph makes the relationships explicit and queryable. The trophic-cascade diagram makes the chain of direct and indirect effects easier to see as a whole.

It may also distinguish positive and negative effects:

```turtle
:WolfPopulationIncrease
    :hasEffect [
        a :NegativeEffect ;
        :affects :ElkPopulation
    ] .

:ReducedElkBrowsing
    :hasEffect [
        a :PositiveEffect ;
        :affects :WillowGrowth
    ] .
```

The original diagram may communicate effect direction, strength, uncertainty, and ecological layers more effectively than a list of triples.

## F.12 Network and Infrastructure Diagrams

A network topology may show servers, routers, firewalls, data stores, security zones, and communication paths.

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

The topology diagram may additionally show:

* internal and external network zones;
* load balancers;
* redundant routes;
* firewall boundaries;
* traffic direction;
* cloud regions;
* and failover paths.

The graph can link the depicted devices to operational knowledge:

```turtle
:ApplicationServer01
    :ownedBy :ApplicationOperations ;
    :runsSoftware :OrderService ;
    :hasPatchStatus :Current ;
    :dependsOn :CustomerDatabase ;
    :depictedIn :ProductionNetworkDiagram .
```

The rich property preserves the architectural view. The graph adds ownership, vulnerabilities, incidents, dependencies, configuration, and governance.

## F.13 Building Plans

A building plan communicates spatial knowledge that is difficult to express naturally through class hierarchies.

```turtle
:Headquarters
    a :OfficeBuilding ;
    :hasFloorPlan :FirstFloorPlan .

:FirstFloorPlan
    a :BuildingPlan ;
    :depictsRoom :ConferenceRoomA ;
    :depictsRoom :ServerRoom ;
    :depictsAsset :FireExtinguisher17 .
```

The graph may express containment:

```turtle
:ServerRoom
    :partOf :Headquarters ;
    :locatedOn :FirstFloor .

:Firewall01
    :locatedIn :ServerRoom .
```

But the original floor plan retains:

* exact placement;
* dimensions;
* entrances;
* exits;
* adjacency;
* wall boundaries;
* evacuation routes;
* and physical access paths.

A region within the floor plan could be anchored to `:ServerRoom`, allowing a user to click the room and retrieve its devices, access controls, environmental sensors, and maintenance history.

## F.14 Machine-Learning Models as Rich Properties

A trained machine-learning model is another example of knowledge that cannot be usefully reduced to a handful of literals.

```turtle
:CustomerChurnProcess
    :hasPredictiveModel :ChurnModelV3 .

:ChurnModelV3
    a :MachineLearningModel ;
    :modelType :GradientBoostedTree ;
    :fileLocation <https://example.org/models/churn-v3.pkl> ;
    :trainedOn :CustomerTrainingDataset ;
    :predicts :CustomerChurnProbability ;
    :version "3.0" .
```

The graph can describe the model, but the actual learned structure remains in the pickle, ONNX, PMML, or other model file.

The model may be connected to:

* input features;
* output values;
* training data;
* evaluation metrics;
* model owner;
* deployment endpoint;
* applicable populations;
* and known limitations.

```turtle
:ChurnModelV3
    :hasInputFeature :DaysSinceLastPurchase ;
    :hasInputFeature :SupportCallCount ;
    :hasOutput :ChurnProbability ;
    :hasAccuracy 0.87 ;
    :deployedAt <https://example.org/api/churn-v3> .
```

A decision tree might be partially converted to explicit rules. A neural network may not be usefully reducible in that manner. Retaining the original artifact allows investigators to return to the full model—the equivalent of going back to the scene of the crime.

## F.15 Audio, Video, and Signals

Audio and video contain detail that words alone cannot fully explain.

```turtle
:EngineSN4421
    :hasDiagnosticRecording :EngineRecording20260601 .

:EngineRecording20260601
    a :AudioRecording ;
    :fileLocation <https://example.org/audio/engine-4421.wav> ;
    :recordedOn "2026-06-01"^^xsd:date ;
    :indicates :PossibleBearingFailure .
```

The KG might store extracted properties such as:

```turtle
:EngineRecording20260601
    :dominantFrequency "184.2"^^xsd:decimal ;
    :hasSpectralModel :EngineRecordingFourierTransform .
```

The Fourier transform is itself another representation of the recording:

```turtle
:EngineRecordingFourierTransform
    a :FrequencyDomainRepresentation ;
    :derivedFrom :EngineRecording20260601 ;
    :fileLocation <https://example.org/signals/engine-4421-spectrum.parquet> .
```

The recording preserves the sound. The Fourier representation exposes frequency structure. The graph preserves identity, provenance, interpretation, and relationships to the equipment and diagnosis.

No one representation replaces the others.

## F.16 Native Artifact and Graph Extraction

A rich property can be represented at several levels:

| Level             | Description                                                                        |
| ----------------- | ---------------------------------------------------------------------------------- |
| Native artifact   | The original SVG, CAD file, PDF, video, model, or recording                        |
| Artifact metadata | Format, version, creator, location, date, provenance, and access                   |
| Semantic anchors  | Links from regions or components within the artifact to KG entities                |
| Extracted graph   | Important facts translated from the artifact into explicit nodes and relationships |

For example, a workflow can remain as a BPMN file while its most important steps and transitions are also represented in RDF.

The decision is not between storing the artifact or graphing it. A useful implementation usually does both.

The artifact preserves the original representation. The graph exposes the parts needed for:

* discovery;
* integration;
* querying;
* governance;
* reasoning;
* and AI retrieval.

## F.17 Why Not Convert Everything to Triples?

In theory, every line, coordinate, pixel, neural-network weight, and audio sample could be represented as triples. That would not necessarily make the knowledge more useful.

A diagram often communicates through:

* spatial arrangement;
* proximity;
* visual grouping;
* direction;
* sequence;
* containment;
* shape;
* scale;
* color;
* notation;
* and the interaction of all those elements.

Flattening everything into triples can obscure the whole while producing an enormous quantity of low-value graph data.

The graph should generally extract what needs to be identified, linked, queried, governed, or reasoned over. The original artifact should preserve the rest.

This is a division of labor:

> The artifact preserves fidelity. The knowledge graph preserves semantic accessibility.

## F.18 Relationship to Established Practices

The idea of rich properties intersects several established areas.

| Established area             | Related practice                                                            |
| ---------------------------- | --------------------------------------------------------------------------- |
| RDF and Linked Data          | Representing artifacts as identifiable resources                            |
| Web annotation               | Linking KG entities to regions or segments of media                         |
| Digital twins                | Connecting physical assets to models, simulations, and observations         |
| Product lifecycle management | Managing engineering drawings, CAD models, and versions                     |
| Model registries             | Governing trained machine-learning models and deployments                   |
| Document management          | Linking entities to manuals, reports, and records                           |
| Process management           | Connecting business processes to BPMN and workflow artifacts                |
| Geospatial systems           | Linking entities to maps, layers, and geometry                              |
| Media knowledge graphs       | Connecting people, events, and concepts to image, audio, and video segments |

The individual practices are therefore well established.

The term **rich property**, however, is not standard knowledge-graph vocabulary with this exact meaning. In other contexts, it might be interpreted as a JSON-valued property, an RDF-star annotation, or a graph property with several internal fields.

For that reason, the term should be explicitly defined as it is used in this book.

The broader contribution is the synthesis: recognizing that an engineering schematic, UML diagram, strategy map, trophic cascade, workflow, neural network, recording, and simulation model all follow a common architectural pattern.

Each is a representation of knowledge that can be linked to the graph without pretending that all of its meaning must first be converted into an ontology.

## F.19 Semantic Schematics

A useful subtype of rich property is the **semantic schematic**:

> A semantic schematic is a visual or structured representation whose identifiable elements are linked to entities in a knowledge graph.

Examples include:

* a vehicle schematic whose parts link to component entities;
* a building plan whose rooms link to locations and assets;
* a UML diagram whose classes link to source code and database tables;
* a workflow whose steps link to events, roles, and policies;
* a strategy map whose objectives link to KPIs and initiatives;
* and a trophic cascade whose species and effects link to ecological observations.

A semantic schematic is more than an illustration. It is an alternate interface to the knowledge graph and an alternate representation of knowledge.

## F.20 Conclusion

Knowledge graphs are powerful because they make identity, meaning, and relationships explicit. They should not, however, be treated as the only useful representation of knowledge.

Some knowledge is inherently visual. Some is spatial. Some is temporal, mathematical, procedural, or executable. A rich property allows that knowledge to remain in the representation best suited to it while still participating in the larger knowledge graph.

The knowledge graph does not need to reproduce every detail of a schematic, model, recording, or diagram. It needs to know:

* what the artifact is;
* what it describes;
* where it came from;
* which version is authoritative;
* and how its important elements connect to the rest of the graph.

The external artifact preserves nuance and fidelity. The knowledge graph provides identity, context, governance, integration, and reasoning.

Together, they describe more than either could describe alone.
