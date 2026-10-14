MODULE := engines/astronomica
MODULE_OBJS := astronomica.o help.o resource.o script.o conditions_test.o sprites.o metaengine.o
ifeq ($(ENABLE_ASTRONOMICA), DYNAMIC_PLUGIN)
PLUGIN := 1
endif
include $(srcdir)/rules.mk
DETECT_OBJS += $(MODULE)/detection.o
