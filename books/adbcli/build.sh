# requires pandoc-include: pip install pandoc-include
pandoc adbcli.md --from markdown --template "../templates/eisvogel.tex" --listings --top-level-division="chapter" --filter pandoc-include -o "adbcli.pdf" 
