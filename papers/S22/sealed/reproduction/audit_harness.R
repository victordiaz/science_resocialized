# Harness: runs download/RPP_swrhy.R unchanged except (1) the external source() of getOSFfile is skipped and
# getOSFfile() returns the local copy of the file, (2) library() calls for absent packages (httr, RCurl) are skipped.
local_map <- c("https://osf.io/i4syx/" = "download/OSF-Farrell-results-csv.csv")
getOSFfile <- function(url) local_map[[url]]
.lib <- base::library
library <- function(pkg, ...) { p <- as.character(substitute(pkg)); if (requireNamespace(p, quietly=TRUE)) .lib(p, character.only=TRUE) else cat("[harness] package missing, skipped:", p, "\n") }
src <- readLines("download/RPP_swrhy.R"); src <- src[!grepl("^\\s*source\\(", src)]
for (e in parse(text=src)) { v <- withVisible(eval(e, globalenv())); if (v$visible) print(v$value) }
