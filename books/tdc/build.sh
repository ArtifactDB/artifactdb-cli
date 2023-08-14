# requires pandoc-include: pip install pandoc-include
pandoc tdc.md --from markdown --template "../templates/eisvogel.tex" --listings --top-level-division="chapter" --filter pandoc-include -o "tdc.pdf" 
