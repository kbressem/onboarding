---
title: RadCat data access
subtitle: Radiology images, reports and clinical data at TUM
---

RadCat supplies radiology images, reports and clinical (SAP) data for research. You send a request on the RadCat website, and an administrator gives the access there. The database and the files on the storage server then change automatically. The access always uses your server login.

## Website

The address of the website is https://10.32.16.96/access/. You can connect to it only from the clinic network. Log in with your server user name and password.

The certificate is self-signed. Thus, the browser shows a warning one time. Continue only if the SHA-256 fingerprint is

`BC:62:0D:AC:D2:59:52:77:01:DF:AB:E3:9E:BF:29:0D:67:83:A9:E2:FF:B3:FB:02:FC:B5:C0:A8:6C:7B:4B:5D`

## Data request

1. Log in and open "New request".
2. Write the project and the data that is necessary for it.
    - Modality and body region
    - ICD-10 codes of the diagnosis groups
    - Time period
    - Document types
3. Write the ethics reference and the end date of the access.
4. Wait for the approval. If the administrators must have more information, the status changes to "needs information".

After the approval, database queries operate immediately. The files are in your folder after 15 to 20 seconds. For a large first access, this takes some minutes. At the end date, the access stops automatically in the database and on the disk.

The access always has two parts, which patients and which content types. You cannot see other data.

| Content group | Content types |
|---|---|
| Images | CT, MR, X-ray, other imaging (PET/NM, US, angiography), segmentations and measurements |
| Reports | Letters and history, radiology, pathology, laboratory, microbiology and virology, tumor boards, other documents |
| Clinical data (SAP) | Diagnoses, procedures, services, pharmacy, chemotherapy, laboratory values, cases and stays, other SAP lists |

## Database

The database uses peer login. Thus, a database password is not necessary. On the storage server, use these commands.

```
psql -d radcat_acltest
SELECT * FROM api.whoami();
```

The `api` schema has functions, for example `api.cohort(...)`, `api.patient_timeline(id)` and `api.export_paths('TUM', 'CT')`. The column `files_present` shows if the files of a series are on the disk. To connect from a different server, use the scripts in `~luebberstedt/radcat-acl/examples/`. The script `radcat_connect.sh` opens an SSH tunnel for psql and Python.

## Files

All data that you can access is linked in `~/radcat-data` (`/data/ssd/views/<user>`). The data is in folders for each type and patient, for example `images/<patient>/<study>/<series>`, `doc_radiology/<patient>/...` and `diagnoses/...`. The data includes images, NIfTI files, report PDFs, report texts and SAP lists.

To use the files on a different server, mount the folder into an empty directory.

```
sshfs -o follow_symlinks,reconnect,idmap=user \
      -o ServerAliveInterval=15,ServerAliveCountMax=3 \
      <user>@RAD-ADAMS-STO-1.rad.mri.tu-muenchen.de:/data/ssd/views/<user> \
      ~/radcat
```

- Use the remote path `/data/ssd/views/<user>`. Do not use `~/radcat-data`, because sshfs cannot mount a link as the root.
- Use the option `follow_symlinks`. If you do not use it, the files are not correct.
- Use the option `idmap=user`. If you do not use it, the files show an incorrect owner.
- In MobaXterm, you can open the files with a double-click when the folder is mounted on a different server. In the MobaXterm file browser on the storage server, use right-click and Download to open reports.

## Logs

The website records each API query (user, time and patients) and each change of an access. The website does not record the file reads.

## Status (5 October 2026)

RadCat is in a test phase on the database `radcat_acltest`. The current access settings will stay when the test database becomes the live database `radcat`. This change has a short, scheduled downtime. At this time, the live database `radcat` has the old data and no access control.

- All 375,040 TUM studies are in the database. The files go from `/data/hdd/incoming` to `/data/hdd/dicom/TUM/...`. This copy will be complete on about 7 October. When a series is in the new location, it is in your folder after about 10 minutes.
- The test phase does not change `/data/hdd/incoming`. The `data-transfer` account operates as before.
- 89 % of the NIfTI files have a link to their series. You can use them when the derivatives storage has access control.
