Assembler designed for a simple CPU written entirely in Python using regular expression.
All functions only have one or none arguments.
You can define new functions by changing 'config.json'
There are four types of functions:
1. No Operands : Just put the name and corresponding binary
2. Relative Operand : Put the binary with 'x's in it, as a marker as to where the relative number needs to go.
3. Absolute Operand : Put the binary with 'y's in it, as a marker as to where the absolute number needs to go.
4. Register Operand : Put the binary with 'r's in it, as a marker as to where the register number needs to go.

Usage:
```
python assembler.py <filename>
```

Create an [issue](https://github.com/nithinmanne/coa-assembler/issues) if any functionality is not working as intended or for a new functionality.
