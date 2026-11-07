# Harness: runs download/Analysis Audit/RPP_apidb.R unchanged except (1) the external source() of getOSFfile is
# skipped and getOSFfile() returns the local copy of the file, (2) library() calls for absent packages are skipped.
# Each top-level expression is run in tryCatch so an error is printed and the run continues.
local_map <- c("https://osf.io/qghwy/" = "download/Study 2 Dataset/Exp2_Data.sav")
getOSFfile <- function(url) local_map[[url]]
.lib <- base::library
library <- function(pkg, ...) { p <- as.character(substitute(pkg)); if (requireNamespace(p, quietly=TRUE)) .lib(p, character.only=TRUE) else cat("[harness] package missing, skipped:", p, "\n") }
src <- readLines("download/Analysis Audit/RPP_apidb.R"); src <- src[!grepl("^\\s*source\\(", src)]
for (e in parse(text=src)) { cat(">", deparse(e)[1], "\n"); tryCatch({ v <- withVisible(eval(e, globalenv())); if (v$visible) print(v$value) }, error=function(err) cat("[ERROR]", conditionMessage(err), "\n")) }
