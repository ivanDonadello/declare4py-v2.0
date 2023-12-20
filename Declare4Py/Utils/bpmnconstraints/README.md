# BPMN2Constraints
[![REUSE status](https://api.reuse.software/badge/github.com/signavio/bpmn2constraints)](https://api.reuse.software/info/github.com/signavio/bpmn2constraints)
![Python](https://img.shields.io/badge/python-3.8-blue.svg)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

Tool for compiling BPMN models directly to constraints.
Currently, BPMN2Constraints can compile BPMN models stored in both `JSON` and `XML`
format and output to `DECLARE`, `SIGNAL`
and `Linear Temporal Logic on Finite Traces` (LTLf).
BPMN2Constraints can also compile BPMN diagrams to Mermaid.js compatible flowcharts.

The original repository is available [here](https://github.com/signavio/bpmn2constraints), 
and is developed by SAP Signavio.

A tutorial that provides a walk-through of how to use the tool in
an SAP Signavio context is provided [here](./tutorial/tutorial.ipynb).


## Acknowledgements.
This project has been authored by:
- Arvid Bergman ([@arvidbt](https://github.com/arvidbt)),
- Timotheus Kampik ([@TimKam](https://github.com/TimKam)),
- Adrian Rebmann ([@adrianrebmann](https://github.com/adrianrebmann)).
And integrated into Declare4Py by:
- Marcus Rost ([@marcusrostSAP](https://github.com/MarcusRostSAP)).