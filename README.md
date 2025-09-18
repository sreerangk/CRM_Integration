# Django CRM Integration System

A scalable Django application that integrates with multiple CRM systems (HubSpot, Zoho) to synchronise file attachments and metadata to a local database.

# Features

-  Multiple CRM support (HubSpot, Zoho) with extensible architecture
-  File synchronisation with duplicate handling
-  RESTful API endpoints for file management
-  Advanced filtering and search capabilities
-  Comprehensive error handling and logging
-  Management commands for CLI operations
-  Mock CRM services for development/testing (no real CRM accounts needed)
-  Periodic Task Scheduling - Automated maintenance operations(using celery)

# Quick Setup

## 1. Install Dependencies
```bash
pip install -r requirements.txt
```
## 2. Database Setup
```bash
python manage.py makemigrations file_synch
python manage.py migrate
```

## 3. Initialise CRM Providers

```bash
python manage.py setup_crm_providers
```

## 4. Start Development Server

```bash
bashpython manage.py runserver
```

# API Endpoints

- For Api Endpoints refer Postman collection

# Management Commands

## Sync all providers
```bash
python manage.py sync_crm_files --all
```
## Sync specific provider
```bash
python manage.py sync_crm_files --provider hubspot
```
## Sync specific files
```bash
python manage.py sync_crm_files --provider hubspot --files file1 file2
```
# Testing
## Run all tests
```bash
python manage.py test file_synch
```
## Run specific test modules
```bash
python manage.py test file_synch.tests.test_models
python manage.py test file_synch.tests.test_services
python manage.py test file_synch.tests.test_views
```

# Mock CRM Data
The system uses mock CRM services that generate realistic test data:

-HubSpot Mock: Generates 4 deals with 2-4 files each (PDFs, DOCX, XLSX, images)
-Zoho Mock: Generates 5 deals with 1-5 files each with different naming conventions
-File Types: PDF contracts, Word documents, Excel sheets, images, text files
-Realistic Sizes: 10KB to 800KB with variation

# Database Schema Design

Entity Relationship Design
CRMProvider (1) ──────── (N) Deal (1) ──────── (N) FileMetadata
     │                                               │
     └─────────────── (N) SyncLog ──────────────────┘


# -- Project Submission Summary --

## Approach Summary

The project follows a clean, layered architecture with a focus on scalability and maintainability. I built a base service class that defines a common interface for CRM integrations, so adding new providers is straightforward without touching the core business logic. This keeps the system organized, flexible, and easy to extend.

Since I couldn’t use real CRM accounts, I created detailed mock services that generate realistic data—different file types, sizes, and response times. These mocks helped test the full sync flow under near-real conditions. The database design ensures data integrity with unique constraints, indexing for performance, and clean APIs that expose file discovery, sync, and management features. Logging, error handling, and management commands make the system feel production-ready, even with mocks.

Key Assumptions and Trade-offs

I assumed CRM APIs provide stable IDs, that metadata is more useful than full file storage, and that scale will be in the thousands (not millions) of files. For trade-offs, I kept the process synchronous for simplicity, though it can be extended with Celery later. Metadata was prioritized over actual file storage to avoid overhead. SQLite was used for development, but PostgreSQL would be better for production.

Overall, the system is simple to use, realistic in testing, and easy to extend with real APIs or more advanced features later.


### - Note on CRM Connection
Due to verification issues, I wasn’t able to create live HubSpot or Zoho accounts. Instead, I built realistic mock CRM services that simulate API responses, file structures, and response times. This allowed me to fully test the synchronisation workflow and keep the architecture ready for real CRM integration once valid accounts are available.
     


