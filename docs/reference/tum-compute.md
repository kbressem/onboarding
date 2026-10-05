---
title: TUM compute
subtitle: GPU servers, storage and HPC clusters
---

You can connect to all servers only from the clinic network. Use Slack #mri-gpu-server for problems and announcements. The administrators also use this channel for outages and maintenance.

| System | Use |
|---|---|
| RAD-ADAMS-STO-1 | Storage server with the RadCat database and files |
| ADAMS1 | GPU server with H100 GPUs |
| Ada | GPU server with the segmentation endpoint (10.203.71.204) |
| Language model server | Text generation endpoint (10.32.16.43) |
| NHR@FAU Alex and Helma | National HPC clusters for large model training |

<!-- TODO: hostnames, GPU counts, how to get accounts on ADAMS1 and Ada, job scheduling rules. -->

## Storage rules

All users share the `/home` disk, and it becomes full quickly. Keep your home directory smaller than 1 GB. Put data, environments and large tool folders in `/data/<user>`. For the VS Code server, move the folder and make a link to it.

```
mv ~/.vscode-server /data/$USER/.vscode-server
ln -s /data/$USER/.vscode-server ~/.vscode-server
```

## GPU use

Before you start a job, look at the output of `nvidia-smi`. If a process uses GPU memory and has no GPU load, write a message in #mri-gpu-server. Do not stop processes of other users.

## Segmentation endpoint

Ada supplies TotalSegmentator organ segmentation. The option `--fast` uses the original fast setting. The option `--fast-experimental` is about seven times faster and gives the same segmentations. If you find a difference, write a message in #mri-gpu-server. An example script is in the channel (15 September 2026).

## NHR@FAU clusters

Use the NHR@FAU HPC portal for your account and your SSH key. A new account operates from about 09:00 on the next day. Before this time, the login shows an error because there is no home directory.
