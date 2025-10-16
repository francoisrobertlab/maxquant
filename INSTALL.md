# Installing MaxQuant scripts on Alliance Canada

### Steps

1. [Updating scripts](#Updating-scripts)
1. [Installing of the scripts](#Installing-of-the-scripts)
   1. [Change directory to `projects` folder](#Change-directory-to-projects-folder)
   2. [Clone repository](#Clone-repository)
2. [Creating container for MaxQuant](#Creating-container-for-MaxQuant)

## Updating scripts

Go to the maxquant scripts folder and run `git pull`.

```shell
cd ~/projects/def-robertf/scripts/maxquant
git pull
```

For Rorqual server, use

```shell
cd ~/links/projects/def-robertf/scripts/maxquant
git pull
```

## Installing of the scripts

### Change directory to projects folder

```shell
cd ~/projects/def-robertf/scripts
```

For Rorqual server, use

```shell
cd ~/links/projects/def-robertf/scripts
```

### Clone repository

```shell
git clone https://github.com/francoisrobertlab/maxquant.git
```

## Creating container for MaxQuant

### Download MaxQuant

Go to [MaxQuant Website](https://www.maxquant.org) and download the MaxQuant ZIP file. Then copy the file on Globus on Narval in this directory.
`~/projects/def-robertf/Sharing/globus-shared-apps/maxquant`

### Create container

To create an [Apptainer](https://apptainer.org) container for MaxQuant, you must use a Linux computer. Ideally, you should have root access on the computer. 

> [!IMPORTANT]
> Replace `<version>` with the actual version number, like `2.7.5.0`.

```shell
module load apptainer
apptainer build --fakeroot --build-arg version=<version> maxquant-<version>.sif maxquant.def
```

### Copy container on Globus

```shell
scp maxquant-<version>.sif 'narval.computecanada.ca:~/projects/def-robertf/Sharing/globus-shared-apps/maxquant'
```
