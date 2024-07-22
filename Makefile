MODULE=flowgraph
PYTHON_SITE=$(shell python -c 'import sysconfig; print(sysconfig.get_path("purelib"))')

all:
	@echo "use 'make (un)install' to (un)install; you may need elevated permissions"

install: uninstall
	cp -r $(MODULE) $(PYTHON_SITE)

uninstall:
	rm -rf $(PYTHON_SITE)/$(MODULE)
