# DataTools4Heart Common Data Model (DT4H CDM)
This repository Keeps the FHIR profiles, code systems and value sets composing the DT4H CDM.

* Profiles
Profiles are well-defined HL7-FHIR-based representations of healthcare resources, such as conditions, lab measurements or medications that are used in the DT4H project.
Profiles are used to enforce syntactic and semantic restrictions on resource definitions such as cardinality of a particular element and
code systems to be used for a coded value, respectively.

  * Standard terminology system that are used in DT4H:
    * ICD-10: conditions (diagnosis)
    * ICD-10-PCS: procedures
    * LOINC: lab, echo and ECG measurements, 
    * ATC: medications 
    * SNOMED-CT: symptoms

* Value sets
Value sets are used to restrict values that can be specified for specific elements of healthcare resources.
For instance, we have an HL7 FHIR Observation-based profile for New York Heart Assessment measurements, for which we would like
to restrict possible values with the four pre-defined categorized ones, I, II, III and IV.

* Code systems
Code systems are a group of codes defined in the scope of DT4H for coded representation of a particular concept.
For instance, we have defined a code system containing coded values for some echocardiogram measurements that do not have a
corresponding code in the available standard-based terminology systems.
