gui_automaton = {
        "create":
            {
                    "accept"            : False,
                    "add_state_variable": True,
                    "add_variable"      : True,
                    "cancel"            : True,
                    "delete_entity"     : False,
                    "delete_variable"   : False,
                    "edit_variable"     : False,
                    },
        "edit_no_selection":
            {
                    "accept"            : True,
                    "add_state_variable": True,
                    "add_variable"      : True,
                    "cancel"            : True,
                    "delete_entity"     : False,
                    "delete_variable"   : False,  # Disabled until variable selected
                    "edit_variable"     : False,
                    },
        "edit_with_selection":
            {
                    "accept"            : True,
                    "add_state_variable": True,
                    "add_variable"      : True,
                    "cancel"            : True,
                    "delete_entity"     : False,
                    "delete_variable"   : True,   # Enabled when variable selected
                    "edit_variable"     : False,
                    },
        "edit"  : {
                "accept"            : True,
                "add_state_variable": True,
                "add_variable"      : True,
                "cancel"            : True,
                "delete_entity"     : False,
                "delete_variable"   : True,
                "edit_variable"     : False,
                },
        }
