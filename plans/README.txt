This folder contains plans to be executed with pnp_naoqi

Formalism for plans:

action_params ; < cond ? X_1; X_n : (not cond) ? Y_1; Y_n > ; lastaction_params

Formalism for execution rules:

*if* condition *during* action *do* Z_1; Z_n; { skip_action | restart_action | restart_plan | fail_plan }

Generating PNPs from plan (compile and install PNPgen)

$ pnpgen_translator inline <name>.plan <name>.er


