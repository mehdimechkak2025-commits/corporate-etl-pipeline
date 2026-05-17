# Automated Market Intelligence ETL Pipeline 📊

## Overview
This project is an automated Data Engineering pipeline (Extract, Transform, Load) built in Python. It is designed to replace manual market research by autonomously connecting to live corporate data endpoints, structuring the raw responses, and generating actionable business intelligence.

## System Architecture
* **Extract:** Utilizes the Python `requests` library to connect to the Arbeitnow Public REST API.
* **Transform:** Ingests unstructured JSON into a `Pandas` DataFrame. The script sanitizes the data and filters for high-value data points (Title, Company, Location, Remote Status).
* **Load:** Exports the sanitized, structured database into a `.csv` file format, ready for immediate ingestion by HR departments.

## Tech Stack
* **Language:** Python 3
* **Libraries:** Pandas, Requests
* **Concepts:** REST APIs, JSON Parsing, Data Sanitation, Git Version Control