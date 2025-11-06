# MaxQuant on Alliance Canada

This repository contains scripts to run MaxQuant on Alliance Canada servers.

To install the scripts on Alliance Canada servers and create containers, see [INSTALL.md](INSTALL.md)

### Steps

1. [Create parameter file on Windows](#Create-parameter-file-on-Windows)
2. [Transfer data to `scratch`](#Transfer-data-to-scratch)
3. [Add MaxQuant scripts folder to your PATH](#Add-MaxQuant-scripts-folder-to-your-PATH)
4. [Download MaxQuant container](#Download-MaxQuant-container)
5. [See MaxQuant help (optional)](#See-MaxQuant-help)
6. [Change folders in MaxQuant parameter file](#Change-folders-in-MaxQuant-parameter-file)
7. [Change number of threads](#Change-number-of-threads)
8. [Fix evidence and msms files for DIA](#Fix-evidence-and-msms-files-for-DIA)
9. [Checking the different steps MaxQuant will use (optional)](#Checking-the-different-steps-MaxQuant-will-use)
10. [Running MaxQuant](#Running-MaxQuant)

## Create parameter file on Windows

Start MaxQuant on a Windows computer and create parameter file.

## Transfer data to scratch

You will need to transfer the following files on the server in the `scratch` folder.

* Parameter file for MaxQuant (usually named `mqpar.xml`).
  * This file is generally created using MaxQuant GUI on a Windows computer.
* MS/MS RAW files present in the parameter file.
* FASTA file(s) present in the parameter file.
* Any additional files that are needed by MaxQuant, when applicable. These may include any of the following.
  * Additional configuration files if MaxQuant's configuration was used.
    * Additional configuration files must be copied into a `conf` subfolder,
  * `evidence.txt` and `msms.txt` from a DDA run to use for DIA analysis.
    * I suggest putting these two files in a `dda` subfolder.

There are many ways to transfer data to the server. Here are some suggestions.

* Use an FTP software like [WinSCP](https://winscp.net) (Windows), [Cyberduck](https://cyberduck.io) (Mac), [FileZilla](https://filezilla-project.org).
* Use command line tools like `rsync` or `scp`.

## Add MaxQuant scripts folder to your PATH

```shell
export PATH=~/projects/def-robertf/scripts/maxquant:$PATH
```

For Rorqual server, use

```shell
export PATH=~/links/projects/def-robertf/scripts/maxquant:$PATH
```

## Download MaxQuant container

```shell
wget https://g-88ccb6.6d81c.5898.data.globus.org/maxquant/maxquant-2.7.5.0.sif
```

## See MaxQuant help

> [!TIP]
> You can see MaxQuant's help using this command

```shell
maxquant.sh --help
```

## Change folders in MaxQuant parameter file

Since the parameter file was created on a Windows computer, you need to change the folder inside the parameter file.

```shell
maxquant.sh mqpar.xml --changeFolder mqpar-container.xml /data /data
```

For DIA using additional `evidence.txt` and `msms.txt` files present in the `dda` subfolder.

```shell
maxquant.sh mqpar.xml --changeFolder mqpar-container.xml /data /data /data/dda
```

## Change number of threads

You should choose the right number of threads. Here we show an example using 24 threads.

For DDA experiments, a good number of threads is 1.5 times the number of samples.

```shell
threads=24
```

Update the parameter file with the selected number of threads.

```shell
maxquant.sh mqpar-container.xml --changeParameter numThreads $threads
```

## Fix evidence and msms files for DIA

> [!CAUTION]
> This section can probably be skipped. Just use the `evidence.txt` and `msms.txt` output from DDA analysis without any changes.

If you are running a DIA analysis with MaxQuant and you want to use MS/MS spectras from a DDA run,
you need to keep only certain columns in the `evidence.txt` and `msms.txt` files otherwise.
Otherwise, MaxQuant will fail.

To fix the files, just run the following commands.

```shell
fix-dda-files-for-dia.py --evidence dda/evidence.txt --msms dda/msms.txt --out_evidence dda/evidence-fix.txt --out_msms dda/msms-fix.txt
mv -f dda/evidence-fix.txt dda/evidence.txt
mv -f dda/msms-fix.txt dda/msms.txt
```

## Checking the different steps MaxQuant will use

```shell
maxquant.sh mqpar-container.xml --dryrun
```

## Running MaxQuant

You should choose the right amount of memory (RAM) to use.

If you don't know the amount of memory, you can try with 64GB and adjust if the task fails due to an *out of memory* exception

> [!TIP]
> If you have access to multiple projects, you will need to specify the account for `sbatch` using parameter `--account=def-robertf`.

```shell
sbatch --cpus-per-task=$threads --mem=96G maxquant.sh mqpar-container.xml
```
