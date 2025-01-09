#!/usr/bin/env python3
import argparse
import parmed as pmd

def main():
    parser = argparse.ArgumentParser(
        description=(
            "Convert GROMACS coordinate/topology files into OpenMM XML force field files "
            "using ParmEd. By default, writes out a 'system.xml' for the entire system. "
            "Optionally, you can also export a .ffxml (force field XML)."
        )
    )
    parser.add_argument(
        "-c", "--coord",
        type=str, required=True,
        help="Path to the coordinate file (e.g., .gro, .pdb)."
    )
    parser.add_argument(
        "-t", "--topol",
        type=str, required=True,
        help="Path to the topology file (e.g., .top)."
    )
    parser.add_argument(
        "-o", "--outputxml",
        type=str, default="system.xml",
        help="Output filename for the system-wide OpenMM XML (default: system.xml)."
    )
    parser.add_argument(
        "-f", "--outputffxml",
        type=str, default=None,
        help="Optional output filename for the force field XML (.ffxml). "
             "If omitted, no ffxml is generated."
    )

    args = parser.parse_args()

    # 1) Load the coordinate file (e.g., .gro or .pdb)
    coords = pmd.load_file(args.coord)

    # 2) Load the GROMACS topology (.top)
    topol = pmd.load_file(args.topol)

    # 3) Merge them into one ParmEd Structure
    structure = topol + coords

    # 4) Create an OpenMM System from the Structure
    omm_system = structure.createSystem()

    # 5) Write out the entire system as an OpenMM .xml
    xml_str = pmd.openmm.topsystem.write_system_xml(omm_system, structure)
    with open(args.outputxml, 'w') as f:
        f.write(xml_str)

    # 6) Optionally, also export a reusable .ffxml
    if args.outputffxml is not None:
        structure.save(args.outputffxml, overwrite=True)

    print("Conversion complete!")
    print(f"System XML written to: {args.outputxml}")
    if args.outputffxml:
        print(f"Force-field XML (ffxml) written to: {args.outputffxml}")

if __name__ == "__main__":
    main()

