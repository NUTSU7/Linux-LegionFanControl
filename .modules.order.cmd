cmd_/home/nutsu7/LegionController/modules.order := {   echo /home/nutsu7/LegionController/LegionController.ko; :; } | awk '!x[$$0]++' - > /home/nutsu7/LegionController/modules.order
