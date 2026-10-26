# DISPATER.AI Commercial Synthetic Towing Demonstration Guide

## Overview
This document outlines the 5-minute commercial demonstration procedure for towing company executives and fleet operations managers.

## 5-Minute Demonstration Script

1. **Minute 1: Record Intake**
   - Open `/dispater` and view the **Commercial Towing Field Record Audit** console.
   - Select synthetic towing records (CDL driver qualification, vehicle brake inspection, winch logs, service tickets).

2. **Minute 2: Authenticated Audit Processing**
   - Click **Initiate Authenticated Audit**.
   - Observe backend execution state transition: `SUBMITTING` → `AUDITING` → `COMPLETED`.

3. **Minute 3: XAELI Evidence Findings**
   - Review 5-step XAELI findings:
     - `driver_qualification`: PRESENT_NOT_VERIFIED
     - `vehicle_inspection`: EXPIRED
     - `maintenance`: CONFLICTING
     - `service_ticket`: NOT_VERIFIED
     - `incident_register`: MISSING

4. **Minute 4: Office Work Queue**
   - Manage exceptions in the Operational Office Work Queue.
   - Apply human review dispositions: `ACKNOWLEDGED`, `DISPUTED`, `NEEDS_EVIDENCE`, `RESOLVED_BY_HUMAN_REVIEW`.

5. **Minute 5: Digital Audit Binder Export**
   - Click **Export Audit Binder (.json)** to generate the audit package with SHA-256 evidence integrity manifests.
