# Runs the audit script RPP_6n3bm.R unchanged except for its loading lines:
# library(httr), library(RCurl) and source(getOSFfile.R) are dropped (external, offline here),
# and getOSFfile() is defined to return the already-downloaded OSF file.
.map <- c("https://osf.io/srnvg/" = normalizePath("download/mvpr4__rawdata_preprocessed.zip"))
getOSFfile <- function(url) .map[[url]]
lines <- readLines("download/ibd4a__RPP_6n3bm.R", warn = FALSE)
drop <- grepl('^library\\("(httr|RCurl)"\\)', lines) | grepl("getOSFfile.R", lines, fixed = TRUE)
cat("dropped lines:\n"); cat(lines[drop], sep = "\n")
setwd(tempdir()); unlink("BeamerFiles", recursive = TRUE)
source(exprs = parse(text = lines[!drop]), echo = TRUE, max.deparse.length = 300)
