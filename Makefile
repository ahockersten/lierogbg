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

# the CSS files belonging to bootstrap
BOOTSTRAP_CSS_FILES = bootstrap.css bootstrap.min.css bootstrap-theme.css bootstrap-theme.min.css

# the Bootstrap CSS files, local copy
BOOTSTRAP_LOCAL_CSS_FILES = $(addprefix $(CSS_OUTPUT_DIR), $(BOOTSTRAP_CSS_FILES))

# files provided by Bootstrap
BOOTSTRAP_FILES = $(addprefix bootstrap/dist/css/, $(BOOTSTRAP_CSS_FILES))

all: bootstrap django-prepare-translations django-compile-translations $(CSS_FILES) $(BOOTSTRAP_LOCAL_CSS_FILES)

$(CSS_FILES): $(LESS_FILES) $(LESS_IMPORTS)

$(BOOTSTRAP_LOCAL_CSS_FILES): $(BOOTSTRAP_FILES)
	@cp -r $^ $(CSS_OUTPUT_DIR)

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
