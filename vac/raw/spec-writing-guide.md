---
title: SPEC-WRITING-GUIDE
name: Specification Writing Techniques
category: Informational 
editor: Jimmy Debe <jimmy@status.im>
contributors:
---

## Abstract

The documents describes a few techniques that can be used when writing specifications.
This is an informational document and is not required the use of the following techniques.

## Background/ Motivation

Specification writing can daunting at times.
Some programmers, 
Technical or normative specifications define mandatory requirements to be implemented in systems or products.
The information should be written clearly to avoid confusion or misinterpretation.

Informational specifications offer recommended guidelines or requirements, simialar to this document. 
What is described as best practices can be used by the reader to reach a certain goal.

A normative specification may have both informational and technical information.
It is not recommended to place normative sections within an informational specifications as this may leave room for ambiguities,
but there can be references to other normative texts.

The goal of this document is to guide new and 
current specification writers with techinques of what should and
should not be included in their document.

## Specification Wrtiting

The key words “MUST”, “MUST NOT”, “REQUIRED”, “SHALL”, “SHALL NOT”, “SHOULD”,
“SHOULD NOT”, “RECOMMENDED”, “NOT RECOMMENDED”, “MAY”, and
“OPTIONAL” in this document are to be interpreted as described in [RFC 2119](https://www.ietf.org/rfc/rfc2119.txt).

### RFC Guidelines

The writer has the freedom to structure specifications as they see fit.
New specifications are meant to have errors and can be under specified.
For bett 
So following the Vac RFC guidelines is not a requirement.
The Vac RFC process follows the [1/COSS]() as guidelines when writing specifications.

### Using AI Chatbot

Creating prompts to use with Ai chatbots are a great way to start you specifcation.
The RECCOMMENDED prompt should use the following:

```text

  Please write an RFC using the Consensus-Oriented Specification System as defined here:
  https://github.com/vacp2p/rfc-index/blob/main/vac/1/coss.md.

  Background:
  - Reference materials: [links or documents]
  - Related existing standards: [standards]

  Requirements:
  - Must address: [the required features]

  Technical constraints:
  - Must use IETF RFC 2119 keywords (MUST, SHOULD, MAY, etc.) to clearly indicate requirements.

```

The prompt can be adjusted based on use.
After your initial RFC draft is created,
the writer SHOULD revisit each section to correct any statements.

An example prompt and the results can be found [here]().

### Specification Structure

The RECOMMENDED initial sections are:

- Abstract: The abstract section should not have additional sections.
- Motivation/ Background/ Goal: this may be one section or three different sections depending on your approach to best describe your topic.
- The Protocol/ Wire Specification
- Security Considerations
- Copyright
- References

Raw or proof of concepts do not need to follow the sections mentioned above,
which allows writers to try different approaches.
When a specification matures, following iterations,
the specification can begin to follow the Vac RFC Process.
Thereafter, the specification will follow the sections mentioned above.

#### Abstract

- SHOULD be the first section in your specification.
- SHOULD briefly state what the document will be specifying.

There is no fixed length requirement, but
the statements SHOULD help the reader decide if they should be reading the specification.

Technical Specifications:

- MAY include protocol identifiers
- MAY state the target audience of specification, e.g developers, researchers, implementers

If the specification is a new version of the protocol,
a reference link to the previous protocol SHOULD be included here.
References to other protocols MAY be mentioned here if it is necessary to inform the reader.
For example, if C++ experience is needed to implement the protocol.

Informational Specifications:

- MAY mention that the specification is not technical. 
- Reference to a technical specification or implementation.

#### Motivation, Background, and/or Goal

Based on the writer's choice, there MAY be one section or
separate sections,
Motivation, Background, and Goal.
Describe the topic of the specification by providing background information.
The writer SHOULD introduce or 
reintroduce the reader to all the topics that will be covered in the document.
When introducing a topic, brief explanations, two to three statements, is RECOMMENDED.
Adding references to other documents following these sentences is also RECOMMENDED. 
The writer may assume that the reader has some background understanding with the concepts that will be presented.
This may or may not be the case, in both scenarios, the writer SHOULD present all concepts, protocols, 
topics within this section before diving into the specifics.
This approach gives the reader time to evaluate what should be understood before consuming the rest of the document.

- Motivation: What was the inspiration for creating the document? 
- Background: What are the protocols/tools/infrastructure/concepts being used in the document?
- Goal: What problem is the document trying to solve and how may this be accomplished?

#### Theory or Semantics

A `stable` specification MUST have this section.
If not included in a new specification,
future iterations MAY include them.
This section SHOULD describe how the protocol works.
The writer SHOULD start to explain the technical concepts in detail,
including terms that were introduced in the Background section.
A terminology section MAY be introduced here,
which have certain definitions and terms for unique terms to the document.
This section should explicitly state all components being used.
Workflow diagrams and other requirements information can be included here.
Informational Specifications:

#### The Protocol, Wire Format, Specification

This section should not include explanations of semantics like the previous section. Some parts of the theory section can be repeated when necessary..
The reader will be using this section as a guideline for their implementation. When the reader reaches this section, all terms should have been introduced so the reader has an overall understanding of what is being specified in this section.
The use of keywords are important to use so the reader/implementer can understand which components are explicitly used, required, or not mandatory. The keywords used are: MUST, MUST NOT, REQUIRED, SHALL, SHALL NOT, SHOULD, SHOULD NOT, RECOMMENDED, NOT RECOMMENDED, MAY, and OPTIONAL.
Pseudo-code referencing an implementation should be added to help readers implement as described. Adding code from your implementation should not be added in this section. The specification should be thought of as guidelines to building your implementation, not step by step instructions to re-create or re- write your code from an implementation. 
If coding examples are required to define any components, it is best to include this in the implementation suggestions section, which follows this section.
After writing the pseudo-code, each function, variable, components, etc. should be defined. There is no required description length/method to define these objects, but the writer should explain how each object is used in the protocol, optional descriptions include: 
Why the object is being used
Using keywords, is the object required
Using keywords, if the object is required, what may occur if the object is not included in an implementation.

Informational Specifications:

#### Implementation Suggestions (Optional):

This is an optional section to further explain the components introduced in the specification section.
Technical Specifications
If a new specification does not have an implementation at time of writing this section can be omitted.
Adding code snippets can help further the readers understanding for components.

Security Suggestions:

Security suggestions are required for stable specifications. The reason for this is a specification, especially a raw/proof of concept specification, may not have enough testing that occurred that would allow suggestions to be added here.
In a new/raw/proof of concept specification, the writer may add what security suggestions are known, even if they are not valid. New specifications have room for mistakes, so adding those suggestions may be useful to the reader.
The security suggestion may have information repeated from the implementation section.
If there are no security suggestions, this section should briefly mention why there is no suggestions.

## Copyright

Copyright and related rights waived via [CC0](https://creativecommons.org/publicdomain/zero/1.0/).
All other copyright information.

## References

Place all references in a list in the order they are presented in the document.
- MUST  repeat the same links.

