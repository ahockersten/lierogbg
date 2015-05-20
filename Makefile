.PHONY: all
.DEFAULT: all

PYFILES = $(wildcard lierogbg/*/*.py)
PYCFILES = $(patsubst %.py,%.pyc,$(PYFILES))

POFILES = $(wildcard lierogbg/locale/*/LC_MESSAGES/django.po)
MOFILES = $(patsubst %.po,%.mo,$(POFILES))

TEMPLATEFILES = templates/*.html templates/*/*.html lierogbg/*/templates/*/*.html

# these are not meaningful to build, as they are only meant for including into other LESS files
LESS_IMPORTS = less/variables.less
LESS_FILES = $(filter-out $(LESS_IMPORTS),$(wildcard less/*.less))

BUILD_DIR = build

CSS_OUTPUT_DIR = $(BUILD_DIR)/css/
CSS_FILES = $(patsubst less/%.less,$(CSS_OUTPUT_DIR)/%.css,$(LESS_FILES))

all: $(CSS_FILES) django-prepare-translations django-compile-translations

$(CSS_FILES): $(LESS_FILES) $(LESS_IMPORTS)

$(CSS_OUTPUT_DIR)/%.css: less/%.less
	@mkdir -p $(CSS_OUTPUT_DIR)
	lessc $< > $@

django-compile-translations: $(MOFILES)

$(MOFILES): $(POFILES)
	python lierogbg/manage.py compilemessages

django-prepare-translations: $(POFILES)

$(POFILES): $(PYFILES) $(TEMPLATEFILES)
	python lierogbg/manage.py makemessages -i pyenv -a
	@echo Don\'t forget to run \"make django-compile-translations\" after editing the new translations

clean:
	@echo Deleting all .pyc files
	@-rm -f $(PYCFILES)
	@echo Deleting CSS files
	@-rm -rf $(CSS_OUTPUT_DIR)
	@echo Deleting compile folder
	@-rm -rf $(BUILD_DIR)
	@echo Deleting compiled locale
	@-rm -rf $(MOFILES)
