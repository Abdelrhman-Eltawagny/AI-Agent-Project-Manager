# Clinic Appointment & Patient Management System - Project Documentation

Document version 1.0 - sample project (no real clinic data).

## 1. Project Overview

Clinic Appointment & Patient Management System is a web application that lets a small medical clinic manage doctors' schedules, patient records and appointment bookings from one place. Receptionists book and reschedule appointments, doctors see their daily schedule and add visit notes, and the clinic manager follows basic statistics.

Duration: 4 weeks / 1 month (four one-week sprints). Delivery goal: an MVP that the clinic reception can use daily by the end of week 4.

## 2. Business Problem

The clinic books appointments on paper and in a shared spreadsheet. Double bookings happen, patient history is scattered, and the manager has no view of how busy each doctor is. Patients often miss visits because nobody reminds them.

## 3. Project Objectives

- Replace paper and spreadsheet booking with one central system.
- Prevent double bookings and show each doctor's schedule clearly.
- Keep a searchable patient record with full visit history.
- Give the manager simple numbers on appointments per doctor and per status.
- Deliver a secure, deployable MVP within four weeks.

## 4. Scope

The MVP covers authentication and roles, patient management, doctor management and working hours, appointment booking with conflict detection, appointment status handling, visit notes, search and filtering, a basic dashboard, CSV export of appointments, a REST API, a responsive web interface and PostgreSQL storage.

## 5. Out of Scope

- Online payments and insurance claims.
- Native mobile application.
- Patient self-service portal and online booking by patients.
- SMS or WhatsApp reminders and email automation.
- Integration with lab or hospital systems.
- Advanced analytics or custom report builders.

## 6. Users and Personas

- Receptionist: books, reschedules and cancels appointments and registers patients.
- Doctor: views own schedule, opens patient history and writes visit notes.
- Clinic Manager: manages staff accounts, views the dashboard and exports reports.

## 7. Functional Requirements

FR-01 Authentication: users sign in with email and password; sessions expire; failed logins are limited.
FR-02 User roles: roles receptionist, doctor and manager control what a user may do.
FR-03 Patient management: receptionists create, edit and deactivate patient records (name, phone, date of birth, notes).
FR-04 Patient history: a patient page shows personal data and the full history of appointments and visit notes.
FR-05 Doctor management: managers create doctors with specialty and weekly working hours.
FR-06 Appointment booking: receptionists book an appointment for a patient with a doctor, date, time slot and reason.
FR-07 Conflict detection: the system rejects a booking that overlaps another appointment of the same doctor.
FR-08 Appointment status: appointments move through scheduled, confirmed, completed, cancelled and no-show.
FR-09 Rescheduling: receptionists move or cancel an appointment and the change is recorded.
FR-10 Visit notes: doctors add notes to a completed appointment; notes show author and time.
FR-11 Search: staff search patients by name or phone and appointments by patient or doctor.
FR-12 Filtering: the appointment list can be filtered by date, doctor and status.
FR-13 Doctor schedule: a daily and weekly calendar view shows a doctor's appointments.
FR-14 Dashboard: shows today's appointments, appointments by status and appointments per doctor.
FR-15 Basic reporting: managers export the filtered appointment list as CSV.
FR-16 Staff management: managers create, edit and deactivate staff accounts.

## 8. Non-Functional Requirements

NFR-01 Secure authentication: passwords hashed with a modern algorithm, tokens with expiry.
NFR-02 Authorization: every API endpoint checks the caller's role.
NFR-03 REST API: all functionality exposed through a documented REST API returning JSON.
NFR-04 Responsive web interface: usable on desktop and tablet screen sizes.
NFR-05 PostgreSQL database with versioned schema migrations.
NFR-06 Logging: structured application logs for requests and errors.
NFR-07 Error handling: consistent error responses and friendly messages in the UI.
NFR-08 Automated tests: unit and API tests for core flows, plus a small end-to-end smoke suite.
NFR-09 Dockerized deployment: the whole stack starts with Docker Compose.
NFR-10 Privacy: patient data is visible only to authenticated staff with a matching role.

## 9. Technical Constraints

- Backend in Python with a REST API; PostgreSQL as the only database.
- Web frontend built with React.
- Deployment with Docker Compose on a single server.
- All time slots use the clinic's local time zone.

## 10. Team Information

The team is one project manager, two backend developers, two frontend developers, one UI/UX designer, one QA engineer and one DevOps engineer.

## 11. Timeline

Week 1 (Sprint 1): foundations - repository, CI, database schema, authentication and roles, wireframes and design system.
Week 2 (Sprint 2): core - patient management, doctor management with working hours, appointment booking and conflict detection.
Week 3 (Sprint 3): status handling, rescheduling, visit notes, search, filtering, calendar view, dashboard and a first test cycle.
Week 4 (Sprint 4): QA, bug fixing, CSV export, deployment hardening, documentation and MVP release.

## 12. Milestones

- M1 end of week 1: authentication working end to end, database schema approved, dev environment running.
- M2 end of week 2: receptionists can register patients and book appointments without double bookings.
- M3 end of week 3: doctors see their schedule and add visit notes; search, filtering and dashboard integrated.
- M4 end of week 4: MVP deployed with Docker and accepted by the clinic reception.

## 13. Dependencies

- Appointment features depend on the database schema, authentication and doctor working hours.
- Conflict detection depends on the booking API and doctor schedules.
- Frontend screens depend on approved wireframes and on the matching API endpoints.
- Dashboard and reporting depend on appointment data and the status workflow.
- QA regression depends on feature completion; deployment depends on passing QA.

## 14. Risks

- Authentication or role design delays block every other feature.
- Booking conflict logic is complex and may cause bugs in time-slot handling and time zones.
- Database schema changes after week 2 could invalidate API and UI work.
- Frontend and backend integration may slip if API contracts are not agreed early.
- A single QA engineer must test everything in the last two weeks.
- Scope creep: the clinic may ask for reminders or online booking during the month.

## 15. Acceptance Criteria

- A receptionist can register a patient, book, move and cancel an appointment.
- The system never allows two overlapping appointments for the same doctor.
- A doctor sees the daily schedule and can add a note to a completed visit.
- The manager can see the dashboard and export appointments as CSV.
- Every API endpoint rejects users without the required role.
- The full stack starts with one Docker Compose command and core tests pass.

## 16. MVP Definition

The MVP is the smallest system the clinic reception can use every day: login with roles, patients, doctors with working hours, booking with conflict detection, status handling, visit notes, search and filtering, a basic dashboard, CSV export, REST API, responsive UI, PostgreSQL storage and Docker deployment.
