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

CSS_OUTPUT_DIR = static/css/
CSS_FILES = $(patsubst less/%.less,$(CSS_OUTPUT_DIR)/%.css,$(LESS_FILES))

FONTS_OUTPUT_DIR = static/fonts
JS_OUTPUT_DIR = static/js

# the CSS files belonging to bootstrap
BOOTSTRAP_CSS_FILES = bootstrap.css bootstrap.min.css bootstrap-theme.css bootstrap-theme.min.css

# the JS files belonging to bootstrap
BOOTSTRAP_JS_FILES = bootstrap.js bootstrap.min.js

# the fonts files belonging to bootstrap
BOOTSTRAP_FONTS_FILES = glyphicons-halflings-regular.eot glyphicons-halflings-regular.svg \
                        glyphicons-halflings-regular.ttf glyphicons-halflings-regular.woff

JQUERY_FILES = jquery.js jquery.min.js

# the Bootstrap files, local copy
BOOTSTRAP_LOCAL_CSS_FILES = $(addprefix $(CSS_OUTPUT_DIR), $(BOOTSTRAP_CSS_FILES))
BOOTSTRAP_LOCAL_FONTS_FILES = $(addprefix $(FONTS_OUTPUT_DIR), $(BOOTSTRAP_FONTS_FILES))
BOOTSTRAP_LOCAL_JS_FILES = $(addprefix $(JS_OUTPUT_DIR), $(BOOTSTRAP_JS_FILES))

JQUERY_LOCAL_FILES = $(addprefix $(JS_OUTPUT_DIR), $(JQUERY_FILES))

# files provided by Bootstrap
BOOTSTRAP_CSS_FILES_PATH = $(addprefix bootstrap/dist/css/, $(BOOTSTRAP_CSS_FILES))
BOOTSTRAP_FONTS_FILES_PATH = $(addprefix bootstrap/dist/fonts/, $(BOOTSTRAP_FONTS_FILES))
BOOTSTRAP_JS_FILES_PATH = $(addprefix bootstrap/dist/js/, $(BOOTSTRAP_JS_FILES))

JQUERY_FILES_PATH = $(addprefix jquery/, $(JQUERY_FILES))

all: bootstrap django-prepare-translations django-compile-translations $(CSS_FILES) \
	 $(BOOTSTRAP_LOCAL_CSS_FILES) $(BOOTSTRAP_LOCAL_FONTS_FILES) $(BOOTSTRAP_LOCAL_JS_FILES) \
	 $(JQUERY_LOCAL_FILES)

$(CSS_FILES): $(LESS_FILES) $(LESS_IMPORTS)

$(BOOTSTRAP_LOCAL_CSS_FILES): $(BOOTSTRAP_CSS_FILES_PATH)
	@mkdir -p $(CSS_OUTPUT_DIR)
	@cp -r $^ $(CSS_OUTPUT_DIR)

$(BOOTSTRAP_LOCAL_FONTS_FILES): $(BOOTSTRAP_FONTS_FILES_PATH)
	@mkdir -p $(FONTS_OUTPUT_DIR)
	@cp -r $^ $(FONTS_OUTPUT_DIR)

$(BOOTSTRAP_LOCAL_JS_FILES): $(BOOTSTRAP_JS_FILES_PATH)
	@mkdir -p $(JS_OUTPUT_DIR)
	@cp -r $^ $(JS_OUTPUT_DIR)

$(JQUERY_LOCAL_FILES): $(JQUERY_FILES_PATH)
	@mkdir -p $(JS_OUTPUT_DIR)
	@cp -r $^ $(JS_OUTPUT_DIR)

static/css/%.css: less/%.less
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
	@echo Deleting CSS files
	@-rm -f $(CSS_FILES) $(BOOTSTRAP_LOCAL_CSS_FILES)
	@echo Deleting fonts files
	@-rm -f $(CSS_FILES) $(BOOTSTRAP_LOCAL_FONTS_FILES)
	@echo Deleting JS files
	@-rm -f $(BOOTSTRAP_LOCAL_JS_FILES)

