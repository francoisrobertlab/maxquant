#!/bin/bash
#SBATCH --time=5-00:00:00
#SBATCH --output=maxquant-%A.out

set -e

if [[ -n "$CC_CLUSTER" ]]
then
  module purge
  module load StdEnv/2023
  module load apptainer/1
  echo
  echo
fi

containers=(*.sif)
if [[ -f "${containers[0]}" ]]
then
  container=${containers[0]}
  echo "Using container $container"
  echo
else
  >&2 echo "Error: no containers were found in current folder, exiting..."
  exit 1
fi

workdir="${SLURM_TMPDIR:-$PWD}"

# Use '--help' as default arguments.
args+=("$@")
if [ $# -eq 0 ]
then
  args+=("--help")
fi
threads_args=()

# Remind user that when using --changeFolder, '/data' should be used as folder.
if [[ "${args[*]}" == *"-f"* || "${args[*]}" == *"--changeFolder"* ]]
then
  last_index=${#args[@]}-1
  if [[ ${args[last_index]} != "/data"* ]]
  then
    >&2 echo "Warning: '--changeFolder' should be used with '/data' folder because MaxQuant is running inside a containers"
    >&2 echo
  fi
fi

if [[ -n "$SLURM_TMPDIR" ]]
then
  echo "Coping files from $PWD to $SLURM_TMPDIR for faster access."
  rsync -rvt --exclude="*.out" "$PWD"/* "$SLURM_TMPDIR"
  echo

  threads_args=("--numThreads" "$SLURM_CPUS_PER_TASK")

  copy_temp_to_output() {
    echo
    echo "Copying files back from $SLURM_TMPDIR to $PWD"
    rsync -rvt "$SLURM_TMPDIR"/* "$PWD"
  }
  trap 'copy_temp_to_output; exit' ERR EXIT
fi

echo "Binding files in './conf' folder to MaxQuant's 'conf' folder."
bind_args=()
if [ -d "${workdir}/conf" ]
then
  for file in "${workdir}/conf"/*
  do
    filename=$(basename "$file")
    bind_args+=("-B" "$file:/opt/MaxQuant/bin/conf/$filename")
  done
  echo "Extra bind arguments for apptainer are: " "${bind_args[@]}"
fi
echo

apptainer_params=("--containall" "--workdir" "$workdir" "--pwd" "/data"
    "--bind" "${workdir}:/data")
apptainer_params+=("${bind_args[@]}")

apptainer run \
    "${apptainer_params[@]}" \
    "${workdir}/${container}" \
    "${args[@]}" \
    "${threads_args[@]}"
