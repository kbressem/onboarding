---
title: Onboarding TUM
subtitle: Institute of Diagnostic and Interventional Radiology, TUM Klinikum, Munich
---

The Munich part of the group is at the Institute of Diagnostic and Interventional Radiology of TUM Klinikum. Keno Bressem is the group leader. Speak to Keno first.

<!-- TODO: office location, building access, first-day logistics. -->

## Contacts

| Person | Items | Contact |
|---|---|---|
| Keno Bressem, group leader | All items. Speak to Keno first. | keno.bressem@tum.de |
| Lisa Adams | Supervision and project decisions | Email, Slack |
| Cosmin Bercea | Supervision, project decisions and server administration | Email, Slack |
| Jannik Lübberstedt | Server administration, RadCat and scan exports | Slack |
| Johannes Moll | GPU servers | Slack #mri-gpu-server |

<!-- TODO: roles and email addresses of Lisa Adams and Cosmin Bercea, TUM HR and IT contacts. -->

> Use email to contact Keno, Lisa Adams or Cosmin Bercea about decisions and important items. Slack, and WhatsApp for Keno, are for short messages. It is possible that a person does not see a Slack message.

## First weeks

1. Complete the HR and IT onboarding of your employer (TUM Klinikum or TUM).
2. Tell Keno to add you to the lab Slack (agki.slack.com). Then add yourself to the channels #general and #mri-gpu-server.
3. Tell a server administrator to make an account for you on the storage server. At the first login, change the initial password with `passwd`. RadCat uses the same login.
4. Use RadCat to get the data for your project. Refer to [Data access](#data-access).
5. For large model training, you can use the NHR@FAU clusters (Alex, Helma). Get access through the HPC portal and add your SSH key there. A new account operates from the next morning.

<!-- TODO: TUM account and email activation, who invites to the NHR project, whether GPU server accounts are separate. -->

## Remote access

You can connect to the servers and to RadCat only from the clinic network.

<!-- TODO: VPN application, client and remote desktop route for TUM Klinikum. -->

## Data access

RadCat supplies radiology images, reports and clinical (SAP) data. You get access for each project. The access always uses your server login.

1. Log in to the RadCat website (https://10.32.16.96/access/) with your server account.
2. Open "New request". Write the project, modalities, body region, ICD-10 codes, time period, document types, ethics reference and end date.
3. An administrator examines the request. If more information is necessary, the administrator tells you.
4. After the approval, database queries operate immediately. The files are in `~/radcat-data` after some minutes.
5. Your access stops automatically at the end date.

For projects with patient data, you must have an approved vote of the TUM ethics committee. Speak to Keno before you write the ethics application. For more scan exports, write a message in #mri-gpu-server. For more information, refer to [RadCat](reference/radcat.md).

## Compute

The group has GPU servers (ADAMS1 with H100 GPUs, Ada with a segmentation endpoint) and a language model server. Keep your home directory smaller than 1 GB. Put data, environments and the VS Code server in `/data/<user>`. Use #mri-gpu-server for announcements and problems. For more information, refer to [TUM compute](reference/tum-compute.md).

## Annotations

The medical doctors (MDs) in the group give time for clinical expertise and annotations. The total is now 300 hours each month. The time for each MD changes with the projects. Use the [group spreadsheet](https://docs.google.com/spreadsheets/d/1u5qNBF6q5MZqZWaTI2Gbz5txh2EhGKpXm2O2GMob4dI/edit) for all annotation tasks.

- If your project must have clinical expertise or annotations, write it in the Annotations tab.
- If you are an MD, write your projects in the Annotations tab and your office times in the Team tab.

## Meetings

All group meetings are online in Google Meet, [meet.google.com/hkt-bqxy-rya](https://meet.google.com/hkt-bqxy-rya). Keno also uses this room for 1:1 meetings.

| Meeting | Time | Description |
|---|---|---|
| Morning sprint | Tuesday and Friday, 09:15 | Short status meeting of the full group, also with short paper presentations. For a presentation, write your name, the paper and the date in the presentation sheet of the [group spreadsheet](https://docs.google.com/spreadsheets/d/1u5qNBF6q5MZqZWaTI2Gbz5txh2EhGKpXm2O2GMob4dI/edit). |
| Thursday meeting | Every second Thursday from 15 October 2026, 17:15 | Meeting of the full group |
| 1:1 meeting with Keno | Usually in the morning, until 11:30 | Meetings about your work and your projects |

<!-- TODO: name and content of the Thursday meeting, calendar invitation for new members. -->

## Business trips and purchases

Before you make a reservation or a purchase, speak to Keno about it and about the funding.

<!-- TODO: TUM business travel (application, booking, reimbursement) and ordering process. -->
