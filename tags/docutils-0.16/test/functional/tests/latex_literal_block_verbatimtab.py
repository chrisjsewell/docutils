# Source and destination file names.
test_source = "latex_literal_block.txt"
test_destination = "latex_literal_block_verbatimtab.tex"

# Keyword parameters passed to publish_file.
reader_name = "standalone"
parser_name = "rst"
writer_name = "latex"

# Extra setting we need
settings_overrides['literal_block_env'] = 'verbatimtab'
settings_overrides['syntax_highlight'] = 'none'
