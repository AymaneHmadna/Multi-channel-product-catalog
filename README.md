# Multi channel product catalog
![MongoDB](https://img.shields.io/badge/MongoDB-Document_DB-47A248?style=flat-square&logo=mongodb&logoColor=white)
![Python](https://img.shields.io/badge/Python-ETL_Engine-3776AB?style=flat-square&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Data_Processing-150458?style=flat-square&logo=pandas&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-User_Interface-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
## Overview
This multi channel product catalog system resolves the critical challenges of modern ecommerce data management. It overcomes the rigid limitations of relational databases by utilizing a NoSQL document oriented architecture to seamlessly store polymorphic product attributes without sparse data issues. Furthermore, it eliminates the risk of publishing incomplete or inaccurate information through a strict 'Draft to Live' data governance workflow. Finally, it solves the complex distribution problem by acting as a dynamic ETL engine, instantly transforming a centralized data source into tailored, channel specific formats such as nested JSON for websites and flattened CSVs for marketplaces ensuring absolute data consistency and operational efficiency across all sales platforms.

## Technology Stack & Justification
* **MongoDB (Database):** Chosen for its flexible schema, allowing the storage of polymorphic product attributes.
* **Python & Pandas (Data Processing):** Utilized as the core ETL engine. The `json_normalize` function is critical for "flattening" deeply nested JSON structures into 2D CSV files required by external marketplaces.
* **Streamlit (User Interface):** Provides a rapid, interactive CRUD (Create, Read, Update, Delete) interface for product managers.

## Core Features

### 1. Data governance & quality workflow
To prevent the distribution of incomplete data, the system implements a strict state machine (`[DRAFT]` vs `[LIVE]`). 
* A product cannot be published if mandatory fields (Price, Specific attributes based on category) are missing.
* Visual alerts block the publication process until data integrity is resolved.

### 2. Multi channel export engine
The system structures the outgoing data feed based on the target audience:
* **Ecommerce Website (JSON):** Preserves the hierarchical nested structure for modern web front ends.
* **Marketplaces (Flattened CSV):** Unpacks technical attributes (Storage, Warranty, Material) into distinct columns for strict spreadsheet based ingestion.
* **Social media (Simple CSV):** Strips the data down to the bare minimum (SKU, Name, Price, Category) for lightweight advertising algorithms.

### 3. Traceability & Indexing
* **Audit log:** All critical actions (Create, Update, Publish) are historically tracked with timestamps.
* **Optimized queries:** Implements Unique indexes (SKU) to prevent logistical duplicates and compound text indexes (Name, Brand) for high performance search capabilities.

## How to run locally

**1. Clone the repository & install dependencies**
```bash
git clone [https://github.com/AymaneHmadna/nosql-multichannel-catalog.git](https://github.com/AymaneHmadna/nosql-multichannel-catalog.git)
pip install pymongo pandas streamlit
