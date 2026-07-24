# Pattern: Informal implementation guidance as a substitute for governed knowledge

## Context

Customers require concrete guidance that goes beyond product documentation. Experienced employees possess working examples derived from previous customer engagements.

## Organizational response

Formal, reusable playbooks are held for Product and Engineering review. Meanwhile, employees continue answering customer questions through:

* Slack messages;
* links to customer or demonstration environments;
* remembered implementation details;
* isolated code or markup examples;
* verbal consultation;
* private files and individual expertise.

## Example

For an iframe implementation, Tracy provided:

* the required `<object>` element;
* the necessary `outputclass="iframe"` value;
* a working source example;
* the rendered Portal URL;
* an informal statement of the acceptable implementation boundary.

Functionally, this was a small implementation playbook, but it was not identified, reviewed, versioned, ranked, or stored as shared institutional guidance.

## Why the pattern persists

Informal guidance feels lower-risk because it is conversational and comes from a trusted expert. It does not look like an official deliverable and therefore avoids triggering the formal review concern attached to a packaged playbook.

This allows the organization to satisfy immediate customer needs without confronting the unresolved governance problem.

## Consequences

* Knowledge remains associated with particular employees.
* Consultants must know whom to ask.
* Different customers may receive different answers.
* Examples are not systematically tested or maintained.
* Product changes do not trigger updates to scattered guidance.
* Limitations and support boundaries may not be recorded.
* Prior customer solutions may be referenced without consistent review of what is safe to reuse.
* Successful patterns do not become searchable institutional knowledge.
* Repeated work is rediscovered rather than reused.
* The company has limited visibility into what implementation guidance is already being shared.
* The formal review hold creates the appearance of control without controlling the actual information flow.

## Resulting risk

The organization avoids the visible risk of distributing a governed playbook while accepting the less visible risks of informal, inconsistent, and unaudited implementation guidance.

In short:

> The prohibition does not prevent solution patterns from being shared. It prevents them from being shared consistently, transparently, and governably.

That is the central contradiction. Heretto can safely imagine that unreviewed implementation guidance is not leaving the organization because no formal artifact has been released. In reality, useful examples must circulate for consulting to function. They circulate through Slack, meetings, employee memory, and existing customer implementations.

The playbook library would make this existing practice legible:

* where the pattern came from;
* what it contains;
* what was validated;
* who reviewed it;
* how mature it is;
* what limitations apply;
* when it needs reconsideration.

So you are not arguing for replacing control with unrestricted sharing. You are documenting how the current restriction displaces information sharing into a less controlled form. The organization can either govern the practice it already depends upon or continue pretending that informal examples are categorically different from implementation guidance.

https://heretto.slack.com/archives/C06TEBSHL7R/p1784829951579509?thread_ts=1784828990.906509&cid=C06TEBSHL7R