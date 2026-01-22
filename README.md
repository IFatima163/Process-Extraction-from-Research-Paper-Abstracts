# Process Extraction from Research Paper Abstrcts 

This code allows user to automate the repetetive task of going through every research paper abstract and picking out the methods mentioned that have been used in that paper.

## Method
Within the "data" folder:
- Insert any paper in pdf form into the "input" folder
- Receive the extracted processes in "output" folder
- Receive your processed pdf paper in the "archive" folder

## Workflow
### Input: 
PDF / DOI / text file

### Extraction: 
Locate abstract > Clean abstract text (remove citations, symbols)

### Inference: 
Identify candidate process phrases > Filter non-process terms > Normalize variants (e.g., “X-based method” vs “X method”)

### Output: 
Structured rows: paper_id, process_name, confidence_score (even rough), abstract_snippet (optional)

### Storage: 
CSV / Excel / DB > Archive processed paper