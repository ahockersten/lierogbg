.PHONY: all
.DEFAULT: all

PYFILES = $(wildcard lierogbg/*/*.py)
PYCFILES = $(patsubst %.py,%.pyc,$(PYFILES))

POFILES = $(wildcard locale/*/LC_MESSAGES/django.po)
MOFILES = $(patsubst %.po,%.mo,$(POFILES))

TEMPLATEFILES = templates/*.html templates/*/*.html

# these are not meaningful to build, as they are only meant for including into other LESS files
LESS_IMPORTS = less/variables.less
LESS_FILES = $(filter-out $(LESS_IMPORTS),$(wildcard less/*.less))

BUILD_DIR = build

CSS_OUTPUT_DIR = $(BUILD_DIR)/css
CSS_FILES = $(patsubst less/%.less,$(CSS_OUTPUT_DIR)/%.css,$(LESS_FILES))

IMG_OUTPUT_DIR = $(BUILD_DIR)/img
IMG_INPUT_FILES = $(wildcard img/*.svg)
IMG_FILES = $(patsubst img/%.svg,$(IMG_OUTPUT_DIR)/%.svg,$(IMG_INPUT_FILES))

JS_OUTPUT_DIR = $(BUILD_DIR)/js
JS_INPUT_FILES = $(wildcard js/*.js)
JS_FILES = $(patsubst js/%.js,$(JS_OUTPUT_DIR)/%.js,$(JS_INPUT_FILES))

all: bootstrap django-prepare-translations django-compile-translations $(CSS_FILES) $(IMG_FILES) $(JS_FILES)

$(CSS_FILES): $(LESS_FILES) $(LESS_IMPORTS)

$(IMG_FILES): $(IMG_INPUT_FILES)

$(JS_FILES): $(JS_INPUT_FILES)

$(IMG_OUTPUT_DIR)/%.svg: img/%.svg
	@mkdir -p $(IMG_OUTPUT_DIR)
	cp $< $@

$(JS_OUTPUT_DIR)/%.js: js/%.js
	@mkdir -p $(JS_OUTPUT_DIR)
	cp $< $@

$(CSS_OUTPUT_DIR)/%.css: less/%.less
	@mkdir -p $(CSS_OUTPUT_DIR)
	lessc $< > $@

django-compile-translations: $(MOFILES)

$(MOFILES): $(POFILES)
	django-admin compilemessages

django-prepare-translations: $(POFILES)

$(POFILES): $(PYFILES) $(TEMPLATEFILES)
	django-admin makemessages -l sv
	@echo Don\'t forget to run \"make django-compile-translations\" after editing the new translations

clean:
	@echo Deleting all .pyc files
	@-rm -f $(PYCFILES)
	@echo Deleting static files
	@-rm -rf static
	@echo Deleting compiled CSS
	@-rm -rf $(CSS_OUTPUT_DIR)
	@echo Deleting compiled JS
	@-rm -rf $(JS_OUTPUT_DIR)
	@echo Deleting compile folder
	@-rm -rf $(BUILD_DIR)
	@echo Deleting compiled locale
	@-rm -rf $(MOFILES)
