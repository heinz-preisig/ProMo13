#!/usr/bin/env python3
"""
Simple test to verify interface equation record structure
"""

import sys
import os

# Add the Common directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Import just the record creation functions
from Common.record_definitions import makeCompletEquationRecord, makeCompleteVariableRecord
from OntologyBuilder.EquationEditor_v01.resources import dateString

def test_record_format():
    """Test that we can create proper equation and variable records"""
    
    print("Testing Record Format")
    print("=" * 30)
    
    try:
        # Test equation record creation
        rhs_dic = {"global_ID": "V_source", "latex": "T"}
        incidence_list = ["V_source"]
        
        equation_record = makeCompletEquationRecord(
            rhs=rhs_dic, 
            network="interface", 
            doc="Interface equation linking physical_T to physical.T",
            incidence_list=incidence_list, 
            created=dateString()
        )
        
        print("✓ Equation record created successfully")
        
        # Check required fields
        required_fields = ["rhs", "type", "doc", "network", "incidence_list", "created", "modified"]
        missing_fields = [field for field in required_fields if field not in equation_record]
        
        if missing_fields:
            print(f"❌ Missing fields: {missing_fields}")
            return False
        else:
            print("✓ All required equation fields present")
        
        # Check RHS format
        rhs = equation_record["rhs"]
        if "global_ID" in rhs and "latex" in rhs:
            print("✓ RHS has proper format: {'global_ID': ..., 'latex': ...}")
        else:
            print("❌ RHS format incorrect")
            return False
        
        # Check equation type
        if equation_record["type"] == "generic":
            print("✓ Equation type is 'generic' (standard)")
        else:
            print(f"❌ Unexpected equation type: {equation_record['type']}")
            return False
        
        # Test variable record creation with equation
        variable_record = makeCompleteVariableRecord(
            var_ID="V_interface",
            label="physical_T",
            type="state",
            network="interface",
            doc="Interface variable for physical.T",
            index_structures=[],
            units="K",
            equations={"E_interface": equation_record},
            aliases={"latex": "physical_T", "global_ID": "V_interface"},
            port_variable=False,
            tokens=[],
            memory=None
        )
        
        print("✓ Variable record with equation created successfully")
        
        # Check variable record
        if "equations" in variable_record and "E_interface" in variable_record["equations"]:
            print("✓ Equation properly embedded in variable record")
        else:
            print("❌ Equation not found in variable record")
            return False
        
        print("\n✅ Record Format Test PASSED!")
        print(f"Equation record keys: {list(equation_record.keys())}")
        print(f"Variable record keys: {list(variable_record.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during record creation: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_comparison():
    """Show the difference between old and new formats"""
    
    print("\nFormat Comparison")
    print("=" * 20)
    
    print("❌ OLD (incorrect) format:")
    print("""
interface_equation = {
    "lhs": {"global_ID": interface_var_ID},      # Wrong - LHS not stored here
    "rhs": {"global_ID": source_var_ID},        # Wrong - missing latex
    "type": "interface",                        # Wrong - should be "generic"
    "network": interface_domain,
    "created": dateString()                      # Wrong - missing required fields
}
""")
    
    print("✅ NEW (correct) format:")
    print("""
rhs_dic = {"global_ID": source_var_ID, "latex": source_var.aliases.get("latex", source_var.label)}
incidence_list = makeIncidentList(source_var_ID)

interface_equation_record = makeCompletEquationRecord(
    rhs=rhs_dic, 
    network=interface_domain, 
    doc=f"Interface equation linking {interface_var_name} to {source_domain}.{source_var.label}",
    incidence_list=incidence_list, 
    created=dateString()
)
# Result: {"rhs": {...}, "type": "generic", "doc": "...", "network": "...", "incidence_list": [...], "created": "...", "modified": "..."}
""")

if __name__ == "__main__":
    success = test_record_format()
    show_comparison()
    
    if success:
        print("\n🎯 Interface equations now use proper record structure!")
        print("This ensures compatibility with the standard equation editor.")
    else:
        print("\n❌ Record format needs more work")
        sys.exit(1)
