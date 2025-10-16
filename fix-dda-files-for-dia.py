#!/usr/bin/env python3

import argparse
from typing import TextIO


EVIDENCE_KEEP_HEADERS=["Sequence", "Modified sequence", "Proteins", "MS/MS IDs", "Type", "Reverse", "Charge", "Calibrated retention time"]
MSMS_KEEP_HEADERS=["Fragmentation", "Mass analyzer", "Retention time", "PEP", "Score", "Matches", "Intensities", "id"]


def main(argv: list[str] = None):
  parser = argparse.ArgumentParser(description="Removes useless columns from 'evidence.txt' and 'msms.txt'"
                                               " DDA files to use for DIA in MaxQuant.")
  parser.add_argument("-e", "--evidence", type=argparse.FileType("r"), default="evidence.txt",
                      help="'evidence.txt' file from a MaxQuant DDA analysis  (default: %(default)s)")
  parser.add_argument("-m", "--msms", type=argparse.FileType("r"), default="msms.txt",
                      help="'msms.txt' file from a MaxQuant DDA analysis  (default: %(default)s)")
  parser.add_argument("-E", "--out_evidence", type=argparse.FileType("w"), default="evidence-fix.txt",
                      help="Output for the fixed 'evidence.txt' file  (default: %(default)s)")
  parser.add_argument("-M", "--out_msms", type=argparse.FileType("w"), default="msms-fix.txt",
                      help="Output for the fixed 'msms.txt' file  (default: %(default)s)")

  args = parser.parse_args(argv)
  fix_columns(args.evidence, args.msms, args.out_evidence, args.out_msms)


def fix_columns(evidence_input: TextIO, msms_input: TextIO, evidence_output: TextIO, msms_output: TextIO):
  """
  Removes useless columns from 'evidence.txt' and 'msms.txt' DDA files to use for DIA in MaxQuant.

  :param evidence_input: 'evidence.txt' file from a MaxQuant DDA analysis
  :param msms_input: 'msms.txt' file from a MaxQuant DDA analysis
  :param evidence_output: output for the fixed 'evidence.txt' file
  :param msms_output: output for the fixed 'msms.txt' file
  """
  keep_columns(evidence_input, evidence_output, EVIDENCE_KEEP_HEADERS)
  keep_columns(msms_input, msms_output, MSMS_KEEP_HEADERS)


def keep_columns(input_file: TextIO, output_file: TextIO, column_headers: list[str]):
  """
  Keep selected columns from TSV file.

  :param input_file: input TSV file
  :param output_file: output TSV file containing only specified columns
  :param column_headers: header of the columns to keep
  """
  headers = input_file.readline().rstrip("\r\n").split("\t")
  keep_indexes = [headers.index(header) for header in column_headers]

  output_file.write("\t".join([headers[i] for i in keep_indexes]))
  output_file.write("\n")

  for line in input_file:
    columns = line.rstrip("\r\n").split("\t")
    output_file.write("\t".join([columns[i] for i in keep_indexes]))
    output_file.write("\n")


if __name__ == '__main__':
  main()
