---
title: RadCat administration
subtitle: For RadCat administrators
---

The RadCat administrators are the persons in the `sudo` group on the storage server (now bressem, bercea, luebberstedt). The website copies this group automatically. You cannot change it on the website.

## New users

Each user must have a server account first, because the access always uses the login of the user.

1. On the storage server, make the server account with `sudo adduser <username>`.
2. Tell the user to change the initial password with `passwd` at the first login.
3. On the website, make the RadCat account. Select Users, then "Add user", and write the server user name.

As an alternative to step 3, use `sudo usermod -aG radcat-web-users <username>`. The user can then log in and send a request. The user has no data access before you give it.

## Access

"Save and grant" on a request does all tasks in one step. It makes the RadCat account if necessary. It gives the datasets or adds the user to a project. It sets the end date and changes the request status to approved. Administrators can write comments, set the status "needs information" or write internal notes. The user cannot see the internal notes.

Use projects for usual access. A project is a patient list with its content types and members.

1. Select Projects, then "New project". Write the name and the end date. Select the content types. The default is no content types.
2. On the project page, select "Select patients". Select a patient list, for example TUM_PID, TUM_PSEUDO_PID, UKB_EID or NAKO_ID.
3. Use the filters, for example ICD-10 and OPS prefixes, sex, birth date, deceased, scans on the server and dataset.
4. Select "Add selected" or "Add all N matching". You can add more patient lists to the same project.
5. Add the members. You can set an end date for each member. A member gets all content types of the project and no other content types.

A dataset grant gives one user a full dataset (for example UKB-679910) with the selected content types. Use dataset grants only when necessary. One TUM grant gives access to 2.2 million patients.

## Removal of access

RadCat removes access before it gives new access. To remove access, do one of these steps.

- Remove patients or a member from a project.
- Remove the selection of a content type.
- Cancel a dataset grant.
- Wait for the end date.

The database changes immediately. The files change after 15 to 20 seconds.

If there is an emergency, use `sudo radcat-filesync --db radcat_acltest revoke <user>`. This command deactivates the account and removes all file access in about one second. To activate the account again, use the page of the user. The access settings stay.

The website shows the access log and the audit trail. The access log shows each API query with user, time and patients. The audit trail shows each change of an access and the administrator who did it. RadCat does not record file reads.
