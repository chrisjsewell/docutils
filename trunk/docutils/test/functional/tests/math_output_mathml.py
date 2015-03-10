# Source and destination file names.
test_source = "data/math.txt"
test_destination = "math_output_mathml.xhtml"

# Keyword parameters passed to publish_file.
reader_name = "standalone"
parser_name = "rst"
writer_name = "xhtml"

# Settings
settings_overrides['math_output'] = 'MathML'
# local copy of default stylesheet:
settings_overrides['stylesheet_path'] = (
    'functional/input/data/html4-base.css')
