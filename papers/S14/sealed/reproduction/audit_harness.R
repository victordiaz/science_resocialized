# Harness: runs download/RPP_7rtcz.R unchanged except (1) the external source() of getOSFfile is skipped and
# getOSFfile() returns the local copy of the file, (2) library() calls for absent packages are skipped,
# (3) reshape2 is absent, so a base-R melt() shim (id.vars/measure.vars/variable.name/value.name) stands in.
local_map <- c("https://osf.io/sue7q/" = "download/replication_marsh.sav")
getOSFfile <- function(url) local_map[[url]]
.lib <- base::library
library <- function(pkg, ...) { p <- as.character(substitute(pkg)); if (requireNamespace(p, quietly=TRUE)) .lib(p, character.only=TRUE) else cat("[harness] package missing, skipped:", p, "\n") }
if (!requireNamespace("reshape2", quietly=TRUE)) melt <- function(data, id.vars, measure.vars, variable.name, value.name) {
  out <- do.call(rbind, lapply(measure.vars, function(m) { x <- data[, id.vars, drop=FALSE]; x[[variable.name]] <- m; x[[value.name]] <- data[[m]]; x }))
  out[[variable.name]] <- factor(out[[variable.name]], levels=measure.vars); out }
src <- readLines("download/RPP_7rtcz.R"); src <- src[!grepl("^\\s*source\\(", src)]
exprs <- parse(text=src)
for (e in exprs) { v <- withVisible(eval(e, globalenv())); if (v$visible) print(v$value) }
