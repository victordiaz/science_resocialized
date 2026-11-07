# Runs the audit script unchanged except: the remote helper source() line is dropped and
# getOSFfile() returns the local copy of the same OSF file; library(httr)/library(RCurl) are
# skipped because only the remote helper uses them. Run: Rscript audit_run.R (from this folder).
here <- "/Users/vladnicolescu/Developer/science-resocialized/data/findings/Row.6"
getOSFfile <- function(url) { m <- c("https://osf.io/btr65/"="download/Data/Agg_priming_ANOVA.dat"); f <- m[[url]]; if (is.null(f)) stop("no local copy for ", url); file.path(here, f) }
library <- function(pkg, ...) { p <- as.character(substitute(pkg)); if (p %in% c("httr", "RCurl")) { cat("[shim] skipped library(", p, ")\n"); return(invisible(NULL)) }; base::library(p, character.only = TRUE, ...) }
lines <- readLines(file.path(here, "download/Analysis Audit/RPP_atgp5.R"), warn = FALSE)
drop <- grepl("sachaepskamp.com", lines)
cat("[shim] dropped line(s):", which(drop), "\n")
exprs <- parse(text = lines[!drop])
for (e in exprs) { cat(">", paste(deparse(e), collapse = "\n+ "), "\n"); v <- withVisible(eval(e, envir = globalenv())); if (v$visible) print(v$value) }
