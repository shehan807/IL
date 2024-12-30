import argparse
import xml.etree.ElementTree as ET
import math

def parse_atom_types(xml_file):
    """Parse the AtomTypes section from the XML file."""
    atom_types = {"name_to_element": {}, "class_to_element": {}}
    tree = ET.parse(xml_file)
    root = tree.getroot()
    atom_types_section = root.find("AtomTypes")

    if atom_types_section is None:
        print("Error: AtomTypes section not found in XML.")
        return atom_types

    for atom_type in atom_types_section.findall("Type"):
        name = atom_type.get("name")
        atom_class = atom_type.get("class")
        element = atom_type.get("element")
        if name:
            atom_types["name_to_element"][name] = element
        if atom_class:
            atom_types["class_to_element"][atom_class] = element

    return atom_types

def parse_itp_bonds(itp_file):
    """Parse the bonds section from the .itp file."""
    bonds = []
    with open(itp_file, 'r') as f:
        in_bonds_section = False
        for line in f:
            line = line.strip()
            if line.startswith("[  bonds  ]"):
                in_bonds_section = True
                continue
            if in_bonds_section:
                if line.startswith(";") or not line:
                    continue
                if line.startswith("["):
                    break
                tokens = line.split()
                try:
                    ai, aj, funct, length, k, *bond_type_parts = tokens
                    bond_type = bond_type_parts[-1]  # Use the last part as bond type
                    bonds.append((int(ai), int(aj), float(length), float(k), bond_type))
                except ValueError:
                    print(f"Warning: Skipping malformed line: {line}")
    return bonds

def parse_itp_angles(itp_file):
    """Parse the angles section from the .itp file."""
    angles = []
    with open(itp_file, 'r') as f:
        in_angles_section = False
        for line in f:
            line = line.strip()
            if line.startswith("[  angles  ]"):
                in_angles_section = True
                continue
            if in_angles_section:
                if line.startswith(";") or not line:
                    continue
                if line.startswith("["):
                    break
                tokens = line.split()
                try:
                    ai, aj, ak, funct, angle, k, *angle_type_parts = tokens
                    angle_type = angle_type_parts[-1] if angle_type_parts else None
                    angles.append((int(ai), int(aj), int(ak), math.radians(float(angle)), float(k), angle_type))
                except ValueError:
                    print(f"Warning: Skipping malformed line: {line}")
    return angles

def parse_itp_dihedrals(itp_file):
    """Parse the dihedrals section from the .itp file."""
    dihedrals = []
    with open(itp_file, 'r') as f:
        in_dihedrals_section = False
        for line in f:
            line = line.strip()
            if line.startswith("[  dihedrals  ]"):
                in_dihedrals_section = True
                continue
            if in_dihedrals_section:
                if line.startswith(";") or not line:
                    continue
                if line.startswith("["):
                    break
                tokens = line.split()
                try:
                    # Detect if the last column is 'improper'
                    is_improper = tokens[-1].lower() == "improper"
                    if is_improper:
                        tokens = tokens[:-1]  # Exclude 'improper' for parsing

                    ai, aj, ak, al, funct, k1, k2, k3, k4, *dihedral_type_parts = tokens
                    dihedral_type = dihedral_type_parts[-1] if dihedral_type_parts else None
                    dihedrals.append( (
                        int(ai), int(aj), int(ak), int(al),
                        float(k1), float(k2), float(k3), float(k4),
                        dihedral_type, is_improper
                    ))
                except ValueError:
                    print(f"Warning: Skipping malformed line: {line}")
    return dihedrals

def parse_itp_nonbonded(itp_file):
    """Parse the nonbonded section from the .itp file."""
    nonbonded = []
    with open(itp_file, 'r') as f:
        in_nonbonded_section = False
        for line in f:
            line = line.strip()
            if line.startswith("[  atomtypes  ]"):
                in_nonbonded_section = True
                continue
            if in_nonbonded_section:
                if line.startswith(";") or not line:
                    continue
                if line.startswith("["):
                    break
                tokens = line.split()
                try:
                    atom_type, mass, charge, ptype, sigma, epsilon, *nonbonded_type_parts = tokens
                    nonbonded.append((atom_type, float(charge), float(sigma), float(epsilon)))
                except ValueError:
                    print(f"Warning: Skipping malformed line: {line}")
    return nonbonded

def update_tree(root, parameters, atom_types, force_type):
    """Update the XML tree for a specific force type (bonds, angles, dihedrals, nonbonded)."""
    force_section = root.find(force_type)

    if force_section is None:
        print(f"Error: {force_type} section not found in XML.")
        return

    for param in force_section:
        class1 = param.get("class1")
        class2 = param.get("class2")
        class3 = param.get("class3") if param.get("class3") else None
        class4 = param.get("class4") if param.get("class4") else None

        element1 = atom_types["class_to_element"].get(class1, None)
        element2 = atom_types["class_to_element"].get(class2, None)
        element3 = atom_types["class_to_element"].get(class3, None) if class3 else None
        element4 = atom_types["class_to_element"].get(class4, None) if class4 else None

        # Adjust handling for missing elements
        if not element1 or not element2 or (force_type in ["HarmonicAngleForce", "PeriodicTorsionForce"] and not element3):
            if force_type == "NonbondedForce":
                element1 = atom_types["name_to_element"].get(param.get("type"), None)
            else:
                print(f"Warning: Could not determine element for classes {class1}, {class2}, {class3}, {class4}.")
                continue

        if force_type == "HarmonicBondForce":
            bond_elements = f"{element1}-{element2}" if element1 <= element2 else f"{element2}-{element1}"
            for bond in parameters:
                ai, aj, length, k, bond_type = bond
                if bond_elements == bond_type:
                    param.set("length", f"{length:.6f}")
                    param.set("k", f"{k:.6f}")
                    break

        elif force_type == "HarmonicAngleForce":
            angle_elements = f"{element1}-{element2}-{element3}" if element1 <= element3 else f"{element3}-{element2}-{element1}"
            for angle in parameters:
                ai, aj, ak, angle_value, k, angle_type = angle
                angle_type = [a[0] for a in angle_type.split("-")]
                angle_type = "-".join(angle_type)
                if angle_elements == angle_type:
                    param.set("angle", f"{angle_value:.6f}")
                    param.set("k", f"{k:.6f}")
                    break

        elif force_type == "PeriodicTorsionForce":
            dihedral_elements = [element1, element2, element3, element4]
            for dihedral in parameters:
                ai, aj, ak, al, k1, k2, k3, k4, dihedral_type, is_improper = dihedral
                dihedral_type_elements = dihedral_type.split("-")
                dihedral_type_elements = [e[0] for e in dihedral_type_elements]
                if (dihedral_elements == dihedral_type_elements or
                    dihedral_elements == dihedral_type_elements[::-1]):  # Check reverse match
                    tag = "Improper" if is_improper else "Proper"
                    param.tag = tag  # Update the tag (Proper or Improper)
                    param.set("k1", f"{k1:.6f}")
                    param.set("k2", f"{k2:.6f}")
                    param.set("k3", f"{k3:.6f}")
                    param.set("k4", f"{k4:.6f}")
                    break

        elif force_type == "NonbondedForce":
            for atom_type, charge, sigma, epsilon in parameters:
                element_from_atom_type = atom_type[0]  # First character reliably gives the element
                if element1 == element_from_atom_type:
                    param.set("charge", f"{charge:.6f}")
                    param.set("sigma", f"{sigma:.6f}")
                    param.set("epsilon", f"{epsilon:.6f}")
                    break

def main():
    parser = argparse.ArgumentParser(description="Update XML force field file with parameters from ITP file.")
    parser.add_argument("-a", "--atomtypes-itp", type=str, help="Path to the atomtypes.itp file.")
    parser.add_argument("-i", "--input-itp", type=str, help="Path to the input .itp file.")
    parser.add_argument("-x", "--input-xml", type=str, help="Path to the input XML file.")
    parser.add_argument("-o", "--output-xml", type=str, help="Path to the output XML file.")
    args = parser.parse_args()

    atom_types = parse_atom_types(args.input_xml)
    bonds = parse_itp_bonds(args.input_itp)
    angles = parse_itp_angles(args.input_itp)
    dihedrals = parse_itp_dihedrals(args.input_itp)
    nonbonded = parse_itp_nonbonded(args.atomtypes_itp)

    tree = ET.parse(args.input_xml)
    root = tree.getroot()

    update_tree(root, bonds, atom_types, "HarmonicBondForce")
    update_tree(root, angles, atom_types, "HarmonicAngleForce")
    update_tree(root, dihedrals, atom_types, "PeriodicTorsionForce")
    update_tree(root, nonbonded, atom_types, "NonbondedForce")

    tree.write(args.output_xml)

if __name__ == "__main__":
    main()

