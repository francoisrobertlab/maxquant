#!/usr/bin/env python3

import argparse
import os
from typing import TextIO, Callable

EVIDENCE_KEEP_HEADERS=["Sequence", "Modified sequence", "Proteins", "MS/MS IDs", "Type", "Reverse", "Charge", "Calibrated retention time"]
MSMS_KEEP_HEADERS=["Fragmentation", "Mass analyzer", "Retention time", "PEP", "Score", "Matches", "Intensities", "id"]
MODIFIED_SEQUENCE_HEADER="Modified sequence"
MSMS_IDS_HEADER="MS/MS IDs"
MSMS_ID_HEADER="id"


def file_path(string):
  if os.path.isfile(string):
    return string
  else:
    raise FileNotFoundError(string)


def main(argv: list[str] = None):
  parser = argparse.ArgumentParser(description="Removes useless columns from 'evidence.txt' and 'msms.txt'"
                                               " DDA files to use for DIA in MaxQuant.")
  parser.add_argument("-e", "--evidence", type=file_path, default="evidence.txt",
                      help="'evidence.txt' file from a MaxQuant DDA analysis  (default: %(default)s)")
  parser.add_argument("-m", "--msms", type=file_path, default="msms.txt",
                      help="'msms.txt' file from a MaxQuant DDA analysis  (default: %(default)s)")
  parser.add_argument("-E", "--out_evidence", type=argparse.FileType("w"), default="evidence-fix.txt",
                      help="Output for the fixed 'evidence.txt' file  (default: %(default)s)")
  parser.add_argument("-M", "--out_msms", type=argparse.FileType("w"), default="msms-fix.txt",
                      help="Output for the fixed 'msms.txt' file  (default: %(default)s)")
  parser.add_argument("-r", "--remove", nargs="*", default=None,
                      help="Removes peptides with any of the specified modifications  (default: %(default)s)")

  args = parser.parse_args(argv)
  fix_columns(args.evidence, args.msms, args.out_evidence, args.out_msms, args.remove)


def fix_columns(evidence_input: str, msms_input: str, evidence_output: TextIO, msms_output: TextIO, remove_modifications: list[str] = None):
  """
  Removes useless columns from 'evidence.txt' and 'msms.txt' DDA files to use for DIA in MaxQuant.

  :param evidence_input: 'evidence.txt' file from a MaxQuant DDA analysis
  :param msms_input: 'msms.txt' file from a MaxQuant DDA analysis
  :param evidence_output: output for the fixed 'evidence.txt' file
  :param msms_output: output for the fixed 'msms.txt' file
  :param remove_modifications: removes peptides with any of the specified modifications
  """
  modified_msms_ids = set()
  if remove_modifications:
    for modification in remove_modifications:
      with open(evidence_input, "r") as evidence_in:
        modified_msms_ids.update(find_modified_msms_ids(evidence_in, modification))

  with open(evidence_input, "r") as evidence_in:
    headers = evidence_in.readline().rstrip("\r\n").split("\t")
    msms_ids_index = headers.index(MSMS_IDS_HEADER)
  with open(evidence_input, "r") as evidence_in:
    keep_columns(evidence_in, evidence_output, EVIDENCE_KEEP_HEADERS, lambda line: alter_content_evidence(line, msms_ids_index, modified_msms_ids))
  with open(msms_input, "r") as msms_in:
    headers = msms_in.readline().rstrip("\r\n").split("\t")
    msms_id_index = headers.index(MSMS_ID_HEADER)
  with open(msms_input, "r") as msms_in:
    keep_columns(msms_in, msms_output, MSMS_KEEP_HEADERS, lambda line: alter_content_evidence(line, msms_id_index, modified_msms_ids))


def find_modified_msms_ids(evidence: TextIO, modification: str) -> list[str]:
  """
  Returns list of 'MS/MS IDs' of all peptides with modification.

  :param evidence: 'evidence.txt' file from a MaxQuant analysis
  :param modification: modification to look for
  :return: list of 'MS/MS IDs' of all peptides with modification.
  """
  headers = evidence.readline().rstrip("\r\n").split("\t")
  modified_sequence_index = headers.index(MODIFIED_SEQUENCE_HEADER)
  msms_ids_index = headers.index(MSMS_IDS_HEADER)

  msms_ids = []
  for line in evidence:
    columns = line.rstrip("\r\n").split("\t")
    modified_sequence = columns[modified_sequence_index]
    if modification in modified_sequence:
      msms_ids.extend(columns[msms_ids_index].split(";"))
  return msms_ids


def alter_content_evidence(line: str, msms_ids_index: int, remove_msms_ids: set[str] = None) -> str:
  """
  Removes 'MS/MS IDs' from evidence file line. If all 'MS/MS IDs' are removed, return empty string.

  :param line: line from evidence file
  :param msms_ids_index: index of column containing 'MS/MS IDs'
  :param remove_msms_ids: 'MS/MS IDs' to remove
  :return: line without removed 'MS/MS IDs', or empty if all 'MS/MS IDs' are removed
  """
  columns = line.rstrip("\r\n").split("\t")
  msms_ids = columns[msms_ids_index].split(";")
  msms_ids = [msms_id for msms_id in msms_ids if msms_id not in remove_msms_ids]
  if msms_ids:
    columns[msms_ids_index] = ";".join(msms_ids)
    return "\t".join(columns) + "\n"
  else:
    return ""


def alter_content_msms(line: str, msms_id_index: int, remove_msms_ids: set[str] = None) -> str:
  """
  If msms 'id' is present in remove_msms_ids parameter, return empty string, otherwise return original line.

  :param line: line from msms file
  :param msms_id_index: index of column containing 'id'
  :param remove_msms_ids: 'id' to remove
  :return: empty string if 'id' is present in remove_msms_ids, otherwise return original line.
  """
  columns = line.rstrip("\r\n").split("\t")
  if int(columns[msms_id_index]) in remove_msms_ids:
    return ""
  else:
    return line


def keep_columns(input_file: TextIO, output_file: TextIO, column_headers: list[str], alter_content: Callable[[str], str] = None):
  """
  Keep selected columns from TSV file.

  :param input_file: input TSV file
  :param output_file: output TSV file containing only specified columns
  :param column_headers: header of the columns to keep
  :param alter_content: function that alters content of line - line is removed from output if empty
  """
  if not alter_content:
    alter_content = lambda _line: _line

  headers = input_file.readline().rstrip("\r\n").split("\t")
  keep_indexes = [headers.index(header) for header in column_headers]

  output_file.write("\t".join([headers[i] for i in keep_indexes]))
  output_file.write("\n")

  for line in input_file:
    line = alter_content(line)
    if line:
      columns = line.rstrip("\r\n").split("\t")
      output_file.write("\t".join([columns[i] for i in keep_indexes]))
      output_file.write("\n")


if __name__ == '__main__':
  main()
