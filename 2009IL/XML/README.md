The script within this folder, `ITP2XML.py` converts a GROMACS .ITP force field
file into an OPENMM .XML file. A typical run looks like this:

```python 
python3 ITP2XML.py --atomtypes-itp ../ITP/DCA_atomtypes.itp --input-itp ../ITP/DCA.itp --input-xml DCA_template.xml --output-xml DCA.xml
```

Note that the following aniona in this directory have been manually checked as well:

* $BF_4$
* $NO_3$
* DCA
* formate 
* $PF_6$
* TFSI

# TO-DO

The initial structuring of this code requires an original .XML file to serve as a template 
(i.e., created by LigParGen). THIS IS BUG PRONE! While I have personally/manually 
checked the anions in this current directory, the `/under_dev` directory contains 
molecules that have some minor inconsistencies. The proper way to convert FF files is 
to:

## 1. Construct a GROMACS molecule 

Using the `[  atoms  ]` and `[  bonds  ]` sections of the .itp file, enough 
information is available (i.e., atom type, residue name, atom name) to 
create a molecule. This in turn can create the `<Residue>` and `<AtomType> 
class in the .xml file. 

There are likely a wide distribution of tools that can help efficiently 
convert between FF formats, but this would take longer, so ligpargen is
being used for the molecules that work. 

### a. fix DCA bug

DCA has unique C-N and N-C bonds that look identical to the current code that were manually fixed. 

