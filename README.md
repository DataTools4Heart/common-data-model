# Common Data Model For Heart Failure Research

<div align="center" style="background-color: white">
  <a href="https://www.datatools4heart.eu/">
    <img height="60px" src="readme-assets/dt4h_logo_color.svg" alt="DataTools4Heart Project"/>
  </a>
  &nbsp; &nbsp; &nbsp; &nbsp;
  <a href="https://www.ai4hf.com/">
    <img height="60px" src="readme-assets/ai4hf_logo.svg" alt="AI4HF Project"/>
  </a>
</div>

<br/>

<p align="center">
  <a href="https://github.com/DataTools4Heart/common-data-model">
    <img src="https://img.shields.io/github/license/DataTools4Heart/common-data-model" alt="License">
  </a>
  <a href="https://img.shields.io/github/license/DataTools4Heart/releases">
    <img src="https://img.shields.io/github/v/release/DataTools4Heart/common-data-model" alt="Releases">
  </a>
</p>

<br/>

This repository includes the FHIR profile definitions, code systems and value sets which constitute the Common Health
Data Model
used for heart failure research. The profiling was performed with respect to the data requirements originated from the
use-case
scenarios of the [DataTools4Heart](https://www.datatools4heart.eu/) and [AI4HF](https://www.ai4hf.com/) projects.

### Profiles

Profiles are well-defined HL7-FHIR-based representations of healthcare resources, such as conditions, lab measurements
or medications. Profiles are used to enforce syntactic and semantic restrictions on resource definitions such as
cardinality of a
particular element and/or code systems to be used for a coded value.

Standard terminology system that are used in Heart Failure Resarch CDM:

* ICD-10: conditions (diagnosis)
* ICD-10-PCS: procedures
* LOINC: lab, echo and ECG measurements,
* ATC: medications
* SNOMED-CT: symptoms

### Value sets

Value sets are used to restrict values that can be specified for specific elements of healthcare resources.
For instance, we have an HL7 FHIR Observation-based profile for New York Heart Association (NYHA) classification, for
which we
would like to restrict possible values with the four pre-defined classes: I, II, III and IV.

### Code systems

Code systems are a group of codes defined in the scope of DT4H & AI4HF projects for coded representation of particular
concepts.
For instance, we have defined a code system containing coded values for some echocardiogram measurements that do not
have a
corresponding code in the available standard-based terminology systems, such as LOINC.
