# Runs the audit script unchanged, offline: getOSFfile() returns the local copy of the
# same OSF file (hashes checked at download), the remote source() of getOSFfile.R is
# skipped, and httr/RCurl (only used for downloading) are not loaded. Every other
# library() call is the real one, so a missing package stops the script as it would.
args <- commandArgs(trailingOnly = TRUE)
script <- args[1]; map <- args[-1]
urlmap <- setNames(sapply(strsplit(map, "="), `[`, 2), sapply(strsplit(map, "="), `[`, 1))
getOSFfile <- function(url, ...) { key <- sub("/$", "", sub("^https?://osf.io/", "", url)); f <- urlmap[[key]]; cat("[shim] getOSFfile", url, "->", f, "\n"); f }
source <- function(file, ...) { if (grepl("^http", file)) { cat("[shim] skipped remote source:", file, "\n"); invisible(NULL) } else base::source(file, ...) }
library <- function(package, ...) { p <- as.character(substitute(package)); if (p %in% c("httr", "RCurl")) { cat("[shim] skipped", p, "(download only)\n"); return(invisible()) }; if (!requireNamespace(p, quietly = TRUE)) stop(paste0("package missing: ", p)); base::library(p, character.only = TRUE) }
exprs <- parse(script)
for (e in exprs) { cat("> ", paste(deparse(e), collapse = "\n+ "), "\n", sep = ""); r <- withVisible(eval(e, envir = globalenv())); if (r$visible) print(r$value) }
