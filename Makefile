PREFIX ?= /usr/local
USER_PREFIX ?= $(HOME)/.local
PYTHON ?= python3

.PHONY: all build install user-install uninstall test clean

all: build

build:
	@echo "Build complete (pure Python package)."

install:
	install -d $(DESTDIR)$(PREFIX)/bin
	install -d $(DESTDIR)$(PREFIX)/lib/reversal-autotheme
	install -d $(DESTDIR)$(PREFIX)/share/applications
	install -d $(DESTDIR)$(PREFIX)/share/icons/hicolor/scalable/apps
	install -d $(DESTDIR)$(PREFIX)/share/icons/hicolor/512x512/apps
	cp -r src/reversal_autotheme $(DESTDIR)$(PREFIX)/lib/reversal-autotheme/
	printf '#!/usr/bin/env bash\nexport PYTHONPATH="%s/lib/reversal-autotheme:$$PYTHONPATH"\nexec python3 -m reversal_autotheme.cli "$$@"\n' "$(PREFIX)" > $(DESTDIR)$(PREFIX)/bin/reversal-autotheme
	chmod +x $(DESTDIR)$(PREFIX)/bin/reversal-autotheme
	install -m 644 data/reversal-autotheme.desktop $(DESTDIR)$(PREFIX)/share/applications/
	install -m 644 data/icons/reversal-autotheme.svg $(DESTDIR)$(PREFIX)/share/icons/hicolor/scalable/apps/
	install -m 644 data/icons/512x512/reversal-autotheme.png $(DESTDIR)$(PREFIX)/share/icons/hicolor/512x512/apps/
	update-desktop-database $(DESTDIR)$(PREFIX)/share/applications 2>/dev/null || true
	gtk-update-icon-cache -f -t $(DESTDIR)$(PREFIX)/share/icons/hicolor 2>/dev/null || true

user-install:
	install -d $(USER_PREFIX)/bin
	install -d $(USER_PREFIX)/lib/reversal-autotheme
	install -d $(USER_PREFIX)/share/applications
	install -d $(USER_PREFIX)/share/icons/hicolor/scalable/apps
	install -d $(USER_PREFIX)/share/icons/hicolor/512x512/apps
	cp -r src/reversal_autotheme $(USER_PREFIX)/lib/reversal-autotheme/
	printf '#!/usr/bin/env bash\nexport PYTHONPATH="%s/lib/reversal-autotheme:$$PYTHONPATH"\nexec python3 -m reversal_autotheme.cli "$$@"\n' "$(USER_PREFIX)" > $(USER_PREFIX)/bin/reversal-autotheme
	chmod +x $(USER_PREFIX)/bin/reversal-autotheme
	install -m 644 data/reversal-autotheme.desktop $(USER_PREFIX)/share/applications/
	install -m 644 data/icons/reversal-autotheme.svg $(USER_PREFIX)/share/icons/hicolor/scalable/apps/
	install -m 644 data/icons/512x512/reversal-autotheme.png $(USER_PREFIX)/share/icons/hicolor/512x512/apps/
	update-desktop-database $(USER_PREFIX)/share/applications 2>/dev/null || true
	gtk-update-icon-cache -f -t $(USER_PREFIX)/share/icons/hicolor 2>/dev/null || true

uninstall:
	rm -f $(PREFIX)/bin/reversal-autotheme
	rm -rf $(PREFIX)/lib/reversal-autotheme
	rm -f $(PREFIX)/share/applications/reversal-autotheme.desktop
	rm -f $(PREFIX)/share/icons/hicolor/scalable/apps/reversal-autotheme.svg
	rm -f $(PREFIX)/share/icons/hicolor/512x512/apps/reversal-autotheme.png
	update-desktop-database $(PREFIX)/share/applications 2>/dev/null || true

test:
	PYTHONPATH=src $(PYTHON) -m unittest discover tests

clean:
	rm -rf build dist *.egg-info src/*.egg-info
